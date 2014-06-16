import sys
import urllib2, json

cc = ['us', 'fr', 'it', 'uk', 'au']
currency = {
	'us': '$',
	'fr': u"\u20ac",
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

# initially, everything is valid
is_invalid = [False for x in xrange(len(appids))]

def sub_get_info(table, idx1, country, idx2, subid):
	response = urllib2.urlopen('http://store.steampowered.com/api/packagedetails?packageids=' + str(subid) + '&cc='+country)
	data_orig = json.load(response)
	if(data_orig[str(subid)]['success'] == False):
		print 'Invalid ID: ' + str(subid) + ', skipping...'
		is_invalid[idx2] = True
		return (table, subid)
	
	data = data_orig[str(subid)]['data']
	sub_appid = subid
	if(idx1 == 0):
		if('name' in data):
			table[3 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/sub/' + str(subid) + '/)'
		if('price' in data):
			pricedata = data['price']
			table[3 + idx2][1] = str(pricedata['discount_percent']) + '%'
	
	if('price' in data):
		pricedata = data['price']
		if(idx1 < 2):
			table[3 + idx2][2 + idx1] = currency[country] + str(float(pricedata['final']) / 100)
		elif(idx1 == 2):
			if((currency[country] + str(float(pricedata['final']) / 100)) != table[3 + idx2][3]):
				table[3 + idx2][3] = table[3 + idx2][3] + "/" + currency[country] + str(float(pricedata['final']) / 100)
		elif(idx1 > 2):
			table[3 + idx2][2 + (idx1 - 1)] = currency[country] + str(float(pricedata['final']) / 100)
	
	if('apps' in data):
		sub_appid = data['apps'][0]['id']
	
	return (table, sub_appid)

def app_get_info(table, idx1, country, idx2, appid, data):
	if(idx1 == 0):
		if('name' in data):
			table[3 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/app/' + str(appid) + '/)'
		if('price_overview' in data):
			pricedata = data['price_overview']
			table[3 + idx2][1] = str(pricedata['discount_percent']) + '%'
	
	if('price_overview' in data):
		pricedata = data['price_overview']
		if(idx1 < 2):
			table[3 + idx2][2 + idx1] = currency[country] + str(float(pricedata['final']) / 100)
		# combine EU Tiers 1 and 2 into one cell
		elif(idx1 == 2):
			# if the prices in EU Tiers 1 and 2 aren't the same, show Tier 2's price
			if((currency[country] + str(float(pricedata['final']) / 100)) != table[3 + idx2][3]):
				table[3 + idx2][3] = table[3 + idx2][3] + "/" + currency[country] + str(float(pricedata['final']) / 100)
		elif(idx1 > 2):
			table[3 + idx2][2 + (idx1 - 1)] = currency[country] + str(float(pricedata['final']) / 100)
	
	return table

def get_table(appids): # get a table with the appIDs or subIDs
	# initialize the table
	table = [['' for x in xrange(10)] for x in xrange(len(appids)+3)]
	table[0] = ['',          '',          '',          '',               '',              '',         '**Meta**',  '',             '**Trading**', '**PCGW**']
	table[1] = [':-',        '-:',        '-:',        '-:',             '-:',            '-:',       '-:',        ':-:',          ':-:',         ':-:']
	table[2] = ['**Title**', '**Disc.**', '**$USD**', u'**EUR\u20ac**', u'**\u00a3GBP**', '**$AUD**', '**score**', '**Platform**', '**Cards**',   '**Article**']
	
	appids_list = ','.join(map(str, appids))
	
	for idx1, country in enumerate(cc):
		# default is that the ID refers to an app, because most IDs will be
		response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + appids_list + '&cc='+country)
		data_orig = json.load(response)

		for idx2, appid in enumerate(appids):
			# skip processing if already known to be invalid
			if(is_invalid[idx2]):
				continue
			
			sub_appid = None
			
			# if it's not an app, try it as a sub
			if(data_orig[str(appid)]['success'] == False):
				(table, sub_appid) = sub_get_info(table, idx1, country, idx2, appid)
				
				# if the sub isn't invalid, get info from the main app in the sub
				if(not is_invalid[idx2]):
					appid = sub_appid
					
					response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + str(appid) + '&cc='+country)
					data_orig_new = json.load(response)
					
					data = data_orig_new[str(appid)]['data']
			else:
				data = data_orig[str(appid)]['data']
				table = app_get_info(table, idx1, country, idx2, appid, data)
			
			if(idx1 == 0 and not is_invalid[idx2]):
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
for idx, line in enumerate(table):
	# skip line if invalid
	if(idx >= 3 and is_invalid[idx - 3]):
		continue
	l = "|" + u"|".join(line).encode('utf-8').strip() + "|"
	with open(filename, "a") as myfile:
		myfile.write(l+"\n")
