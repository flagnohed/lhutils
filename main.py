#!/usr/bin/env python3

from bs4 import BeautifulSoup
import colorama
from re import match
from sys import argv
from time import time

from arena import print_test_case
# from game import parse_game
from roster import parse_roster
from player import (
    Player,
    print_value_predictions,
    get_trainings_left,
    MAX_WEEKS,
    MAX_DAYS,
)
from transfer import (
    parse_transfers,
    parse_transfer_history,
    show_history,
)
from utils import (
    numstr,
    get_current_date,
    Msg_t,
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
MAX_DAYS: int = 7
MAX_WEEKS: int = 13
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
PVT_DICT: dict[int, tuple[int, int]] = {17: (5200000, 300000),
                                        18: (11000000, 400000),
                                        19: (16000000, 500000),
                                        20: (20000000, 600000),
                                        21: (30000000, 700000),
                                        22: (40000000, 700000)}

# ------------------------------------------------------------------------------

def filter_players(players: list[Player], age_min: int, age_max: int,
                   week: int, day: int, budget: int) -> list[Player]:
    """ Filters out bad players, based on values in PVT_DICT.
    Returns a list of players that passed the filter. 
    budget == 0 --> no limit """
    fplayers: list[Player] = []
    for player in players:
        trainings_left = get_trainings_left(player, week, day)
        if player.age in PVT_DICT.keys() and age_min <= player.age <= age_max:
            # Get threshold and weekly increase for the relevant age.
            t, w = PVT_DICT[player.age]

            """
            Add to FPLAYERS if  player probably will reach threshold value OR
            player just turned 17 OR
            player value already has a close-to-threshold value
            """
            # If it's a transfer listed player, and user entered a budget,
            # skip if user can't afford.
            if player.bid and budget and int(numstr(player.bid)) > budget:
                continue

            if player.value + trainings_left * w >= t:
                player.note = f"[Can surpass {t} kr]"
                fplayers += [player]

            elif player.age == 17 and trainings_left >= MAX_WEEKS - 1 and \
                    player.value >= 900000:
                player.note = f"[Freshly drawn]"
                fplayers += [player]

            elif player.age == 17 and player.value >= 4000000:
                player.note = "[Hidden gem?]"
                fplayers += [player]

    return fplayers

# ------------------------------------------------------------------------------

def is_flag(param: str) -> bool:
    """ Determines if argument PARAM is a valid flag. """
    return param in ["-h", "--help", "-r", "--roster", "-t",
                     "--transfer", "-f", "--filter"]

# ------------------------------------------------------------------------------

def parse(filename: str, short_flag: str) -> tuple[list[Player], int, int]:
    """ Creates the necessary objects for parsing and
        calls the correct parser function. """
    players: list = []
    with open(filename, errors="ignore", mode='r') as file:

        if not bool(file.read(1)):
            yell(f"{filename} is empty.", Msg_t.ERROR)

        soup: BeautifulSoup = BeautifulSoup(file, "html.parser",
                                            from_encoding="utf-8")
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
            yell("This should not happen.", Msg_t.ERROR)

    return players, week, day

# ------------------------------------------------------------------------------

def print_usage() -> None:
    """ Prints usage information. Called if -h/--help flag present
        or usage error detected. """

    print("\nUsage: python3 main.py [options]\n")
    print("-h, --help")
    print("\tPrints this information and quits.")
    print("-r, --roster")
    print("\tParse a team roster. Paste HTML into html/roster.html.")
    print("-t, --transfer")
    print("\tParse transfer list. Paste HTML into html/transfers.html.")
    print("-f, --filter LOW,MAX")
    print("\tOnly show players with age between LOW and MAX years.")
    print("\tIf no age interval is provided, default values are used.")
    print("\tCurrent default values: ")
    print(f"\tMIN = {FILTER_DEFAULT_MIN}, MAX = {FILTER_DEFAULT_MAX}")
    print("-a, --arena CAPACITY NEW_CAPACITY")
    print("\tCalculate how much it costs to change capacity (build/demolish).")
    print("\tAlso prints how many weeks until profit,")
    print("\tas well as how much difference it will be in terms of rent.")
    exit()

# ------------------------------------------------------------------------------

def main():
    start: float = time()
    argc: int = len(argv)
    if argc < ARGC_MIN or argc > ARGC_MAX:
        print_usage()

    budget: int = 0
    filter: bool = False
    age_min: int = FILTER_DEFAULT_MIN
    age_max: int = FILTER_DEFAULT_MAX
    args: list[str] = argv[1:]
    players: list = []  # can contain Players or HistEntries
    colorama.init()              # <--- colors in terminal
    # Parse arguments
    for i in range(len(args)):
        if args[i] in ("-h", "--help"):
            print_usage()
        elif args[i] in ("-r", "--roster"):
            players, week, day = parse(FILE_ROSTER, "-r")
        elif args[i] in ("-t", "--transfer"):
            players, week, day = parse(FILE_TRANSFER, "-t")

        elif args[i] in ("-f", "--filter"):
            filter = True
            # Filter flag can be succeeded by age range (comma separated)
            # If not we just use the default values. This also applies
            # when the age range looks weird.
            if i + 1 < len(args) and match(r"\d\d,[0-9]+", args[i + 1]):
                i = i + 1
                age_min, age_max = [int(x) for x in args[i].split(',')]
        elif args[i] in ("-th", "--transfer-history"):
            if filter:
                yell("Filter not yet compatible with transfer history.",
                     Msg_t.ERROR)
            players, _, _ = parse(FILE_TRANSFER_HISTORY, "-th")
            show_history(players)
            exit()

        elif args[i] in ("-a", "--arena"):
            if i + 2 < len(args) and args[i + 1].isnumeric() \
                    and args[i + 2].isnumeric():
                print_test_case(int(args[i + 1]), int(args[i + 2]))
                exit()
            else:
                print_usage()
        
        elif args[i] in ("-g", "--game"):
            parse(FILE_GAME, "-g")

        elif args[i] in ("-b", "--budget"):
            if i + 1 < len(args) and args[i + 1].isnumeric():
                budget = int(args[i + 1])
            else:
                budget = DEFAULT_BUDGET
                yell("Note: invalid budget.", Msg_t.INFO)
                yell(f"Resorting to DEFAULT_BUDGET = {printable_num(budget)} kr", 
                     Msg_t.INFO)

        else:
            print_usage()

    num_total_players: int = len(players)

    if filter:
        players = filter_players(players, age_min, age_max, week, day, budget)

    print_value_predictions(players, week, day)
    end: float = time()

    yell(f"Total players parsed: {num_total_players}")
    if filter:
        yell(f"Players after filtering: {len(players)}")
    yell(f"Time elapsed: {end - start}s")

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------