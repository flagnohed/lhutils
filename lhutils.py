# ------------------------------------------------------------------------------
# TODO:
# * fix bug with new players around 900k not showing with filter
# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from arena import print_test_case
from bs4 import BeautifulSoup, ResultSet, PageElement
from colorama import init
from enum import Enum
from io import TextIOWrapper
from re import match
from sys import argv
from termcolor import colored
from unicodedata import normalize

# 
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

CLR_APP: str = "white"
CLR_INFO: str = "green"
CLR_ERROR: str = "red"


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

ID2POS_DICT: dict[str, str] = {"ucTeamSquadGoalkeepers" : "GK",
                               "ucTeamSquadDefenders" : "DEF",
                               "ucTeamSquadForwards" : "FWD"}

# ------------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------------

week: int = 0
day: int = 0

# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.age: int = 0
        self.bday: int = 0			  # [1, 7]
        self.bweek: int = 0			  # [1, 13]
        self.value: int = 0
        self.idx: int = 0   		  # 1-based index for transfers.
        self.name: str = ""
        self.pos: str = ""
        self.bid: str = ""			  # Starting bid in parenthesis if no bids. 	 

    def get_trainings_left(self) -> int:
        """ Gets the number of training occasions remaining 
            before birthday. """
        wdiff: int = (self.bweek - week) % 13
        if wdiff < 0:
            wdiff += 13
        
        dose_reset: bool = day == 7	
        last_training: bool = self.bday == 7		
        return wdiff + int(last_training) - int(dose_reset)
    
class Msg_t(Enum):
    APP = 0		# The actual output of the program
    INFO = 1	# Status update/other information
    ERROR = 2	# Something went wrong

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

""" Yell to the terminal in color depending on mood. """
def yell(msg: str, lvl: Msg_t):
    if lvl == Msg_t.APP:
        color = CLR_APP
    elif lvl == Msg_t.INFO:
        color = CLR_INFO
    elif lvl == Msg_t.ERROR:
        color = CLR_ERROR
    else:
        yell("Unknown message type!", Msg_t.ERROR)

    print(colored(msg, color))
    if lvl == Msg_t.ERROR:
        exit()
        

def filter_players(players: list[Player], 
                   age_min: int, age_max: int) -> list[Player]:
    """ Filters out bad players, based on values in PVT_DICT.
        Returns a list of players that passed the filter. """
    fplayers: list[Player] = []
    for player in players:
        trainings_left = player.get_trainings_left()
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

def get_current_date(soup: BeautifulSoup) -> list:
    #  Find the current date (in game) in the HTML file
    current_date_str = soup.find(id="topmenurightdateinner").get_text()
    clean_str = normalize("NFKD", current_date_str)
    return [int(a) for a in clean_str.split(' ') if a.isnumeric()]

# ------------------------------------------------------------------------------
    
def num2str(num: int) -> str:
    """ Takes an integer, converts it to a string.
        Makes it easier to read large numbers like 5000000 --> 5 000 000. """
    rev_str: str = str(num)[::-1]   
    count: int = 0
    pretty_str: str = ""

    for d in rev_str:
        count += 1
        pretty_str += d
        if count == 3:
            count = 0
            pretty_str += " "
    
    return pretty_str[::-1]

# ------------------------------------------------------------------------------

def is_player_anchor(anchor: PageElement):
    return anchor["href"].startswith("/Pages/Player/Player.aspx?Player_Id=")

# ------------------------------------------------------------------------------

def numstr(s: str) -> str:
    """ Extract numbers from a string and return those as a new string. """
    return ''.join([c for c in s if c.isdigit()])

# ------------------------------------------------------------------------------

""" Determines if argument PARAM is a valid flag. """
def is_flag(param: str) -> bool:
    return param in ["-h", "--help", "-r", "--roster", "-t", 
                     "--transfer", "-f", "--filter"]

# ------------------------------------------------------------------------------
# Parser functions
# ------------------------------------------------------------------------------

def parse_roster(soup: BeautifulSoup) -> list[Player]:
    values: ResultSet[PageElement] = soup.find_all("td", 
                                                {"class": "right value"})
    players: list[Player] = []
    title: str = ""
    for anchor in soup.find_all('a'):

        if not is_player_anchor(anchor):
            continue

        try:
            title = anchor["title"]
        except KeyError:
            continue

        player: Player = Player()
        title_list: list[str] = title.split('\n')
        birthdate = numstr(title_list[4])

        player.name = anchor.get_text()
        player.pos = ID2POS_DICT[anchor["id"].split("_")[3]]
        player.age = int(numstr(title_list[0]))
        player.bday = int(birthdate[-1])
        player.bweek = int(birthdate[:-1])
        player.value = int(numstr(values[len(players)].string))

        players += [player]

    return players

