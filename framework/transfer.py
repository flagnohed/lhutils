"""Transferlist module."""

import dataclasses

from enum import Enum
from bs4 import BeautifulSoup, PageElement, ResultSet
from .player import Player
from .utils import (
    numstr,
    printable_num,
    wstext2int,
    msg,
    CLR_GREEN,
    CLR_RED,
)


class TransferType(Enum):
    """Type of transfer transaction."""

    ERR = 0
    BUY = 1
    SELL = 2
    FLIP = 3


DATE_FORMAT: str = "%Y-%m-%d"


def parse_transfers_html(soup: BeautifulSoup) -> list[Player]:
    """Main parser function for transfers if HTML file as input. Called from main."""
    players: list[Player] = []
    div: PageElement = None

    information: ResultSet = soup.find_all("div", {"class": "ts_collapsed_1"})
    values: ResultSet = soup.find_all("div", {"class": "ts_collapsed_3"})
    bids: ResultSet = soup.find_all("div", {"class": "ts_collapsed_5"})

    for i, div in enumerate(information):
        player: Player = Player()
        # Info has kind of a weird structure:
        # [idx, player_name, ',', 'x år', '(W-D), pos, shoots]
        info: list[str] = list(div.stripped_strings)

        player.name = info[1]
        player.age = int(numstr(info[3]))
        bdate_str: str = numstr(info[4])
        player.bday = int(bdate_str[-1])  # last digit is bday,
        player.bweek = int(bdate_str[:-1])  # and the rest is bweek.
        player.pos = info[4].split(", ")[1]
        player.value = int(numstr(values[i].get_text()))
        player.bid = wstext2int(bids[i].get_text())
        player.idx = i + 1
        players += [player]

    return players


def parse_until(line: str, indicator: str) -> list[str]:
    """ Parses LINE until INDICATOR is found. Then returns 
        the rest of LINE after INDICATOR.
        Returns [parsed_text, rest_of_line]. """
    i: int = line.find(indicator)
    return [line[:i], line[i + len(indicator):]]    


def parse_transfers_txt(lines: list[str]) -> list[Player]:
    players: list[Player] = []
    for line in lines:
        if not line[0].isdigit():
            # Not a player entry, just ignore it and move on.
            continue

        player: Player = Player()
        idx_str, line = parse_until(line, ".")
        player.idx = int(idx_str)
        player.name, line = parse_until(line, " Lag: ")  # Intentional leading whitespace
        # Can parse team name here, but since we do not care about 
        # the selling team at the moment, we can use this helper function
        # to skip forward in LINE.
        _, line = parse_until(line, "Position: ")
        player.pos, line = parse_until(line, "Skjuter: ")
        # age_str contains both the age in years and the (week, day) tuple.
        # We can (and we will) get all digits from age_str, and figure out
        # what is what from there.
        age_str, line = parse_until(line, "Värde: ")
        nums = numstr(age_str)
        # Age is always the first two digits
        player.age = int(nums[:2])
        bdate: str = nums[2:]
        # Birth day is the last digit (can only be between 1 and 7),
        # and the birth week is the rest of BDATE.
        player.bday = int(bdate[-1])
        player.bweek = int(bdate[:-1])

        value_str, line = parse_until(line, "Lön: ")
        player.value = int(numstr(value_str))
        # We do not care about salary
        _, line = parse_until(line, "Utgångsbud: ")

        # We only care about what the current bid is, 
        # or at least what the minimal bid we have to offer is.
        # Therefore, we save start_bid for later.
        start_bid, line = parse_until(line, "Deadline: ")
        
        current_bid, line = parse_until(line, "SMBM")  # End of interesting info
        if current_bid == "-":
            player.bid = "(" + start_bid + ")"
        else:
            # Input file will tell which team that put the latest bid, 
            # but we do not care about that, so just parse the current bid
            # until that info comes.
            current_bid, line = parse_until(line, " av ")
            player.bid = current_bid
        
        players += [player]

    return player


def get_transfer_type(ttstr: str) -> TransferType:
    """Convert transfer string to type."""
    if ttstr == "Sålt":
        return TransferType.SELL
    if ttstr == "Köpt":
        return TransferType.BUY

    return TransferType.ERR


