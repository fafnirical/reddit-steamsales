import sys
import urllib2, json

cc = ['us', 'it', 'uk', 'au']
currency = {
	'us': '$',
	'it': u"\u20ac",
	'uk': u"\u00A3",
	'au': '$'
}
cardcheck = {
	'id': '29',
	'description':'Steam Trading Cards'
}

filename = sys.argv[1]

with open(filename, "w") as myfile:
	myfile.write('')

appids = sys.argv[2:]

def sub_get_info(table, idx1, country, idx2, subid):
	response = urllib2.urlopen('http://store.steampowered.com/api/packagedetails?packageids=' + str(subid) + '&cc='+country)
	data_orig = json.load(response)
	
	data = data_orig[str(subid)]['data']
	sub_appid = subid
	
	if('name' in data):
		table[3 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/sub/' + str(subid) + '/)'
	
	if('price' in data):
		pricedata = data['price']
		table[3 + idx2][1] = str(pricedata['discount_percent']) + '%'
		table[3 + idx2][2 + idx1] = currency[country] + str(float(pricedata['final']) / 100)
	
	if('apps' in data):
		sub_appid = data['apps'][0]['id']
	
	return (table, sub_appid)

def app_get_info(table, idx1, country, idx2, appid, data):
	if('name' in data):
		table[3 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/app/' + str(appid) + '/)'
	
	if('price_overview' in data):
		pricedata = data['price_overview']
		table[3 + idx2][1] = str(pricedata['discount_percent']) + '%'
		table[3 + idx2][2 + idx1] = currency[country] + str(float(pricedata['final']) / 100)
	
	return table

def get_table(appids): # get a table with the appIDs
	# initialize the table
	table = [['' for x in xrange(10)] for x in xrange(len(appids)+3)]
	table[0] = ['',          '',          '',          '',               '',              '',         '**Meta**',  '',             '**Trading**', '**PCGW**']
	table[1] = [':-',        '-:',        '-:',        '-:',             '-:',            '-:',       '-:',        ':-:',          ':-:',         ':-:']
	table[2] = ['**Title**', '**Disc.**', '**$USD**', u'**EUR\u20ac**', u'**\u00a3GBP**', '**$AUD**', '**score**', '**Platform**', '**Cards**',   '**Article**']
	
	appids_list = ','.join(map(str, appids))
	
	for idx1, country in enumerate(cc):
		response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + appids_list + '&cc='+country)
		data_orig = json.load(response)

		for idx2, appid in enumerate(appids):
			sub_appid = None
			
			if(data_orig[str(appid)]['success'] == False):
				(table, sub_appid) = sub_get_info(table, idx1, country, idx2, appid)
				
				appid = sub_appid
				
				response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + str(appid) + '&cc='+country)
				data_orig_new = json.load(response)
				
				data = data_orig_new[str(appid)]['data']
			else:
				data = data_orig[str(appid)]['data']
				table = app_get_info(table, idx1, country, idx2, appid, data)
			
			if(idx1 == 0):
				if('metacritic' in data):
					metacritic = data['metacritic']
					table[3 + idx2][6] = '[' + str(metacritic['score']) + '](' + metacritic['url'] + ')'
				else:
					table[3 + idx2][6] = 'N/A'
				
				if('platforms' in data):
					platforms = data['platforms']
					pl = []
					for key, value in platforms.iteritems():
						if value:
							pl.append(key.capitalize())
					table[3 + idx2][7] = '/'.join(map(str, pl))
				
				if('categories' in data):
					cards = data['categories']
					if(cardcheck in cards):
						table[3 + idx2][8] = 'Yes'
					else:
						table[3 + idx2][8] = 'No'
				
				# PCGW Article
				pcgw_response = urllib2.urlopen('http://pcgamingwiki.com/wiki/Special:Ask/-5B-5BSteam-20AppID::' + str(appid) + '-5D-5D/format%3Djson')
				try:
					pcgw_data = json.load(pcgw_response)
					if('fullurl' in pcgw_data.get('results', {}).itervalues().next()):
						table[3 + idx2][9] = '[Yes](' + pcgw_data['results'].itervalues().next()['fullurl'].replace('(', '\(').replace(')', '\)') + ')'
				except ValueError:
					table[3 + idx2][9] = 'No'
	return table

table = get_table(appids)
# print the table
for line in table:
	l = "|" + u"|".join(line).encode('utf-8').strip() + "|"
	with open(filename, "a") as myfile:
		myfile.write(l+"\n")
