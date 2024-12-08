# ------------------------------------------------------------------------------
# TODO:
# * fix bug with new players around 900k not showing with filter
# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from arena import print_test_case
from bs4 import BeautifulSoup
from colorama import init
from player import Player, print_value_predictions
from re import match
from sys import argv
from roster import parse_roster
from transfer import parse_transfers
from utils import (
    get_current_date,
    Msg_t,
    yell
)

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

FILE_ROSTER: str = "html/roster.html"
FILE_TRANSFER: str = "html/transfers.html"

ARGC_MIN: int = 2
ARGC_MAX: int = 4
MAX_DAYS: int = 7
MAX_WEEKS: int = 13
FILTER_DEFAULT_MIN: int = 17
FILTER_DEFAULT_MAX: int = 22

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
# Global variables
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------


    


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def filter_players(players: list[Player], age_min: int, age_max: int, week: int, 
                   day: int) -> list[Player]:
    """ Filters out bad players, based on values in PVT_DICT.
        Returns a list of players that passed the filter. """
    fplayers: list[Player] = []
    for player in players:
        trainings_left = player.get_trainings_left(week, day)
        if player.age in PVT_DICT.keys() and age_min <= player.age <= age_max:
            # Get threshold and weekly increase for the relevant age.
            t, w = PVT_DICT[player.age]
            if player.value + trainings_left * w >= t:
                fplayers += [player]
        
        elif player.age == 17 and trainings_left >= MAX_WEEKS - 1 and \
            player.value >= 900000:
            fplayers += [player]

    return fplayers
            
# ------------------------------------------------------------------------------
    


# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------

""" Determines if argument PARAM is a valid flag. """
def is_flag(param: str) -> bool:
    return param in ["-h", "--help", "-r", "--roster", "-t", 
                     "--transfer", "-f", "--filter"]

# ------------------------------------------------------------------------------
# Parser functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------


    
# ------------------------------------------------------------------------------	



# ------------------------------------------------------------------------------

def parse(filename: str, short_flag: str) -> list[Player]:
    """ Creates the necessary objects for parsing and 
        calls the correct parser function. """
    players: list[Player] = []

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
        else:
            yell("This should not happen.", Msg_t.ERROR)
    
    return players, week, day

# ------------------------------------------------------------------------------
# Print functions
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------

def print_usage() -> None:
    """ Prints usage information. Called if -h/--help flag present 
        or usage error detected. """
    
    print(f"\nUsage: python3 main.py [options]\n")
    print("-h, --help")
    print("    Prints this information and quits.")
    print("-r, --roster")
    print("    Parse a team roster. Paste HTML into html/roster.html.")
    print("-t, --transfer")
    print("    Parse transfer list. Paste HTML into html/transfers.html.")
    print("-f, --filter LOW,MAX")
    print("    Only show players with age between (including) LOW and MAX years.")
    print("    If no age interval is provided, default values are used.")
    print(f"    Current default values: MIN = {FILTER_DEFAULT_MIN}, MAX = {FILTER_DEFAULT_MAX}")
    print("-a, --arena CAPACITY NEW_CAPACITY")
    print("    Calculate how much it would cost to change capacity (build/demolish).")
    print("    Also prints how many weeks it would take before arena being profitable,")
    print("    as well as how much difference it will be in terms of rent.")
    exit()

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------

def main():
    argc: int = len(argv)
    if argc < ARGC_MIN or argc > ARGC_MAX:
        print_usage()	

    filter: bool = False
    age_min: int = FILTER_DEFAULT_MIN
    age_max: int = FILTER_DEFAULT_MAX
    args: list[str] = argv[1:]
    players = list[Player]
    init()  # <--- colors in terminal
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
            if i + 1 < len(args) and match("\d\d,[0-9]+", args[i + 1]):
                i = i + 1
                age_min, age_max = [int(x) for x in args[i].split(',')]
        elif args[i] in ("-a", "--arena"):
            if i + 2 < len(args) and args[i + 1].isnumeric() \
                and args[i + 2].isnumeric():
                print_test_case(int(args[i + 1]), int(args[i + 2]))
            else:
                print_usage()
            
            exit()

        else:
            print_usage()
    
    players = filter_players(players, age_min, age_max, week, day) \
        if filter else players
    print_value_predictions(players, week, day)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
