from bs4 import BeautifulSoup, PageElement, ResultSet
import dataclasses
from enum import Enum
from player import Player
from utils import (
    Msg_t,
    numstr,
    printable_num,
    wstext2int,
    yell,
)


class Transfer_t(Enum):
    ERR = 0
    BUY = 1
    SELL = 2
    FLIP = 3


DATE_FORMAT: str = "%Y-%m-%d"


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

        # Info has kind of a weird structure:
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


def get_transfer_type(ttstr: str) -> Transfer_t:
    if ttstr == "Sålt":
        return Transfer_t.SELL
    elif ttstr == "Köpt":
        return Transfer_t.BUY
    else:
        return Transfer_t.ERR


@dataclasses.dataclass
class HistEntry:
    ttype: Transfer_t = Transfer_t.ERR
    date: str = ""
    name: str = ""
    other_team: str = ""    # new/old team depending on transfer type
    age: int = 0
    transfer_sum: int = 0
    player_value: int = 0
    money_gained: int = 0


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


def print_hist_entry(e: HistEntry, rank: int) -> None:
    arrow: str = ""

    # We do not care about ERR here, cannot come past previous function.
    if e.ttype == Transfer_t.BUY:
        arrow = "from"
    elif e.ttype == Transfer_t.SELL:
        arrow = "to"

    team: str = "" if e.ttype == Transfer_t.FLIP else e.other_team
    print(f"{rank}: {e.date} {e.name}, {e.age} {arrow} {team}")

    if e.ttype == Transfer_t.FLIP:
        print(f"    Money gained: {printable_num(e.money_gained)} kr")
    else:
        print(f"    Transfer sum: {printable_num(e.transfer_sum)} kr")

    if e.ttype != Transfer_t.FLIP:
        print(f"    Player value: {printable_num(e.player_value)} kr")


def show_top_entries(key_func, msg: str, entries: list[HistEntry],
                     num_players: int, r: bool):
    entries.sort(key=key_func, reverse=r)
    yell(msg, Msg_t.INFO)
    n: int = min(num_players, len(entries))
    for i in range(n):
        print_hist_entry(entries[i], i + 1)


def show_history(entries: list[HistEntry]) -> None:

    bought: list[HistEntry] = []
    sold: list[HistEntry] = []
    flipped: list[HistEntry] = []
    bidx: int = -1
    msg: str = ""
    num_players: int = 5

    for e in entries:
        if e.ttype == Transfer_t.BUY:
            try:
                bidx = [s.name for s in sold].index(e.name)
            except ValueError:
                # Not a flipped player
                bought += [e]
                continue
            # A player is flipped if sold after bought.
            # This means that if we find a sold player,
            # check if he already has been added to BOUGHT --> flipped
            # There COULD be errors here, since multiple players can
            # have the same name, and we have no other way of checking
            # identity of player at this time (maybe if we start webscraping)

            e_copy = dataclasses.replace(e)
            e_copy.money_gained = sold[bidx].transfer_sum - e.transfer_sum
            e_copy.ttype = Transfer_t.FLIP
            bought += [e]
            flipped += [e_copy]


        elif e.ttype == Transfer_t.SELL:
            sold += [e]
        else:
            # Shouldn't happen but you never know!
            yell(f"ERR transfer type detected for {e.name}.", Msg_t.ERR)

        bidx = -1

    # Print results
    msg = f"\n===== {num_players} most expensive players bought ====="
    show_top_entries(lambda x: x.transfer_sum, msg, bought, num_players, True)

    msg = f"\n===== {num_players} most expensive players sold ====="
    show_top_entries(lambda x: x.transfer_sum, msg, sold, num_players, True)

    msg = f"\n===== {num_players} most gained (flipped players) ====="
    show_top_entries(lambda x: x.money_gained, msg, flipped, num_players, True)

    msg = f"\n===== {num_players} most lost (flipped players) ====="
    show_top_entries(lambda x: x.money_gained, msg, flipped, num_players, False)