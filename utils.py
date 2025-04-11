"""Commonly used functions across entire applications are placed here."""

import sys
from enum import Enum
from termcolor import colored


CLR_APP: str = "white"
CLR_INFO: str = "green"
CLR_ERROR: str = "red"


class MsgType(Enum):
    """Type of application message. Determines color in terminal."""

    APP = 0  # The actual output of the program
    INFO = 1  # Status update/other information
    ERROR = 2  # Something went wrong


def yell(msg: str, lvl: MsgType = MsgType.INFO):
    """Yell to the terminal in color depending on mood."""
    if lvl == MsgType.APP:
        color = CLR_APP
    elif lvl == MsgType.INFO:
        color = CLR_INFO
    elif lvl == MsgType.ERROR:
        color = CLR_ERROR
    else:
        yell("Unknown message type!", MsgType.ERROR)
        sys.exit()

    print(colored(msg, color))
    if lvl == MsgType.ERROR:
        sys.exit()


def printable_num(num: int) -> str:
    """Takes an integer, converts it to a string.
    Makes it easier to read large numbers like 5000000 --> 5 000 000."""
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
    """Extract numbers from a string and return those as a new string."""
    return "".join([c for c in s if c.isdigit()])


def wstext2int(s: str) -> str:
    """Strips S of trailing and leading whitespace."""
    i1: int = 0
    i2: int = 0
    begun: bool = False
    for i, c in enumerate(len(s)):
        if not begun and (c == "(" or c.isdigit()):
            # Indicate that we are looking for the end of the expression
            # (i.e. closed parenthesis or digit)
            begun = True
            i1 = i

        elif begun and (c in ["\n", "\t"] or i + 1 < len(s) and c == s[i + 1] == " "):
            i2 = i
            break

    return s[i1:i2]
