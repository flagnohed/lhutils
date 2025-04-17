#!/usr/bin/env python3

"""Main module."""
import sys
from unicodedata import normalize
from re import match
from time import time

import colorama

from bs4 import BeautifulSoup
from arena import print_test_case
from roster import parse_roster
from player import (
    Player,
    print_value_predictions,
    get_trainings_left,
    MAX_WEEKS,
)
from tactics import compare_tactics, TACTICS
from transfer import (
    parse_transfers,
    parse_transfer_history,
    show_history,
)
from utils import (
    numstr,
    MsgType,
    yell,
    printable_num,
)

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

FILE_GAME: str = "html/game.html"
FILE_ROSTER: str = "html/roster.html"
FILE_TRANSFER: str = "html/transfers.html"
FILE_TRANSFER_HISTORY: str = "html/transfer_history.html"

ARGC_MIN: int = 2
ARGC_MAX: int = 4
FILTER_DEFAULT_MIN: int = 17
FILTER_DEFAULT_MAX: int = 22
DEFAULT_BUDGET: int = 20000000

# Predicted Value Thresholds
# |-----|------|-----------------|
# | Age | PVT  | Weekly increase |
# | 17  | 5m   | 300k            |
# | 18  | 11m  | 400k            |
# | 19  | 16m  | 500k            |
# | 20  | 20m  | 600k            |
# | 21  | 30m  | 700k            |
# | 22  | 40m  | 700k            |
# |-----|------|-----------------|
PVT_DICT: dict[int, tuple[int, int]] = {
    17: (5000000, 300000),
    18: (11000000, 400000),
    19: (17000000, 500000),
    20: (23000000, 600000),
    21: (35000000, 700000),
    22: (50000000, 700000),
}


def filter_players(
    players: list[Player],
    age_min: int,
    age_max: int,
    date: tuple[int],
    budget: int,
) -> list[Player]:
    """Filters out bad players, based on values in PVT_DICT.
    Returns a list of players that passed the filter.
    budget == 0 --> no limit"""
    week, day = date
    fplayers: list[Player] = []
    for player in players:
        trainings_left = get_trainings_left(player, week, day)
        if player.age in PVT_DICT and age_min <= player.age <= age_max:
            # Get threshold and weekly increase for the relevant age.
            t, w = PVT_DICT[player.age]

            # Add to FPLAYERS if  player probably will reach threshold value OR
            # player just turned 17 OR
            # player value already has a close-to-threshold value

            # If it's a transfer listed player, and user entered a budget,
            # skip if user can't afford.
            if player.bid and budget and int(numstr(player.bid)) > budget:
                continue

            if player.value + trainings_left * w >= t:
                player.note = f"[Can surpass {printable_num(t)} kr]"
                fplayers += [player]

            elif (
                player.age == 17
                and trainings_left >= MAX_WEEKS - 1
                and player.value >= 900000
            ):
                player.note = "[Freshly drawn]"
                fplayers += [player]

            elif player.age == 17 and player.value >= 4000000:
                player.note = "[Hidden gem?]"
                fplayers += [player]

    return fplayers


def get_current_date(soup: BeautifulSoup) -> list:
    """Find the current date (in game) in the HTML file."""
    current_date_str = soup.find(id="topmenurightdateinner").get_text()
    clean_str = normalize("NFKD", current_date_str)
    return [int(a) for a in clean_str.split(" ") if a.isnumeric()]


def is_flag(param: str) -> bool:
    """Determines if argument PARAM is a valid flag."""
    return param in [
        "-h",
        "--help",
        "-r",
        "--roster",
        "-t",
        "--transfer",
        "-f",
        "--filter",
    ]


def parse(filename: str, short_flag: str) -> tuple[list[Player], int, int]:
    """Creates the necessary objects for parsing and
    calls the correct parser function."""
    players: list = []
    with open(filename, errors="ignore", mode="r", encoding="utf-8") as file:

        if not bool(file.read(1)):
            yell(f"{filename} is empty.", MsgType.ERROR)

        soup: BeautifulSoup = BeautifulSoup(
            file, "html.parser", from_encoding="utf-8"
        )
        # Parse current in-game date.
        week, day = get_current_date(soup)
        # We can trust that short_flag is a valid flag here.
        if short_flag == "-r":
            players = parse_roster(soup)
        elif short_flag == "-t":
            players = parse_transfers(soup)
        elif short_flag == "-th":
            players = parse_transfer_history(soup)
        # elif short_flag == "-g":
        #     parse_game(soup)
        else:
            yell("This should not happen.", MsgType.ERROR)

    return players, week, day


