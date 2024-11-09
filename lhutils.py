# ---------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------

import json
import re
import sys
import unicodedata


from bs4 import BeautifulSoup, ResultSet, PageElement
from io import TextIOWrapper

# ---------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------

FILE_DEVELOPMENT: str = "html/development.html"
FILE_PLAYER: str = "html/player.html"
FILE_ROSTER: str = "html/roster.html"
FILE_TRANSFER: str = "html/transfers.html"

ARGC_MIN: int = 2
ARGC_MAX: int = 4
MAX_DAYS: int = 7
MAX_WEEKS: int = 13
FILTER_DEFAULT_MIN: int = 17
FILTER_DEFAULT_MAX: int = 22

# Predicted Value Thresholds
# |-----|------|-----------------|
# | Age | PVT  | Weekly increase |
# | 17  | 5m   | 300k			 |
# | 18  | 11m  | 400k			 |
# | 19  | 16m  | 500k			 |
# | 20  | 20m  | 600k			 |
# | 21  | 30m  | 700k			 |
# | 22  | 40m  | 700k			 |
# |-----|------|-----------------|
PVT_DICT: dict[int, tuple[int, int]] = {17: (5000000, 300000),  18: (11000000, 400000), 
										19: (16000000, 500000), 20: (20000000, 600000), 
										21: (30000000, 700000), 22: (40000000, 700000)}

ID2POS_DICT: dict[str, str] = {"ucTeamSquadGoalkeepers" : "GK",
							   "ucTeamSquadDefenders" : "DEF",
							   "ucTeamSquadForwards" : "FWD"}

# ---------------------------------------------------------------------------------------
# Global variables
# ---------------------------------------------------------------------------------------

week: int = 0
day: int = 0

# ---------------------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------------------

class Player:
	def __init__(self):
		self.age: int = 0
		self.bday: int = 0					  # [1, 7]
		self.bweek: int = 0					  # [1, 13]
		self.value: int = 0
		self.idx: int = 0   				  # 1-based index for transfers.
		self.name: str = ""
		self.position: str = ""
		self.current_bid: str = ""			  # Starting bid in parenthesis if no bids. 	 

	def get_trainings_left(self) -> int:
		""" Gets the number of training occasions remaining 
			before birthday. """
		wdiff: int = (self.bweek - week) % 13
		dose_reset: bool = day == 7	
		last_training: bool = self.bday == 7		
											
		return wdiff + int(last_training) - int(dose_reset)

# ---------------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------------

def filter_players(players: list[Player], 
				   age_min: int, age_max: int) -> list[Player]:
	""" Filters out bad players, based on values in PVT_DICT.
		Returns a list of players that passed the filter. """
	fplayers: list[Player] = []
	for player in players:
		trainings_left = player.get_trainings_left()
		if player.age in PVT_DICT.keys() and age_min <= player.age <= age_max:
			# Get threshold and weekly increase for the relevant age.
			t, w = PVT_DICT[player.age]
			fplayers += [player] if player.value + trainings_left * w >= t else []
	
	return fplayers
			
# ---------------------------------------------------------------------------------------

def get_current_date(soup: BeautifulSoup) -> list:
	#  Find the current date (in game) in the HTML file
	current_date_str = soup.find(id="topmenurightdateinner").get_text()
	clean_str = unicodedata.normalize("NFKD", current_date_str)
	return [int(a) for a in clean_str.split(' ') if a.isnumeric()]

# ---------------------------------------------------------------------------------------
	
def num2str(num: int) -> str:
	""" Takes an integer, converts it to a string.
		Makes it easier to read large numbers like 5000000 --> 5 000 000. """
	rev_str: str = str(num)[::-1]  # int to str, reverse (add to pretty_str backwards)	
	count: int = 0
	pretty_str: str = ""

	for d in rev_str:
		count += 1
		pretty_str += d
		if count == 3:
			count = 0
			pretty_str += " "
	
	return pretty_str[::-1]

# ---------------------------------------------------------------------------------------

def is_player_anchor(anchor: PageElement):
	return anchor["href"].startswith("/Pages/Player/Player.aspx?Player_Id=")

# ---------------------------------------------------------------------------------------

def numstr(s: str) -> str:
	""" Extract numbers from a string and return those numbers as a new string. """
	return ''.join([c for c in s if c.isdigit()])

# ---------------------------------------------------------------------------------------

""" Determines if argument PARAM is a valid flag. """
def is_flag(param: str) -> bool:
	return param in ["-h", "--help", "-r", "--roster", "-t", 
				  	 "--transfer", "-f", "--filter"]

# ---------------------------------------------------------------------------------------
# Parser functions
# ---------------------------------------------------------------------------------------

def parse_roster(soup: BeautifulSoup) -> list[Player]:
	values: ResultSet[PageElement] = soup.find_all("td", {"class": "right value"})
	players: list[Player] = []

	for anchor in soup.find_all('a'):
		if not is_player_anchor(anchor):
			continue

		player: Player = Player()
		title_list: list[str] = anchor["title"].split('\n')
		birthdate = numstr(title_list[4])

		player.name = anchor.get_text()
		player.position = ID2POS_DICT[anchor["id"].split("_")[3]]
		player.age = int(numstr(title_list[0]))
		player.bday = int(birthdate[-1])
		player.bweek = int(birthdate[:-1])
		player.value = int(numstr(values[len(players)].string))

		players += [player]

	return players

