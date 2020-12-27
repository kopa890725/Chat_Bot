import requests, json, re
from bs4 import BeautifulSoup

def is_champion(champion_name):
	url = 'https://ddragon.leagueoflegends.com/cdn/10.25.1/data/zh_TW/champion.json'
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
  		print("Cannot get the html")
  		exit(1)
	
	r_json = r.json()
	champion_EN_name_list = []
	total_champion = 0
	champion_list = r_json['data']

	for champion in champion_list:
		champion_EN_name_list.append(champion)
		total_champion += 1

	for i in range(total_champion):
		if champion_name == r_json['data'][champion_EN_name_list[i]]['name']:
			return [True, champion_EN_name_list[i]]
	return [False, '']

def champion_statistics(champion_name):
	url = 'https://lol.garena.tw/game/champion/' + champion_name
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
  		print("Cannot get the html")
  		exit(1)

	statistics = ""
	soup = BeautifulSoup(r.text, 'html.parser')
	a = soup.find_all(class_ = 'champintro-stats__data-txt')
	for b in a:
		statistics += b.get_text().strip() + '\n'
	return statistics

def champion_ability(champion_name, ability):
	url = 'https://lol.garena.tw/game/champion/' + champion_name
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
  		print("Cannot get the html")
  		exit(1)

	if(ability.upper() == 'P'):
  		i = 0
	elif(ability.upper() == 'Q'):
  		i = 1
	elif(ability.upper() == 'W'):
  		i = 2
	elif(ability.upper() == 'E'):
  		i = 3
	elif(ability.upper() == 'R'):
  		i = 4
	else:
  		return ""
	discription = ""
	soup = BeautifulSoup(r.text, 'html.parser')
	a = soup.find_all(class_ = 'champintro-ab__item-txt')
	discription += a[i].find(class_ = 'champintro-ab__item-desc').get_text().strip() + '\n'
	discription += a[i].find(class_ = 'champintro-ab__item-intro').get_text().strip()
	return discription

def player_search(player_name):
	url = 'https://lol.moa.tw/summoner/show/' + player_name
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
  		print("Cannot get the html")
  		exit(1)

	player_info = ''

	soup = BeautifulSoup(r.text, 'html.parser')
	a = soup.find(class_ = 'label label-danger')
	if a != None:
		return "Not Found"

	a = soup.find(class_ = 'profiles').find_parents('div', limit = 1)
	for b in a:
		player_info += b.get_text().strip() + '\n'
	a = soup.find(class_ = 'dl-horizontal sub-jumbotron h3')
	even_num = False
	for b in a.children:
		if b.string.strip() == '':
			continue
		player_info += b.string.strip()
		if even_num:
			player_info += '\n'
		even_num = (not even_num)

	a = soup.find('a', href="#tabs-aggregate-10")
	player_info += '\n' + a.string + '\n' + '      '
	url = 'https://lol.moa.tw' + a.get('data-url')
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
  		print("Cannot get the html")
  		exit(1)
	soup = BeautifulSoup(r.text, 'html.parser')
	a = soup.find('h3')
	i = 0
	for child in a.children:
		if i == 5:
			player_info += child.get_text() + '\n' + '      '
		i += 1
	a = soup.find(class_ = 'table table-striped table-condensed')
	a = a.find(class_ = 'table table-striped table-condensed')
	a = a.find('tr')
	i = 0
	for td in a:
		if i == 11 or i == 13:
			player_info += td.string.strip()
		i += 1
	return player_info

if __name__ == "__main__":
	'''result = is_champion('阿卡莉')
	if result[0]:
		champion_statistics(result[1])
		print(champion_ability(result[1],"F"))'''
	print(player_search('傑啦德'))