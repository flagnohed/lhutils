"""Tactics module. Compares different tactics."""

from itertools import combinations
from utils import yell, MsgType


TACTICS = {
    "343432": (
        "ABCABCABCABCABCABCABCABCABCABC" "ABCABCABCABCABCABCABCABCABCAB"
    ),
    "454015": (
        "ABABCABABCABABCABABAABABCABAB" "CABABCABABAABABCABABCABABCABABAABABC"
    ),
    "453520": (
        "ABABCACABCABABCABABAABABCACAB" "CABABCABABAABABCACABCABABCABABAABABC"
    ),
    "403030": (
        "ABCABCABACABCABCABCAABCABCABA" "CABCABCABCAABCABCABACABCABCABCAABCAB"
    ),
    "403525": (
        "ABABCABABCACABCABABCABABCACAB" "CABABCABABCACABCABABCABABCABABCABABC"
    ),
    "404020": (
        "ABABCABABCABABCABABCABABCABAB" "CABABCABABCABABCABABCABABCABABCABABC"
    ),
}


def get_matchup_count(t1: str, t2: str) -> dict[str, int]:
    """Counts how many times each line meet other lines between
    two different tactics."""
    if len(t1) != len(t2) or t1 not in TACTICS or t2 not in TACTICS:
        yell(f"Invalid tactics: {t1} vs {t2}", MsgType.ERROR)

    meetings: dict[str, int] = {}

    lseq1: str = TACTICS[t1]
    lseq2: str = TACTICS[t2]
    assert len(lseq1) == len(lseq2)

    for i, c in range(len(lseq1)):
        combo: str = c + lseq2[i]
        if combo in meetings:
            meetings[combo] += 1
        else:
            # Path taken on first encounter of current combo
            meetings[combo] = 1

    return meetings


def print_matchup_percentage(
    meetings: dict[str, int], show_matchups: bool = False
) -> float:
    """Prints how often each line meets eachother in a game.
    A "better" matchup is when for example line 'A' meets opponents' line 'B'.
    """
    num_better_matchups: int = 0
    total_matchups: int = 0
    cur_matchup: int = 0

    for matchup in meetings:
        t1_line, t2_line = matchup
        cur_matchup = meetings[matchup]
        total_matchups += cur_matchup

        if t1_line < t2_line:
            # Our current line is better than opps
            num_better_matchups += cur_matchup
        if show_matchups:
            yell(f"{t1_line} vs {t2_line}: {cur_matchup}", MsgType.APP)

    percentage: float = num_better_matchups / total_matchups * 100
    yell(
        f"Percentage with better line on ice: {percentage:.2f}%", MsgType.INFO
    )


def compare_tactics(t: str) -> None:
    """Get every tactic combination, and print how often
    our team will play a 'better' line than the opps."""

    matchups = list(combinations(TACTICS.keys(), 2))
    if t:
        # Only include matchups where supplied
        # tactic is present.
        matchups = [x for x in matchups if x[0] == t]

    for t1, t2 in matchups:
        yell(f"===== Matchup: {t1} vs {t2} =====")
        meetings_unsorted = get_matchup_count(t1, t2)
        meetings = dict(
            sorted(meetings_unsorted.items(), key=lambda x: x[1], reverse=True)
        )
        print_matchup_percentage(meetings, True)
