"""Player module."""

import dataclasses
from utils import MsgType, yell, printable_num


DIVIDER_LENGTH: int = 30
MAX_WEEKS: int = 13
MAX_DAYS: int = 7


@dataclasses.dataclass
class Player:
    """Class representing a single player."""

    age: int = 0
    bday: int = 0  # [1, 7]
    bweek: int = 0  # [1, 13]
    value: int = 0
    idx: int = 0  # 1-based index for transfers.
    name: str = ""
    pos: str = ""
    bid: str = ""  # Starting bid in parenthesis if no bids.
    note: str = ""


def get_trainings_left(player: Player, week: int, day: int) -> int:
    """Gets the number of training occasions remaining
    before birthday."""
    wdiff: int = (player.bweek - week) % 13
    if wdiff == 0 and day > player.bday:
        # This happens if the player already have had his birthday,
        # but we are still in that week.
        wdiff = MAX_WEEKS

    dose_reset: bool = day == MAX_DAYS
    last_training: bool = player.bday == MAX_DAYS

    return wdiff + int(last_training) - int(dose_reset)


def print_value_predictions(players: list[Player], week, day) -> None:
    """Predicts the value of a player at the end of
    the given age (after last training)."""

    if not players:
        yell("No players found.", MsgType.ERROR)

    headline: str = ""
    for p in players:
        rem_trainings: int = get_trainings_left(p, week, day)
        yell(DIVIDER_LENGTH * "-", MsgType.INFO)

        if p.idx:
            # This means we have parsed the transfer list
            headline = f"{p.idx}. {p.name}, {p.age}, {p.bid}, {p.pos}, {p.note}"
        else:
            # At the moment this can only be roster
            headline = f"{p.name}, {p.age}, {p.pos}"

        yell(headline, MsgType.APP)
        yell(f"Värde :	 {printable_num(p.value)} kr", MsgType.APP)

        if p.age == 17:
            # Players over the age of 17 rarely develop at 300k/w.
            # And if they do, they're shit.
            yell(
                f"300k/w: {printable_num(p.value + rem_trainings * 300000)} kr",
                MsgType.APP,
            )

        yell(
            f"400k/w: {printable_num(p.value + rem_trainings * 400000)} kr", MsgType.APP
        )
        yell(
            f"500k/w: {printable_num(p.value + rem_trainings * 500000)} kr", MsgType.APP
        )

        if p.age > 18:
            yell(
                f"600k/w: {printable_num(p.value + rem_trainings * 600000)} kr",
                MsgType.APP,
            )
            yell(
                f"700k/w: {printable_num(p.value + rem_trainings * 700000)} kr",
                MsgType.APP,
            )

        if p.age > 19:
            yell(
                f"800k/w: {printable_num(p.value + rem_trainings * 800000)} kr",
                MsgType.APP,
            )

    yell(DIVIDER_LENGTH * "-", MsgType.INFO)
