from dataclasses import dataclass
from framework.utils import msg
from framework.tactics import TACTICS

GAME_FPATH = "txt/game.txt"
STR_PENALTY = "UTV"
STR_SHOT = "SOG"
STR_INJURY = "Skada,"
STR_GAME_ID = "Match-id: "
STR_ARENA = "Arena:"  # Whitespace intentionally left out, because of typo in
# Livehockey game file.
STR_GAME_TYPE = "Matchtyp: "
STR_GAME_DATE = "Matchdatum: "
STR_GRADE = "Lagbetyg: "
STR_ICE_TIME = "Istid: "
ABBR_LEN = 3


@dataclass
class Event:
    time: tuple[str, str] = (0, 0)
    player_name: str = ""
    team_abbr: str = ""


@dataclass
class Shot(Event): ...


@dataclass
class Injury(Event): ...


@dataclass
class Penalty(Event):
    penalty_type: str = ""


@dataclass
class Goal(Event):
    goal_format: str = "ES"
    a1: str = ""
    a2: str = ""


@dataclass
class Player:
    name: str = ""
    shots: int = 0
    goals: int = 0
    pen_mins: int = 0


def is_event(line: str) -> bool:
    return line.startswith("(")


def is_goal(et: str) -> bool:
    return len(et) == 3 and et[0].isnumeric() and et[2].isnumeric()


def parse_goal(_re: str, _time: tuple[str, str], _name: str) -> Goal:
    """Parses _re and checks for goal in special teams (PP/BP)
    and if we got any assists. It does NOT check team abbreviation,
    since goals does not have that."""
    e = Goal(_time, _name)
    i_close_paren: int = _re.find(")")
    paren_content: str = _re[:i_close_paren]
    if len(paren_content) == 2:
        # Either PP or BP goal.
        e.goal_format = paren_content
        _re = _re[i_close_paren + 3 :]

    # Check for assists
    i_close_paren = _re.find(")")
    if i_close_paren == -1:
        # No assists. At the moment (2025) this is not
        # possible, but they might add it in the future, so
        # me being good at planning, we have this check here.
        return e

    paren_content = _re[:i_close_paren]
    if len(paren_content) != 3:
        assists: list[str] = paren_content.split(", ")
        e.a1 = assists[0]
        e.a2 = assists[1] if len(assists) == 2 else ""

    return e


def get_events(lines: list[str]) -> list[Event]:
    event_type: str = ""
    _time: tuple[str, str] = ("", "")

    events: list[Event] = []
    i_space: int = 0
    raw_events: list[str] = [line for line in lines if is_event(line)]
    i_open_paren: int = 0
    i_close_paren: int = 0

    for _re in raw_events:
        e = None
        _penalty_type = ""
        # Get event time and cut it from _re.
        # Example time: (13:37)
        i_close_paren = _re.find(")")
        _time = tuple(_re[1:i_close_paren].split(":"))
        _re = _re[i_close_paren + 2 :]  # Remove succeeding whitespace as well.

        # Get event type
        i_space = _re.find(" ")
        event_type = _re[:i_space]
        _re = _re[i_space + 1 :]

        if event_type == STR_PENALTY:
            # Penalties are the only events that doesn't have
            # the "main" player name after event_type.
            # Instead, first parse the penalty type.
            i_close_paren = _re.find(")")
            _penalty_type = _re[1:i_close_paren]
            e = Penalty(_time, _penalty_type)
            _re = _re[i_close_paren + 2 :]

        # Now we can be sure the name of the "main" player of the event
        # comes.
        i_open_paren = _re.find("(")
        _name = _re[: i_open_paren - 1]
        _re = _re[i_open_paren + 1 :]

        # Handle the rest of the event types
        if is_goal(event_type):
            e = parse_goal(_re, _time, _name)
            # Goals do not have abbreviations, so add it to event list
            # and move on.
            events += [e]
            continue

        # Parse team abbreviation.
        if len(_re) != ABBR_LEN + 2:
            print(_re)

        _abbr = _re[:-2]

        if event_type == STR_SHOT:
            e = Shot(_time, _name, _abbr)

        elif event_type == STR_INJURY:
            e = Injury(_time, _name, _abbr)

        elif event_type == STR_PENALTY:
            # We have already created e, but haven't added
            # abbreviation and player name yet, so do that now.
            e.team_abbr = _abbr
            e.player_name = _name

        else:
            msg(f"Unknown event type: {event_type}", "red")

        events += [e]

    return events


class Team:
    """Dataclass representing a team in game."""

    def __init__(self):
        self.name: str = ""
        self.tactics: str = ""
        self.grade: int = 0

    def get_abbr(self) -> str:
        return self.name[:3]

    def line_to_letter(self, line: int) -> str:
        """For example 1 -> A, 2 -> B, 3 -> C."""
        # 34-34-32 (1-2-3) is the normal case.
        pass


@dataclass
class Game:
    def __init__(self):
        self.home: Team = None
        self.away: Team = None
        self._id: str = ""
        self._date: str = ""
        self.arena: str = ""
        self._type: str = ""
        self.events: list[Event] = []


def get_game_info(lines: list[str]) -> Game:
    game = Game()
    home = Team()
    away = Team()
    home_team_found: bool = False  # First team encountered is the home team.
    home_tactics_found: bool = False
    for i, line in enumerate(lines):
        if line[0] == " " or line.isspace():
            continue

        if line.startswith(STR_GAME_DATE):
            game._date = line[len(STR_GAME_DATE) :].strip()

        elif line.startswith(STR_GAME_ID):
            game._id = line[len(STR_GAME_ID) :].strip()

        elif line.startswith(STR_ARENA):
            game.arena = line[len(STR_ARENA) :].strip()

        elif line.startswith(STR_GAME_TYPE):
            game._type = line[len(STR_GAME_TYPE) :].strip()

        elif line.startswith(STR_GRADE):
            if home_team_found:
                away.name = lines[i - 1].strip()
                away.grade = int(line[len(away.name) :])
            else:
                home_team_found = True
                home.name = lines[i - 1].strip()
                home.grade = int(line[len(home.name) :])

        elif line.startswith(STR_ICE_TIME):
            if home_tactics_found:
                away.tactics = line[len(STR_ICE_TIME) :].strip()
            else:
                home_tactics_found = True
                home.tactics = line[len(STR_ICE_TIME) :].strip()

    game.home = home
    game.away = away
    game.events = get_events(lines)
    return game


def print_game(game: Game) -> None:
    print(
        game.arena,
        game.home.name,
        game.away.name,
        game._date,
        game._id,
        game._type,
    )


def parse_game(fpath: str):
    lines: list[str] = []
    with open(fpath, encoding="utf-8") as f:
        lines = f.readlines()

    game = get_game_info(lines)
    print_game(game)


# for testing
if __name__ == "__main__":
    parse_game(GAME_FPATH)
