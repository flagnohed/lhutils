from itertools import combinations
from utils import yell, Msg_t

# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------

def compare(t1: str, t2: str) -> None:
    if len(t1) != len(t2) or t1 not in TACTICS.keys() or \
        t2 not in TACTICS.keys():
        yell(f"Invalid tactics: {t1} vs {t2}", Msg_t.ERROR)

    lines = ['A', 'B', 'C']
    matchups = set(combinations(lines + lines, 2))
    meetings = {}
    for i, mu in enumerate(matchups):
        t1m, t2m = mu

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    t1 = "343432"
    t2 = "454015"
    compare(t1, t2)

# ------------------------------------------------------------------------------
