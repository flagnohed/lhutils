from bs4 import BeautifulSoup
from enum import Enum
from termcolor import colored
from unicodedata import normalize


CLR_APP: str = "white"
CLR_INFO: str = "green"
CLR_ERROR: str = "red"


class Msg_t(Enum):
    APP = 0		# The actual output of the program
    INFO = 1	# Status update/other information
    ERROR = 2	# Something went wrong


def yell(msg: str, lvl: Msg_t = Msg_t.INFO):
    """ Yell to the terminal in color depending on mood. """
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


def printable_num(num: int) -> str:
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


def numstr(s: str) -> str:
    """ Extract numbers from a string and return those as a new string. """
    return ''.join([c for c in s if c.isdigit()])


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