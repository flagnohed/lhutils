"""Player module."""

import dataclasses
from .utils import (
    msg,
    printable_num,
    CLR_GREEN,
    CLR_RED,
)


DIVIDER_LENGTH: int = 30
MAX_WEEKS: int = 13
MAX_DAYS: int = 7

WEEKLY_INCREASE: dict[int, list[int]] = {
    # Value times 1000. So 300 is 300k.
    17: [300, 400, 500],
    18: [400, 500, 600],
    19: [500, 600, 700, 800],
    20: [700, 800, 900, 1000],
    21: [800, 900, 1000, 1100],
    22: [900, 1000, 1100, 1200],
}


# pylint: disable=too-many-instance-attributes
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
        msg("No players found.", CLR_RED)

    headline: str = ""
    for p in players:
        trainings: int = get_trainings_left(p, week, day)
        msg(DIVIDER_LENGTH * "-", CLR_GREEN)

        if p.idx:
            # This means we have parsed the transfer list
            headline = (
                f"{p.idx}. {p.name}, {p.age}, {p.bid}, {p.pos}, {p.note}"
            )
        else:
            # At the moment this can only be roster
            headline = f"{p.name}, {p.age}, {p.pos}"

        msg(
            headline,
        )
        msg(
            f"Värde : {printable_num(p.value)} kr",
        )
        weekly_increases_list: list[int] = WEEKLY_INCREASE[p.age]
        for wi in weekly_increases_list:
            msg(
                f"{wi}k/w: {printable_num(p.value + trainings * wi * 1000)} kr"
            )

    msg(DIVIDER_LENGTH * "-", CLR_GREEN)
