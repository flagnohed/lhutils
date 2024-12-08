from utils import (
    Msg_t,
    yell,
    printable_num
)

class Player:
    def __init__(self):
        self.age: int = 0
        self.bday: int = 0			  # [1, 7]
        self.bweek: int = 0			  # [1, 13]
        self.value: int = 0
        self.idx: int = 0   		  # 1-based index for transfers.
        self.name: str = ""
        self.pos: str = ""
        self.bid: str = ""			  # Starting bid in parenthesis if no bids. 	 

    def get_trainings_left(self, week: int, day: int) -> int:
        """ Gets the number of training occasions remaining 
            before birthday. """
        wdiff: int = (self.bweek - week) % 13
        if wdiff < 0:
            wdiff += 13
        
        dose_reset: bool = day == 7	
        last_training: bool = self.bday == 7		
        return wdiff + int(last_training) - int(dose_reset)
    
def print_value_predictions(players: list[Player], week, day) -> None:
    """ Predicts the value of a player at the end of 
        the given age (after last training). """ 

    if not players:
        yell("No players found.", Msg_t.ERROR)

    headline: str = ""
    DIVIDER_LENGTH: int = 20
    for p in players:
        rem_trainings: int = p.get_trainings_left(week, day)
        yell(DIVIDER_LENGTH * "-", Msg_t.INFO)

        if p.idx:
            # This means we have parsed the transfer list
            headline = f"{p.idx}. {p.name}, {p.age}, {p.bid}, {p.pos}"
        else:
            # At the moment this can only be roster
            headline = f"{p.name}, {p.age}, {p.pos}"

        yell(headline, Msg_t.APP)
        yell(f"Värde:	{printable_num(p.value)} kr", Msg_t.APP)
        if p.age == 17:
            # Players over the age of 17 rarely develop at 300k/w
            yell(f"300k/w: {printable_num(p.value + rem_trainings * 300000)} kr",
                 Msg_t.APP)

        yell(f"400k/w: {printable_num(p.value + rem_trainings * 400000)} kr",
             Msg_t.APP)
        yell(f"500k/w: {printable_num(p.value + rem_trainings * 500000)} kr",
             Msg_t.APP)

        if p.age > 17:
            yell(f"600k/w: {printable_num(p.value + rem_trainings * 600000)} kr",
                 Msg_t.APP)

    yell(DIVIDER_LENGTH * "-", Msg_t.INFO)
    # Display some info that might be interesting.
    # Number of good players (+ percentage) (if filter was enabled)
    # Count players per position