# ---------------------------------------------------------------------------------------

def parse_transfers(soup: BeautifulSoup) -> list[Player]:
	
	# Should probably parse div.get_text() instead of the title.
	# That way we would also get the position. 
	# (todo)
	players: list[Player] = []
	div: PageElement = None

	information: ResultSet = soup.find_all("div", {"class":"ts_collapsed_1"})
	values: ResultSet = soup.find_all("div", {"class":"ts_collapsed_3"})
	current_bids: ResultSet = soup.find_all("div", {"class":"ts_collapsed_5"})

	# Name, age, birthweek and birthday
	for i, div in enumerate(information):
		# Info: NAME, AGE år (Vecka BWEEK, Dag BDAY) 
		player: Player = Player()
		info: str = div["title"].split('\n')[0]
		nstr: str = numstr(info)
		player.name = info.split(',')[0]
		try:
			player.age = int(nstr[:2])  	# First two digits of info is age,
			player.bday = int(nstr[-1]) 	# last digit is bday,
			player.bweek = int(nstr[2:-1])	# and the rest is bweek.
		except ValueError:
			# Because of Windows. Bill Gates is a whore!
			print(f"Skipped guy with weird name at {i + 1} in transferlist.")
			continue
		
		player.value = int(numstr(''.join(values[i].stripped_strings)))
		player.current_bid = ''.join(current_bids[i].stripped_strings)
		player.idx = i + 1
		players += [player]

	return players

# ---------------------------------------------------------------------------------------

def parse(filename: str, short_flag: str) -> list[Player]:
	""" Creates the necessary objects for parsing and 
		calls the correct parser function. """

	file: TextIOWrapper = open(filename, errors="ignore")
	soup: BeautifulSoup = BeautifulSoup(file, "html.parser", from_encoding="utf-8")
	players: list[Player] = []

	# Parse current in-game date.
	global week
	global day
	week, day = get_current_date(soup)

	# We can trust that short_flag is a valid flag here.
	if short_flag == "-r":
		players = parse_roster(soup)
	elif short_flag == "-t":
		players = parse_transfers(soup)
	else:
		print("This should not happen.")
		exit()
	
	return players

# ---------------------------------------------------------------------------------------
# Print functions
# ---------------------------------------------------------------------------------------

def print_value_predictions(players: list[Player]) -> None:
	""" Predicts the value of a player at the end of 
		the given age (after last training). """ 

	if not players:
		print("No players found.")
		exit()

	headline: str = ""
	for player in players:
		rem_trainings: int = player.get_trainings_left()
		print(20 * "-")

		if player.idx:
			# This means we have parsed the transfer list
			headline = f"{player.idx}. {player.name}, {player.age}, {player.current_bid}"
		else:
			# At the moment this can only be roster
			headline = f"{player.name}, {player.age}, {player.position}"

		print(headline)
		print(f"Värde:	{num2str(player.value)} kr")
		if player.age == 17:
			# Players over the age of 17 rarely develop at 300k/w
			print(f"300k/w: {num2str(player.value + rem_trainings * 300000)} kr")

		print(f"400k/w: {num2str(player.value + rem_trainings * 400000)} kr")
		print(f"500k/w: {num2str(player.value + rem_trainings * 500000)} kr")

		if player.age > 17:
			print(f"600k/w: {num2str(player.value + rem_trainings * 600000)} kr")

# ---------------------------------------------------------------------------------------

def print_usage() -> None:
	""" Prints usage information. Called if -h/--help flag present 
		or usage error detected. """
	
	print()
	print("Usage: python3 lhutils.py [options]")
	print("-h, --help")
	print("    Prints this information and quits.")
	print("-r, --roster")
	print("    Parse a team roster. Paste HTML into html/roster.html.")
	print("-t, --transfer")
	print("    Parse transfer list. Paste HTML into html/transfers.html.")
	print("-f, --filter LOW,MAX")
	print("    Only show players with age between (including) LOW and MAX years.")
	print("    If no age interval is provided, default values are used.")
	print(f"    Current default values: MIN = {FILTER_DEFAULT_MIN}, MAX = {FILTER_DEFAULT_MAX}")

# ---------------------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------------------

def main():
	argc: int = len(sys.argv)
	if argc < ARGC_MIN or argc > ARGC_MAX:
		print_usage()	
		exit()

	filter: bool = False
	age_min: int = FILTER_DEFAULT_MIN
	age_max: int = FILTER_DEFAULT_MAX
	args: list[str] = sys.argv[1:]
	players = list[Player]

	# Parse arguments
	for i in range(len(args)):
		if args[i] in ("-h", "--help"):
			print_usage()
			exit()
		elif args[i] in ("-r", "--roster"):
			players = parse(FILE_ROSTER, "-r")
		elif args[i] in ("-t", "--transfer"):
			players = parse(FILE_TRANSFER, "-t")
		elif args[i] in ["-f", "--filter"]:
			filter = True
			# Filter flag can be succeeded by age range (comma separated)
			# If not we just use the default values. This also applies
			# when the age range looks weird.
			if i + 1 < len(args) and re.match("\d\d,[0-9]+", args[i + 1]):
				i = i + 1
				age_min, age_max = [int(x) for x in args[i].split(',')]

		else:
			print_usage()
			exit()

	players = filter_players(players, age_min, age_max) if filter else players
	print_value_predictions(players)

# ---------------------------------------------------------------------------------------

if __name__ == "__main__":
	main()
