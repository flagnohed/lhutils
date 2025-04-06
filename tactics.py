from itertools import combinations
from utils import yell, Msg_t


TACTICS = {
    "343432":
    "ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB",
    "454015":
    "ABABCABABCABABCABABAABABCABABCABABCABABAABABCABABCABABCABABAABABC",
    "453520":
    "ABABCACABCABABCABABAABABCACABCABABCABABAABABCACABCABABCABABAABABC",
    "403030":
    "ABCABCABACABCABCABCAABCABCABACABCABCABCAABCABCABACABCABCABCAABCAB",
    "403525":
    "ABABCABABCACABCABABCABABCACABCABABCABABCACABCABABCABABCABABCABABC",
    "404020":
    "ABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABC"
}


def get_matchup_count(t1: str, t2: str) -> dict[str, int]:
    if len(t1) != len(t2) or t1 not in TACTICS.keys() or \
        t2 not in TACTICS.keys():
        yell(f"Invalid tactics: {t1} vs {t2}", Msg_t.ERROR)

    meetings: dict[str, int] = {}
    
    lseq1: str = TACTICS[t1]
    lseq2: str = TACTICS[t2]
    assert len(lseq1) == len(lseq2)

    for i in range(len(lseq1)):
        combo: str = lseq1[i] + lseq2[i]
        if combo in meetings.keys():
            meetings[combo] += 1
        else:
            # Path taken on first encounter of current combo
            meetings[combo] = 1
    
    return meetings


def print_matchup_percentage(meetings: dict[str, int], 
                             show_matchups: bool = False) -> float:
    # A "better" matchup is when for example line 'A' meets opponents' line 'B'
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
            yell(f"{t1_line} vs {t2_line}: {cur_matchup}", Msg_t.APP)
    
    percentage: float = num_better_matchups/total_matchups * 100
    yell("Percentage with better line on ice: %.2f" % percentage + "%", Msg_t.INFO)


def compare_tactics(t1: str) -> None:
    """ Get every tactic combination, and print how often 
        our team will play a 'better' line than the opps. """
    
    matchups = list(combinations(TACTICS.keys(), 2))
    if t1:
        # Only include matchups where supplied 
        # tactic is present.
        matchups = [x for x in matchups if x[0] == t1]

    for t1, t2 in matchups:
        yell(f"===== Matchup: {t1} vs {t2} =====")
        meetings_unsorted = get_matchup_count(t1, t2)
        meetings = {k: v for k, v in sorted(meetings_unsorted.items(), 
                                            key=lambda x: x[1], reverse=True)}
        print_matchup_percentage(meetings, True)