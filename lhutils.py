from bs4 import BeautifulSoup
import unicodedata


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

def parse_transfers_near_deadline (html_file, age):
	pass






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
		
			
def is_player_anchor(a):
	return str(a).startswith('<a href="/Pages/Player/Player.aspx?Player_Id=') \
		and '\n' in str(a)


def get_cur_date(soup):
	cur_date_str = soup.find(id="topmenurightdateinner").get_text()
	clean_str = unicodedata.normalize("NFKD", cur_date_str)
	return [int(a) for a in clean_str.split(' ') if a.isnumeric()]


def parse_roster (soup):
	""" Given the HTML page of the roster, return a list
	of all players (each player is a dictionary). """
	
	anchors = soup.find_all('a')  # all info except value per player
	tds = soup.find_all("td", {"class":"right value"})  # value
	players = []

	# parse player info
	for i in range(len(anchors)):
		if is_player_anchor(anchors[i]):
			p = parse_anchor(anchors[i])
			players += [p]
	
	# parse player value
	for i in range(len(players)):
		players[i]["value"] = parse_value(tds[i])

	return players


def get_num_remaining_trainings(bday, cur_date):
	""" first training inclusive if current day < 7, 
		and last training exclusive if bday < 7. """
	num_weeks = 13
	count_first = int(cur_date[1] < 7)  # training this week hasn't happened 
	dont_count_last = int(bday[1] < 7)

	return (bday[0] - cur_date[0] + count_first - dont_count_last) % 13



			


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
		print("==========")
		print(f"{name}, {age}")
		print(f"300k/w: {value + rem_trainings * 300000}")
		print(f"400k/w: {value + rem_trainings * 400000}")
		print(f"500k/w: {value + rem_trainings * 500000}")
		print("==========")



def main():
	print("*** Livehockey utils ***")
	f = open("arnoroster.md")
	soup = BeautifulSoup(f, "html.parser")

	players = parse_roster(soup)	
	cur_date = get_cur_date(soup)
	
	predict_player_value(players, cur_date)




if __name__ == "__main__":
	main()

