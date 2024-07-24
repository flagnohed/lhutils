from bs4 import BeautifulSoup
import unicodedata
import sys

ROSTER_FILE = "arnoroster.html"
TRANSFER_SEARCH_FILE = "transfers.html"


def calc_best_lineup(opp_lineup):
	"""
	Calculates the 'best' lineup given the opponents
	lineup. The best in this case is 
	where your team's first line plays
	their worst line the most.
	"""
	pass


def calc_advanced_stats (game_file):
	"""
	Calculates PDO, corsi, icetime, 
	and much more (hopefully) given a game.
	Gives stats for both teams and for the respective
	players.
	"""
	pass


def get_cur_date(soup):
	cur_date_str = soup.find(id="topmenurightdateinner").get_text()
	clean_str = unicodedata.normalize("NFKD", cur_date_str)
	return [int(a) for a in clean_str.split(' ') if a.isnumeric()]


def get_num_remaining_trainings(bday, cur_date):
	""" first training inclusive if current day < 7, 
		and last training exclusive if bday < 7. """
	num_weeks = 13
	count_first = int(cur_date[1] < 7)  # training this week hasn't happened 
	dont_count_last = int(bday[1] < 7)
	return (bday[0] - cur_date[0] + count_first - dont_count_last) % 13

			
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


def predict_player_value(players, cur_date):
	""" 
	Predicts the value of a player 
	at the end of the given age (after last 
	training). 	
	""" 
	for p in players:
		rem_trainings = get_num_remaining_trainings(p["bday"], cur_date)
		name = p["name"]
		age = p["age"]
		value = p["value"]
		startbid = p["startbid"]
		print("==========")
		print(f"{name}, {age} år, {pretty_print(value)} kr")
		print(f"300k/w: {pretty_print(value + rem_trainings * 300000)} kr")
		print(f"400k/w: {pretty_print(value + rem_trainings * 400000)} kr")
		print(f"500k/w: {pretty_print(value + rem_trainings * 500000)} kr")
		print(f"Utgångsbud: {startbid}")

def parse_roster (soup):
	""" Given the HTML page of the roster, return a list
	of all players (each player is a dictionary). """
	
	def is_player_anchor(a):
		return str(a).startswith('<a href="/Pages/Player/Player.aspx?Player_Id=') \
			and '\n' in str(a)


	def parse_anchor(a):
		""" Parses an anchor (info about one player) and returns 
		it in readable format as a dictionary. """
		a = list(a.attrs.values())
		pos = a[0].split('_')[3][11:-1]		  # ucTeamSquadGoalkeepers
		rest = a[1].split('\n')
		name, age = rest[0].split(", ")	  # Felix Zetterholt, 17 år
		age = int(age[:2])
		b = rest[4].split(": ")[1].split(' ')
		week = int(b[1][:-1])
		day = int(b[3])	
		return {"name":name, "age":age, "pos":pos, "bday":[week, day]}		

	def parse_value(td):
		return int(''.join([i for i in td.string if i.isnumeric()]))

	anchors = soup.find_all('a')  # all info except value per player
	tds = soup.find_all("td", {"class":"right value"})  # value
	players = []

	# need two for-loops since anchors is larger than tds
	# parse player info
	for i in range(len(anchors)):
		if is_player_anchor(anchors[i]):
			p = parse_anchor(anchors[i])
			players += [p]
	
	# parse player value
	for i in range(len(players)):
		players[i]["value"] = parse_value(tds[i])

	return players


def parse_transfers(soup: BeautifulSoup):
	# want to add price/current bid, number in list, deadline to players
	name_age_raw = soup.find_all("div", {"class":"ts_collapsed_1"})
	players = []

	for i in range(len(name_age_raw)):
		item = name_age_raw[i]
		name = item.contents[1].text
		age = int(item.contents[3].text[:2])
		bday = [int(x) for x in item.contents[4] if x.isnumeric() and x != '0']
		if (len(bday) == 3):
			# ugly workaround for when week number is double digit
			bday = [int(str(bday[0]) + str(bday[1])), int(bday[2])]
		pos = item.contents[4].split(", ")[1]
		players += [{"name":name, "age":age, "pos":pos, "bday":bday}]
	
	value_raw = soup.find_all("div", {"class":"ts_collapsed_3"} )
	for i in range(len(value_raw)):
		val = value_raw[i]
		val_str: str = val.contents[0].replace("\xa0", "")
		num_str = ''.join([a for a in val_str if a.isnumeric()])
		players[i]["value"] = int(num_str)

	starting_bids = [x.contents[1] for x in soup.find_all("div", {"class":"ts_expanded_box2row_bottom"})]
	for i in range(len(starting_bids)):
		players[i]["startbid"] = starting_bids[i]

	return players
	
def print_usage():
	print("*** Livehockey utils ***")
	print("Usage: python3 lhutils.py [page]")
	print("[page]: roster")
	print("        transfer")



def main():

	if len(sys.argv) != 2:
		print_usage()
	
	choice = sys.argv[1]
	filename = ""

	if choice == "roster":
		filename = ROSTER_FILE
	elif choice == "transfer":
		filename = TRANSFER_SEARCH_FILE
	else:
		print_usage()
	
	file = open(filename, errors="ignore")
	soup = BeautifulSoup(file, "html.parser")
	players = []

	if filename == ROSTER_FILE:
		players = parse_roster(soup)
	elif filename == TRANSFER_SEARCH_FILE:
		players = parse_transfers(soup)
	
	cur_date = get_cur_date(soup)
	predict_player_value(players, cur_date)


if __name__ == "__main__":
	main()