def print_usage() -> None:
    """Prints usage information. Called if -h/--help flag present
    or usage error detected."""
    print("Usage: python3 main.py [options]")
    print("Options:\n")
    print("-h, --help")
    print("    Prints this information and quits.")
    print("-a, --arena CAPACITY NEW_CAPACITY")
    print(
        "    Calculate how much it costs to change capacity (build/demolish)."
    )
    print("    Also prints how many weeks until profit,")
    print("    as well as how much difference it will be in terms of rent.")
    print("-f, --filter LOW,MAX")
    print("    Only show players with age between LOW and MAX years.")
    print("    If no age interval is provided, default values are used.")
    print("    Current default values: ")
    print(f"    MIN = {FILTER_DEFAULT_MIN}, MAX = {FILTER_DEFAULT_MAX}")
    print("    Filter should never be standalone. It should always come with")
    print("    either transfer or roster.")
    print("-r, --roster")
    print("    Parse a team roster. Paste HTML into html/roster.html.")
    print("-th, --transfer-history")
    print("    Show some extended stats from your transfer history.")
    print("    Paste HTML into html/transfer_history.html.")
    print("-tx, --tactics TACTIC")
    print("    Compare TACTIC to other tactics to see how often certain")
    print("    lines play against certain oppositional lines. TACTIC can")
    print("    be left blank to compare all tactics against eachother.")
    print("-t, --transfer")
    print("    Parse transfer list. Paste HTML into html/transfers.html.")
    sys.exit()


def main():
    """Main function.
    TODO: reduce complexity of this function."""
    start: float = time()
    argc: int = len(sys.argv)
    if argc < ARGC_MIN or argc > ARGC_MAX:
        print_usage()
    week: int = 0
    day: int = 0
    budget: int = 0
    filter_active: bool = False
    age_min: int = FILTER_DEFAULT_MIN
    age_max: int = FILTER_DEFAULT_MAX
    args: list[str] = sys.argv[1:]
    players: list = []  # can contain Players or HistEntries
    colorama.init()  # <--- colors in terminal
    # Parse arguments
    for i, arg in enumerate(args):
        if arg in ("-h", "--help"):
            print_usage()

        elif arg in ("-r", "--roster"):
            players, week, day = parse(FILE_ROSTER, "-r")

        elif arg in ("-t", "--transfer"):
            players, week, day = parse(FILE_TRANSFER, "-t")

        elif arg in ("-f", "--filter"):
            filter_active = True
            # Filter flag can be succeeded by age range (comma separated)
            # If not we just use the default values. This also applies
            # when the age range looks weird.
            if i + 1 < len(args) and match(r"\d\d,[0-9]+", args[i + 1]):
                i = i + 1
                age_min, age_max = [int(x) for x in arg.split(",")]

        elif arg in ("-th", "--transfer-history"):
            if filter_active:
                yell(
                    "Filter not yet compatible with transfer history.",
                    MsgType.ERROR,
                )
            players, _, _ = parse(FILE_TRANSFER_HISTORY, "-th")
            show_history(players)
            sys.exit()

        elif arg in ("-a", "--arena"):
            if (
                i + 2 < len(args)
                and args[i + 1].isnumeric()
                and args[i + 2].isnumeric()
            ):
                print_test_case(int(args[i + 1]), int(args[i + 2]))
                sys.exit()
            else:
                print_usage()

        elif arg in ("-g", "--game"):
            # Under construction
            parse(FILE_GAME, "-g")

        elif arg in ("-b", "--budget"):
            if i + 1 < len(args) and args[i + 1].isnumeric():
                budget = int(args[i + 1])
            else:
                budget = DEFAULT_BUDGET
                yell("Note: invalid budget.", MsgType.INFO)
                yell(
                    f"Using DEFAULT_BUDGET = {printable_num(budget)} kr",
                    MsgType.INFO,
                )

        elif arg in ("-tx", "--tactics"):
            t1 = ""
            if i + 1 < len(args) and args[i + 1] in TACTICS:
                t1 = args[i + 1]
            compare_tactics(t1)

        else:
            print_usage()

    num_total_players: int = len(players)

    if filter_active:
        players = filter_players(
            players, age_min, age_max, (week, day), budget
        )

    print_value_predictions(players, week, day)
    end: float = time()

    yell(f"Total players parsed: {num_total_players}")
    if filter_active:
        yell(f"Players after filtering: {len(players)}")
    yell(f"Time elapsed: {end - start}s")


if __name__ == "__main__":
    main()
