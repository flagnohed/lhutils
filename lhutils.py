from bs4 import BeautifulSoup
import unicodedata
import sys

# -----------------------------------------------------------------------------------------
#  Filenames
FILE_ROSTER: str = "html/arnoroster.html"
FILE_TRANSFER: str = "html/transfers.html"
FILE_PLAYER: str = "html/player.html"

#  Global variables which tells us which state we are in. 
is_player: bool = False
is_roster: bool = False
is_transfer: bool = False

# Constants
MAX_WEEKS = 13
MAX_DAYS = 7

# -----------------------------------------------------------------------------------------

class Player:
	def __init__(self):
		self.age: int = 0
		self.bday: int = 0	# [1, 7]
		self.bweek: int = 0	# [1, 13]
		self.startbid: int = 0	
		self.value: int = 0
		self.name: str = ""
		self.position: str = ""  # Save pos as str for print (only thing its used for)
		
# -----------------------------------------------------------------------------------------

def get_current_date(soup: BeautifulSoup) -> list:
	#  Find the current date (in game) in the HTML file
	current_date_str = soup.find(id="topmenurightdateinner").get_text()
	#  Clean it a bit.
	clean_str = unicodedata.normalize("NFKD", current_date_str)
	#  [Week, Day]
	return [int(a) for a in clean_str.split(' ') if a.isnumeric()]

# -----------------------------------------------------------------------------------------

def get_num_remaining_trainings(bweek: int, bday: int, week: int, day: int):
	
	wdiff = (week - bweek) % 13	 # Get the difference in weeks (base amount of trainings)
	
	dose_reset: bool = day == 7		# Training reset happens Saturday 00:10 (day 7).
	last_training: bool = bday == 7	# If born day <7, will turn older before dose reset.

	return wdiff + int(last_training) - int(dose_reset)

# -----------------------------------------------------------------------------------------
			
def pretty_print(num):
	""" Takes an integer, converts it to a string.
		Makes it easier to read large numbers like
		5000000 --> 5 000 000"""
	
	rev_str = str(num)[::-1]	
	count = 0
	pretty_str = ""
	for d in rev_str:
		count += 1
		pretty_str += d
		if count == 3:
			count = 0
			pretty_str += " "
	
	return pretty_str[::-1]

# -----------------------------------------------------------------------------------------

def print_value_predictions(players: list[Player], week: int, day: int):
	""" 
	Predicts the value of a player 
	at the end of the given age (after last 
	training). 	
	""" 
	if (not players):
		print("No players found.")
		exit()

	for player in players:
		rem_trainings = get_num_remaining_trainings(player.bweek, player.bday, week, day)
		print("==========")
		print(f"{player.name}, {player.age} år, {pretty_print(player.value)} kr")
		print(f"300k/w: {pretty_print(player.value + rem_trainings * 300000)} kr")
		print(f"400k/w: {pretty_print(player.value + rem_trainings * 400000)} kr")
		print(f"500k/w: {pretty_print(player.value + rem_trainings * 500000)} kr")


# -----------------------------------------------------------------------------------------

""" Given the HTML page of the roster, return a list
	of all players. """
def parse_roster(soup: BeautifulSoup):
	
	def is_player_anchor(a):
		return str(a).startswith('<a href="/Pages/Player/Player.aspx?Player_Id=') \
			and '\n' in str(a)

	""" Parses an anchor (info about one player) and returns 
		it in readable format as a dictionary. """
	def parse_anchor(a) -> Player:
		# Black magic
		a = list(a.attrs.values())
		pos = a[0].split('_')[3][11:-1]		  # ucTeamSquadGoalkeepers
		rest = a[1].split('\n')
		name, age = rest[0].split(", ")	  # Felix Zetterholt, 17 år
		age = int(age[:2])
		b = rest[4].split(": ")[1].split(' ')
		# End of black magic
		player = Player()
		player.age = age
		player.bday = int(b[3])
		player.bweek = int(b[1][:-1])	# Dont ask
		player.name = name
		player.position = pos
		return player		

	def parse_value(td) -> int:
		return int(''.join([i for i in td.string if i.isnumeric()]))

	anchors = soup.find_all('a')  # all info except value per player
	tds = soup.find_all("td", {"class":"right value"})  # value
	players = []

	# Need two for-loops since anchors is larger than tds
	# Parse player info
	for i in range(len(anchors)):
		if is_player_anchor(anchors[i]):
			player: Player = parse_anchor(anchors[i])
			players += [player]
	
	# Parse player value
	for i in range (len(players)):
		players[i].value = parse_value(tds[i])

	return players

# -----------------------------------------------------------------------------------------

def parse_transfers(soup: BeautifulSoup):
	# want to add price/current bid, number in list, deadline to players
	name_age_raw = soup.find_all("div", {"class":"ts_collapsed_1"})
	players = []

	for item in name_age_raw:
		player: Player = Player()
		player.name = item.contents[1].text
		player.age = int(item.contents[3].text[:2])

		bdate = [int(x) for x in item.contents[4] if x.isnumeric() and x != '0']
		if (len(bdate) == 3):
			# ugly workaround for when week number is double digit
			bdate = [int(str(bdate[0]) + str(bdate[1])), int(bdate[2])]
		player.bweek, player.bday = bdate
		player.position = item.contents[4].split(", ")[1]
		
		players += [player]
	
	value_raw = soup.find_all("div", {"class":"ts_collapsed_3"} )
	for i in range(len(value_raw)):
		val_str: str = value_raw[i].contents[0].replace("\xa0", "")
		num_str = ''.join([a for a in val_str if a.isnumeric()])
		players[i].value = int(num_str)

	starting_bids = [x.contents[1] for x in soup.find_all("div", \
													{"class":"ts_expanded_box2row_bottom"})]
	for i in range(len(starting_bids)):
		players[i].startbid = starting_bids[i]

	return players

# -----------------------------------------------------------------------------------------

def print_usage(help: bool) -> None:
	header: str = "Livehockey utils" if help else "Usage error"
	print(f"******** {header} ********")
	print("Usage: python3 lhutils.py [option]")
	print("[option]: ")
	print("	-h, --help")
	print("	-p, --player")
	print("	-r, --roster")
	print("	-t, --transfer")

# -----------------------------------------------------------------------------------------

def is_flag(param: str) -> bool:
	return param in ["-h, --help, -p, --player, -r, --roster, t, --transfer"]

# -----------------------------------------------------------------------------------------

def main():
	# Check for invalid number of arguments. 
	if len(sys.argv) != 2:
		print_usage(True)	
		exit()

	#  Check if we should help the user.
	param: str = sys.argv[1]
	flag: bool = is_flag(param)
	if not flag or param == "-h" or param == "--help":
		print_usage(flag)
		exit()

	#  Determine what type of page we are working with.
	if param == "-p" or param == "--player":
		filename = FILE_PLAYER
		is_player = True
	elif param == "-r" or param == "--roster":
		filename = FILE_ROSTER
		is_roster = True
	else:
		#  Must be a transfer page.
		filename = FILE_TRANSFER 
	
	file = open(filename, errors="ignore")
	soup = BeautifulSoup(file, "html.parser")

	# Get players as a list of dicts.
	if is_player:
		print("Not implemented yet.")
		exit()
	elif is_roster:
		players = parse_roster(soup)
	else:
		players = parse_transfers(soup)

	week, day = get_current_date(soup)
	print_value_predictions(players, week, day)

# -----------------------------------------------------------------------------------------

if __name__ == "__main__":
	main()

