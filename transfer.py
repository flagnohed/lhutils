# ------------------------------------------------------------------------------

from bs4 import BeautifulSoup, PageElement, ResultSet
from dataclasses import dataclass
from datetime import date
from enum import Enum
from player import Player
from utils import (
    numstr,
    wstext2int,
    yell
)

class Transfer_t(Enum):
    ERR = 0
    BUY = 1
    SELL = 2


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

def get_transfer_type(ttstr: str) -> Transfer_t:
    if ttstr == "Sålt":
        return Transfer_t.SELL
    elif ttstr == "Köpt":
        return Transfer_t.BUY
    else:
        return Transfer_t.ERR


# todo: do this for Player also
@dataclass
class HistEntry:
    ttype: Transfer_t = Transfer_t.ERR
    date: str = ""
    name: str = ""
    other_team: str = ""    # new/old team depending on transfer type
    age: int = 0
    transfer_sum: int = 0
    player_value: int = 0


def parse_transfer_history(soup: BeautifulSoup) -> list[HistEntry]:
    entries: list[HistEntry] = []
    info: ResultSet = soup.find_all("tr", {"class":"rowMarker"})
    for row in info:
        text: list = [field.replace("\xa0", " ") for field 
                      in row.stripped_strings]
        entry = HistEntry()
        entry.date = text[0]
        entry.ttype = get_transfer_type(text[1])
        entry.name = text[2]
        entry.age = int(text[3])
        entry.other_team = text[4]
        entry.transfer_sum = int(numstr(text[5]))
        entry.player_value = int(numstr(text[6]))
        entries += [entry]

    return entries


def print_hist_entry(e: HistEntry, rank: int, sold: bool) -> None:
    arrow: str = "TO" if sold else "FROM"
    print(f"{e.date} {e.name}, {e.age} {arrow} {e.other_team}")
    print(f"    Transfer sum: {e.transfer_sum}")
    print(f"    Player value: {e.player_value}")

""" This function assumes that e is in bought. """
def is_flipped(e: HistEntry, sold: list[HistEntry]) -> bool:
    
    for i in range(len(sold)):
        if e.name == sold[i].name:
            # Found player! Now check dates.
            pass



def show_history(entries: list[HistEntry]) -> None:
    """
    The plan is to do the following:
    * separate sold and bought players
    * sort them based on transfer_sum
    * calculate stuff
    * print results
    """
    bought: list[HistEntry] = []
    sold: list[HistEntry] = []

    # Place entries in bought/sold
    for e in entries:
        if e.ttype == Transfer_t.BUY:
            bought += [e]
        elif e.ttype == Transfer_t.SELL:
            sold += [e]
        else:
            # Shouldn't happen but you never know!
            yell(f"ERR transfer type detected for {e.name}.", Msg_t.ERR)

    # A flipped player is first bought then sold. 
    # This is basically filtering out homegrown players,
    # to see how successful transfer purchases are.
    flipped: list[HistEntry] = []
    
    # Need to figure out how to detect if its actually a flipped player.
    # Could be for example that we sell a homegrown player
    # and then buy him back later.

    
        






    
