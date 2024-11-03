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
# | 17  | 4.5m | 300k			 |
# | 18  | 10m  | 400k			 |
# | 19  | 16m  | 500k			 |
# | 20  | 20m  | 500k			 |
# | 21  | 25m  | 500k			 |
# | 22  | 30m  | 500k			 |
# |-----|------|-----------------|
PVT_DICT: dict[int, tuple[int, int]] = {17: (4500000, 300000), 18: (10000000, 400000), 
										19: (15000000, 450000), 20: (20000000, 500000), 
										21: (25000000, 500000), 22: (30000000, 500000)}

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
		self.bday: int = 0	# [1, 7]
		self.bweek: int = 0	# [1, 13]
		self.startbid: int = 0	
		self.value: int = 0

		self.name: str = ""
		self.position: str = ""

		self.dev_entries: list[DevEntry] = []	 
		
	
	def write_to_json(self):
		pass

	def get_trainings_left(self) -> int:
		""" Gets the number of training occasions remaining 
			before birthday. """
		wdiff: int = (self.bweek - week) % 13
		dose_reset: bool = day == 7	
		last_training: bool = self.bday == 7		
											
		return wdiff + int(last_training) - int(dose_reset)


class DevEntry:
	def __init__(self): 
		self.date_str: str = ""

		self.value_dev: int = 0		# Value developments (400k, 270k, ...)
		self.attr_dev: int = 0		# Attribute developments (3, 4, 5, ...)
		self.attr_type: str = ""	# Attribute types (Agg, För, Mål, ...)
		self.dose: str = ""			# Training dosage (L, M, H)

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
	#  [Week: <1, 13>, Day: <1, 7>]
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

def parse_development(soup: BeautifulSoup):
	# Idea is to display value + ability change over time. 
	# This would require update every saturday 
	# (copy paste html of "träningsutveckling" into this program)

	row_entries: ResultSet[PageElement] = soup.find_all("tr", {"class":"rowMarker"})
	test = row_entries[0]

# ---------------------------------------------------------------------------------------


def parse_roster(soup: BeautifulSoup) -> list[Player]:
	
	def is_player_anchor(a: PageElement) -> bool:
		return str(a).startswith('<a href="/Pages/Player/Player.aspx?Player_Id=') \
			and '\n' in str(a)

	def parse_anchor(a: PageElement) -> Player:
		#  Black magic
		a = list(a.attrs.values())
		pos = a[0].split('_')[3][11:-1]		  # ucTeamSquadGoalkeepers
		rest = a[1].split('\n')
		name, age = rest[0].split(", ")	  # Felix Zetterholt, 17 år
		age = int(age[:2])
		b = rest[4].split(": ")[1].split(' ')
		#  End of black magic
		player = Player()
		player.age = age
		player.bday = int(b[3])
		player.bweek = int(b[1][:-1])	# Dont ask
		player.name = name
		player.position = pos
		return player		

	def parse_value(data_cell: PageElement) -> int:
		return int(''.join([i for i in data_cell.string if i.isnumeric()]))


	#  All info except value per player
	anchors: ResultSet[PageElement] = soup.find_all('a')  
	#  Value per player
	data_cells: ResultSet[PageElement] = soup.find_all("td", {"class": "right value"})
	players: list[Player] = []
	#  Need two for-loops since anchors is larger than tds
	#  Parse player info
	for i in range(len(anchors)):
		if is_player_anchor(anchors[i]):
			player: Player = parse_anchor(anchors[i])
			players += [player]
	
	# Parse player value
	for i in range (len(players)):
		players[i].value = parse_value(data_cells[i])

	return players

# ---------------------------------------------------------------------------------------

