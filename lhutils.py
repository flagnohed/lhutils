from bs4 import BeautifulSoup



def calc_best_lineup(opp_lineup):
	"""
	Calculates the 'best' lineup given the opponents
	lineup. The best in this case is 
	where your team's first line plays
	their worst line the most.
	"""
	pass

def predict_player_value(html_file, age):
	""" 
	Predicts the value of a player 
	at the end of the given age (after last 
	training). 	
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
	
	return {"name":name, "age":age, "pos":pos, "bday":(week, day)}		

def parse_value(td):
	return int(''.join([i for i in td.string if i.isnumeric()]))
		
			
def get_remaining_trainings(bday, curday):
	pass	

def parse_roster (html_file):
	"""
	given a roster, calculate predicted values for
	players when they reach their
	birthdays. display different scenarios 
	(200k, 300k, 400k, 500k per week)
	as well as collect average value and display
	how many weeks / number of trainings before
	birthday. this is shown when hovering (open
	that html element).
	"""
	soup = BeautifulSoup(html_file, "html.parser")
	anchors = soup.find_all('a')  # all info except value per player
	tds = soup.find_all("td", {"class":"right value"})
	# print(parse_value(tds[0]))
	""" get current lh date, and then for each player calculate stuff"""
	player = parse_anchor(anchors[0])
	player["value"] = parse_value(tds[0])	
	print(player)

def main():
	print("*** Livehockey utils ***")
	f = open("arnoroster.md")
	parse_roster(f)	


if __name__ == "__main__":
	main()

