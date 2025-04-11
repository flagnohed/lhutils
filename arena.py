"""
The arena module can do the following:
* calculate rent for a certain arena size,
* show the best proportions (money wise) for a certain arena size,
* calculate the cost of demolishing/building to a certain arena size,
* show how long it would take to make profit of a demolition.
"""

# Seats
CUR_SHORT: int = 12500
CUR_LONG: int = 30000
CUR_VIP: int = 7500
CUR_TOTAL: int = CUR_SHORT + CUR_LONG + CUR_VIP
SHORT_INTERVAL: int = 2500
LONG_INTERVAL: int = 5000
VIP_INTERVAL: int = 500
CUR_RENT: int = 655060

COSTS_PER_SEAT: dict[int, tuple[int, int, int]] = {
    0: (108, 150, 246),  # LHL
    1: (97, 139, 235),
    2: (87, 129, 225),
    3: (78, 120, 221),
    4: (70, 112, 215),
    5: (63, 106, 209),
    # We don't care about div 6, impossible to be that bad.
}


def calculate_rent(arena_size: int) -> int:
    """Calculates the rent costs based on arena size."""
    rent: int = 0
    short, long, vip = get_best_proportions(arena_size)
    # Kortsida
    intervals: int = short // SHORT_INTERVAL
    cost_per_seat_interval = [4 + i for i in range(intervals)]
    rent += sum(cost_per_seat_interval) * SHORT_INTERVAL
    # Långsida
    intervals = long // LONG_INTERVAL
    cost_per_seat_interval = [5 + 2 * i for i in range(intervals)]
    cost_per_seat_interval[0] += 2
    rent += (sum(cost_per_seat_interval)) * LONG_INTERVAL
    # VIP
    intervals = vip // VIP_INTERVAL
    cost_per_seat_interval = [15 + 3 * i for i in range(intervals)]
    rent += sum(cost_per_seat_interval) * VIP_INTERVAL

    return rent


def get_best_proportions(arena_size: int) -> tuple[int, int, int]:
    """The idea is to maximize VIP and Long side seats, since
    ticket prices are more expensive there."""
    best_short = int(arena_size * 0.25)
    best_long = int(arena_size * 0.6)
    best_vip = int(arena_size * 0.15)
    return best_short, best_long, best_vip


def calculate_arena_change_cost(old_size: int, new_size: int) -> int:
    """Calculate cost of demolishing/building seats."""
    if new_size == old_size:
        return 0

    demolish: bool = new_size < old_size

    seats_short, seats_long, seats_vip = get_best_proportions(
        max(old_size, new_size) - min(old_size, new_size)
    )
    cost_base = 200000 if demolish else 350000
    cost_short = 30 if demolish else 175
    cost_long = 40 if demolish else 300
    cost_vip = 60 if demolish else 1500

    return (
        cost_base
        + cost_short * seats_short
        + cost_long * seats_long
        + cost_vip * seats_vip
    )


def calc_income(arena_size: int, division: int) -> int:
    """Calculates income per game for a given arena size and division."""
    short_seats, long_seats, vip_seats = get_best_proportions(arena_size)
    cps_short, cps_long, cps_vip = COSTS_PER_SEAT[division]
    income = (
        short_seats * cps_short + long_seats * cps_long + vip_seats * cps_vip
    )
    return income


def print_percentages(short: int, long: int, vip: int):
    """Shows how much of the arena is a certain arena module."""
    print(f"Kortsida: {short / CUR_TOTAL}")
    print(f"Långsida: {long / CUR_TOTAL}")
    print(f"VIP:      {vip / CUR_TOTAL}")


def print_test_case(old_size, new_size) -> None:
    """Main driver. Called from main.py."""
    build_cost: int = 0
    demolition_cost: int = 0
    print("----------")

    if new_size == old_size:
        print("Stupid test, ingore.")
        return

    if new_size < old_size:
        demolition_cost = calculate_arena_change_cost(old_size, new_size)
        print(f"Demolish {old_size} -> {new_size}: {demolition_cost} kr")
    else:
        build_cost = calculate_arena_change_cost(old_size, new_size)
        print(f"Build {old_size} -> {new_size}: {build_cost} kr")

    # Add LHL when the time comes.
    for div in range(1, 6):
        print(
            f"--> div {div}: new income per week: {calc_income(new_size, div)}"
        )

    new_rent = calculate_rent(new_size)
    old_rent = calculate_rent(old_size)

    print(f"New weekly rent: {new_rent}")
    if new_size < old_size:
        rent_saved = old_rent - new_rent
        print(f"Rent saved: {rent_saved} kr")

        build_cost = calculate_arena_change_cost(old_size, new_size)
        print(f"Cost to build back to original size: {build_cost}")

        weeks_until_profit = int((build_cost + demolition_cost) / rent_saved)
        print(f"{weeks_until_profit} weeks before making profit")
    else:
        print(f"Rent increase: {new_rent - old_rent}")