def parse_transfers(soup: BeautifulSoup) -> list[Player]:
	
	name_age_raw: ResultSet[PageElement] = soup.find_all("div", {"class":"ts_collapsed_1"})
	players: list[Player] = []

	for item in name_age_raw:
		player: Player = Player()
		player.name = item.contents[1].text
		player.age = int(item.contents[3].text[:2])

		bdate: list[int] = [int(x) for x in item.contents[4] if x.isnumeric() and x != '0']
		if (len(bdate) == 3):
			# Ugly workaround for when week number is double digit
			bdate = [int(str(bdate[0]) + str(bdate[1])), int(bdate[2])]
		player.bweek, player.bday = bdate
		player.position = item.contents[4].split(", ")[1]
		
		players += [player]
	
	value_raw: ResultSet[PageElement] = soup.find_all("div", {"class":"ts_collapsed_3"} )
	for i in range(len(value_raw)):
		val_str: str = value_raw[i].contents[0].replace("\xa0", "")
		num_str: str = ''.join([a for a in val_str if a.isnumeric()])
		players[i].value = int(num_str)

	starting_bids: list[int] = [x.contents[1] for x 
				  		in soup.find_all("div", {"class":"ts_expanded_box2row_bottom"})]
	for i in range(len(starting_bids)):
		players[i].startbid = starting_bids[i]

	return players

# ---------------------------------------------------------------------------------------

def parse(filename: str, short_flag: str) -> list[Player]:
	""" Creates the necessary objects for parsing and 
		calls the correct parser function. """

	file: TextIOWrapper = open(filename, errors="ignore")
	soup: BeautifulSoup = BeautifulSoup(file, "html.parser")
	players: list[Player] = []

	# We can trust that short_flag is a valid flag here.
	if short_flag == "-d":
		players = parse_development(soup)
	elif short_flag == "-p":
		print("Player parsing not implemented yet!")
		exit()
	elif short_flag == "-r":
		players = parse_roster(soup)
	elif short_flag == "t":
		players = parse_transfers(soup)
	else:
		print("This should not happen.")
		exit()
	
	# Parse current in-game date.
	global week
	global day
	week, day = get_current_date(soup)

	return players

# ---------------------------------------------------------------------------------------

def print_value_predictions(players: list[Player]):
	""" Predicts the value of a player at the end of 
		the given age (after last training). """ 

	if not players:
		print("No players found.")
		exit()

	for player in players:
		rem_trainings: int = player.get_trainings_left()
		print(20 * "=")
		print(f"{player.name}, {player.age} år. Värde: {num2str(player.value)} kr")
		print(f"300k/w: {num2str(player.value + rem_trainings * 300000)} kr")
		print(f"400k/w: {num2str(player.value + rem_trainings * 400000)} kr")
		print(f"500k/w: {num2str(player.value + rem_trainings * 500000)} kr")
		print(f"600k/w: {num2str(player.value + rem_trainings * 600000)} kr")

# ---------------------------------------------------------------------------------------

def print_usage(help: bool) -> None:
	""" Prints usage information. Called if -h/--help flag present 
		or usage error detected. """
	
	header: str = "Livehockey utils" if help else "Usage error"
	print(f"******** {header} ********")
	print("Usage: python3 lhutils.py [option]")
	print("[option]: ")
	print("	-h, --help")
	print("	-p, --player")
	print("	-r, --roster")
	print("	-t, --transfer")

# ---------------------------------------------------------------------------------------

""" Determines if argument PARAM is a valid flag. """
def is_flag(param: str) -> bool:
	return param in ["-h", "--help", "-p", "--player", "-r", "--roster", "-t", 
				  	 "--transfer", "-d", "--development"]

# ---------------------------------------------------------------------------------------

def main():
	# argv can be for example:
	# lhutils.py --roster
	# lhutils.py --development --filter
	# lhutils.py --transfer --filter 18,20
	argc: int = len(sys.argv)
	if argc < ARGC_MIN or argc > ARGC_MAX:
		print_usage(True)	
		exit()

	filter: bool = False
	age_min: int = FILTER_DEFAULT_MIN
	age_max: int = FILTER_DEFAULT_MAX
	args: list[str] = sys.argv[1:]
	players = list[Player]
	# Parse arguments
	for i in range(len(args)):
		if args[i] in ("-h", "--help"):
			print_usage(True)
			exit()

		if args[i] in ("-d", "--development"):
			players = parse(FILE_DEVELOPMENT, "-d")
		elif args[i] in ("-p", "--player"):
			players = parse(FILE_PLAYER, "-p")
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
			print_usage(False)
			exit()
		
	players = filter_players(players, age_min, age_max) if filter else players
	print_value_predictions(players)

# ---------------------------------------------------------------------------------------

if __name__ == "__main__":
	main()
