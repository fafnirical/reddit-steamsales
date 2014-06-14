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
			if(data_orig[str(appid)]['success'] == False):
				print 'Invalid AppID: ' + str(appid)
				continue
			data = data_orig[str(appid)]['data']

			if('price_overview' in data):
				pricedata = data['price_overview']
				table[3 + idx2][2 + idx1] = currency[country] + str(float(pricedata['final']) / 100)

			if(idx1 == 0):
				if('name' in data):
					table[3 + idx2][0] = data['name']
				
				if('price_overview' in data):
					table[3 + idx2][1] = str(pricedata['discount_percent']) + '%'
				
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
					table[3 + idx2][9] = '[Yes](' + pcgw_data['results'].itervalues().next()['fullurl'] + ')'
			except ValueError:
				table[3 + idx2][9] = 'No'
	
	# print the table
	for line in table:
		l = "|" + u"|".join(line).encode('utf-8').strip() + "|"
		with open(filename, "a") as myfile:
			myfile.write(l+"\n")

get_table(appids)
