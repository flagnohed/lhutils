"""Roster module. Parses roster HTML file."""

from bs4 import BeautifulSoup, PageElement, ResultSet
from player import Player
from utils import numstr


ID2POS_DICT: dict[str, str] = {
    "ucTeamSquadGoalkeepers": "GK",
    "ucTeamSquadDefenders": "DEF",
    "ucTeamSquadForwards": "FWD",
}


def is_player_anchor(anchor: PageElement):
    """Helper function to determine if we found a player or just junk."""
    return anchor["href"].startswith("/Pages/Player/Player.aspx?Player_Id=")


def parse_roster(soup: BeautifulSoup) -> list[Player]:
    """Parses an HTML file and looks for players."""
    values: ResultSet[PageElement] = soup.find_all("td", {"class": "right value"})
    players: list[Player] = []
    title: str = ""
    for anchor in soup.find_all("a"):

        if not is_player_anchor(anchor):
            continue

        try:
            title = anchor["title"]
        except KeyError:
            continue

        player: Player = Player()
        title_list: list[str] = title.split("\n")
        birthdate = numstr(title_list[4])

        player.name = anchor.get_text()
        player.pos = ID2POS_DICT[anchor["id"].split("_")[3]]
        player.age = int(numstr(title_list[0]))
        player.bday = int(birthdate[-1])
        player.bweek = int(birthdate[:-1])
        player.value = int(numstr(values[len(players)].string))

        players += [player]

    return players
