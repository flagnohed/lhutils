from dataclasses import dataclass
from framework.utils import msg

GAME_FPATH = "txt/game.txt"
ABBR_LEN = 3


@dataclass
class Event():
    """ Can be a shot or an injury. 
        Also acts like a parent class
        for goals and penalties. """
    time: tuple[str, str] = (0, 0)
    player_name: str = ""
    team_abbr: str = ""
    is_injury: bool = False

@dataclass
class Penalty(Event):
    penalty_type: str = ""

@dataclass
class Goal(Event):
    goal_format: str = "ES"
    a1: str = ""
    a2: str = ""

def is_event(line: str) -> bool:
    return line.startswith("(")

def is_goal(et: str) -> bool:
    return len(et) == 3 and et[0].isnumeric() and et[2].isnumeric()

def parse_goal(_re: str, _time: tuple[str, str], _name: str) -> Goal:
    """ Parses _re and checks for goal in special teams (PP/BP)
        and if we got any assists. It does NOT check team abbreviation, 
        since goals does not have that. """
    e = Goal(_time, _name)
    i_close_paren: int = _re.find(")")
    paren_content: str = _re[:i_close_paren]
    if len(paren_content) == 2:
        # Either PP or BP goal.
        e.goal_format = paren_content
        _re = _re[i_close_paren+3:]
    
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
    raw_events: list[str] = [l for l in lines if is_event(l)]
    i_open_paren: int = 0
    i_close_paren: int = 0

    for _re in raw_events:
        e = None
        _penalty_type = ""
        # Get event time and cut it from _re. 
        # Example time: (13:37)
        i_close_paren = _re.find(")")
        _time = tuple(_re[1:i_close_paren].split(":"))
        _re = _re[i_close_paren+2:]  # Remove succeeding whitespace as well.

        # Get event type
        i_space = _re.find(" ")
        event_type = _re[:i_space]
        _re = _re[i_space+1:]

        if event_type == "UTV":
            # Penalties are the only events that doesn't have
            # the "main" player name after event_type.
            # Instead, first parse the penalty type.
            i_close_paren = _re.find(")")
            _penalty_type = _re[1:i_close_paren]
            e = Penalty(_time, _penalty_type)
            _re = _re[i_close_paren+2:]

        # Now we can be sure the name of the "main" player of the event
        # comes.
        i_open_paren = _re.find("(")
        _name = _re[:i_open_paren-1]
        _re = _re[i_open_paren+1:]

        # Handle the rest of the event types
        if is_goal(event_type):
            e = parse_goal(_re, _time, _name)
            # Goals do not have abbreviations, so add it to event list
            # and move on.
            events += [e]
            continue

        # Parse team abbreviation.
        if len(_re) != ABBR_LEN + 1:
            print(_re)

        _abbr = _re[:-1]

        if event_type == "SOG":
            e = Event(_time, _name, _abbr)

        elif event_type == "Skada,":
            e = Event(_time, _name, _abbr, is_injury=True)

        elif event_type == "UTV":
            # We have already created e, but haven't added
            # abbreviation and player name yet, so do that now.
            e.team_abbr = _abbr
            e.player_name = _name

        else:
            msg(f"Unknown event type: {event_type}", "red")

        events += [e]
    
    return events
        

def parse_game(fpath: str):
    lines: list[str] = []
    with open(fpath, encoding="utf-8") as f:
        lines = f.readlines()

    events: list[Event] = get_events(lines)
    for e in events:
        print(f"{e.player_name}: {e.time}: {e.team_abbr}")

# for testing
if __name__ == "__main__":
    parse_game(GAME_FPATH)