# ------------------------------------------------------------------------------

""" Strips S of trailing and leading whitespace. """
def wstext2int(s: str) -> str:
    i1: int = 0
    i2: int = 0
    begun: bool = False
    for i in range(len(s)):
        if not begun and (s[i] == '(' or s[i].isdigit()):
            # Indicate that we are looking for the end of the expression
            # (i.e. closed parenthesis or digit)
            begun = True
            i1 = i

        elif begun and (s[i] in ['\n', '\t'] or \
            i + 1 < len(s) and s[i] == s[i + 1] == ' '):
            i2 = i
            break

    return s[i1:i2]	
    
# ------------------------------------------------------------------------------	

def parse_transfers(soup: BeautifulSoup) -> list[Player]:
    
    # Should probably parse div.get_text() instead of the title.
    # That way we would also get the pos. 

    players: list[Player] = []
    div: PageElement = None

    information: ResultSet = soup.find_all("div", {"class":"ts_collapsed_1"})
    values: ResultSet = soup.find_all("div", {"class":"ts_collapsed_3"})
    bids: ResultSet = soup.find_all("div", {"class":"ts_collapsed_5"})

    for i, div in enumerate(information):
        player: Player = Player()
        info: list[str] = [s for s in div.stripped_strings]

        # info has kind of a weird structure:
        # [idx, player_name, ',', 'x år', '(W-D), pos, shoots]

        player.name = info[1]
        player.age = int(numstr(info[3])) 
        bdate_str: str = numstr(info[4])
        player.bday = int(bdate_str[-1])    # last digit is bday,
        player.bweek = int(bdate_str[:-1])  # and the rest is bweek.

        player.pos = info[4].split(", ")[1]
        player.value = int(numstr(values[i].get_text()))
        player.bid = wstext2int(bids[i].get_text())

        player.idx = i + 1
        players += [player]

    return players

# ------------------------------------------------------------------------------

def parse(filename: str, short_flag: str) -> list[Player]:
    """ Creates the necessary objects for parsing and 
        calls the correct parser function. """
    players: list[Player] = []
    global week
    global day

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
    
    return players

# ------------------------------------------------------------------------------
# Print functions
# ------------------------------------------------------------------------------

def print_value_predictions(players: list[Player]) -> None:
    """ Predicts the value of a player at the end of 
        the given age (after last training). """ 
    
    if not players:
        yell("No players found.", Msg_t.ERROR)

    init()
    headline: str = ""
    DIVIDER_LENGTH: int = 20
    for p in players:
        rem_trainings: int = p.get_trainings_left()
        yell(DIVIDER_LENGTH * "-", Msg_t.INFO)

        if p.idx:
            # This means we have parsed the transfer list
            headline = f"{p.idx}. {p.name}, {p.age}, {p.bid}, {p.pos}"
        else:
            # At the moment this can only be roster
            headline = f"{p.name}, {p.age}, {p.pos}"

        yell(headline, Msg_t.APP)
        yell(f"Värde:	{num2str(p.value)} kr", Msg_t.APP)
        if p.age == 17:
            # Players over the age of 17 rarely develop at 300k/w
            yell(f"300k/w: {num2str(p.value + rem_trainings * 300000)} kr",
                 Msg_t.APP)

        yell(f"400k/w: {num2str(p.value + rem_trainings * 400000)} kr",
             Msg_t.APP)
        yell(f"500k/w: {num2str(p.value + rem_trainings * 500000)} kr",
             Msg_t.APP)

        if p.age > 17:
            yell(f"600k/w: {num2str(p.value + rem_trainings * 600000)} kr",
                 Msg_t.APP)

    yell(DIVIDER_LENGTH * "-", Msg_t.INFO)
    # Display some info that might be interesting.
    # Number of good players (+ percentage) (if filter was enabled)
    # Count players per position

# ------------------------------------------------------------------------------

def print_usage() -> None:
    """ Prints usage information. Called if -h/--help flag present 
        or usage error detected. """
    
    print()
    print("Usage: python3 lhutils.py [options]")
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

    # Parse arguments
    for i in range(len(args)):
        if args[i] in ("-h", "--help"):
            print_usage()
        elif args[i] in ("-r", "--roster"):
            players = parse(FILE_ROSTER, "-r")
        elif args[i] in ("-t", "--transfer"):
            players = parse(FILE_TRANSFER, "-t")
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
    
    players = filter_players(players, age_min, age_max) if filter else players
    print_value_predictions(players)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