# pylint: disable=too-many-instance-attributes
@dataclasses.dataclass
class HistEntry:
    """Represents a single entry in the transfer history table."""

    ttype: TransferType = TransferType.ERR
    date: str = ""
    name: str = ""
    other_team: str = ""  # new/old team depending on transfer type
    age: int = 0
    transfer_sum: int = 0
    player_value: int = 0
    money_gained: int = 0


def parse_transfer_history(soup: BeautifulSoup) -> list[HistEntry]:
    """Main parsing function for the transfer history module."""
    entries: list[HistEntry] = []
    info: ResultSet = soup.find_all("tr", {"class": "rowMarker"})
    for row in info:
        text: list = [
            field.replace("\xa0", " ") for field in row.stripped_strings
        ]
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
    """Prints a single transfer history entry."""
    arrow: str = ""
    # We do not care about ERR here, cannot come past previous function.
    if e.ttype == TransferType.BUY:
        arrow = "from"
    elif e.ttype == TransferType.SELL:
        arrow = "to"

    team: str = "" if e.ttype == TransferType.FLIP else e.other_team
    print(f"{rank}: {e.date} {e.name}, {e.age} {arrow} {team}")

    if e.ttype == TransferType.FLIP:
        g_or_l = "gained" if e.money_gained > 0 else "lost"
        print(f"    Money {g_or_l}: {printable_num(e.money_gained)} kr")
    else:
        print(f"    Transfer sum: {printable_num(e.transfer_sum)} kr")

    if e.ttype != TransferType.FLIP:
        print(f"    Player value: {printable_num(e.player_value)} kr")


def show_top_entries(
    key_func,
    headline: str,
    entries: list[HistEntry],
    num_top_entries: int,
    r: bool,
):
    """Prints at most NUM_PLAYERS entries."""
    entries.sort(key=key_func, reverse=r)
    msg(headline, CLR_GREEN)
    n: int = min(num_top_entries, len(entries))
    for i in range(n):
        print_hist_entry(entries[i], i + 1)


def count_transaction(
    teams: dict[str, list[int, int]], team_name: str, i: int
) -> dict[str, list[int, int]]:
    """Count purchases and sales per team. Displayed in show_history()."""
    modded_teams = teams

    if team_name not in modded_teams:
        modded_teams[team_name] = [0, 0]

    modded_teams[team_name][i] += 1
    return modded_teams


def show_history(entries: list[HistEntry]) -> None:
    """Printing the top transfers for different categories."""
    bought: list[HistEntry] = []
    sold: list[HistEntry] = []
    flipped: list[HistEntry] = []
    bidx: int = -1
    num_top_entries: int = 5
    teams: dict[str, list[int, int]] = {}
    for e in entries:
        if e.ttype == TransferType.BUY:
            teams = count_transaction(teams, e.other_team, 0)
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
            e_copy.ttype = TransferType.FLIP
            bought += [e]
            flipped += [e_copy]

        elif e.ttype == TransferType.SELL:
            teams = count_transaction(teams, e.other_team, 1)
            sold += [e]
        else:
            # Shouldn't happen but you never know!
            msg(f"ERR transfer type detected for {e.name}.", CLR_RED)

        bidx = -1

    print(f"===== {num_top_entries} teams most traded with =====")
    teams = dict(
        sorted(teams.items(), key=lambda item: sum(item[1]), reverse=True)
    )
    num_items: int = 20
    items = list(teams.items())[:num_items]
    for i, item in enumerate(items):
        name, transactions = item
        print(f"{i + 1}. {name}")
        print(f"    Times bought from: {transactions[0]}")
        if name != "Free agent":
            # Cannot sell to free agency. If they go to free agency
            # they were fired, which does not show in transfer history.
            print(f"    Times sold to:     {transactions[1]}")

    show_top_entries(
        lambda x: x.transfer_sum,
        f"\n===== {num_top_entries} most expensive players bought =====",
        bought,
        num_top_entries,
        True,
    )

    show_top_entries(
        lambda x: x.transfer_sum,
        f"\n===== {num_top_entries} most expensive players sold =====",
        sold,
        num_top_entries,
        True,
    )

    show_top_entries(
        lambda x: x.money_gained,
        f"\n===== {num_top_entries} most gained (flipped players) =====",
        flipped,
        num_top_entries,
        True,
    )

    show_top_entries(
        lambda x: x.money_gained,
        f"\n===== {num_top_entries} most lost (flipped players) =====",
        flipped,
        num_top_entries,
        False,
    )
