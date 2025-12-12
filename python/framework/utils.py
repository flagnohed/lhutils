"""Commonly used functions across entire applications are placed here."""

import sys
from termcolor import colored


CLR_WHITE: str = "white"
CLR_GREEN: str = "green"
CLR_RED: str = "red"


def msg(s: str, color: str = CLR_WHITE):
    """msg to the terminal in color depending on mood."""
    print(colored(s, color))
    if color == CLR_RED:
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
    i1: int = -1
    i2: int = -1
    for i, c in enumerate(s):
        if i1 == -1 and (c == "(" or c.isdigit()):
            # Indicate that we are looking for the end of the expression
            # (i.e. closed parenthesis or digit)
            i1 = i

        elif i1 != -1 and (
            c in ["\n", "\t"] or i + 1 < len(s) and c == s[i + 1] == " "
        ):
            i2 = i
            break

    return s[i1:i2]
