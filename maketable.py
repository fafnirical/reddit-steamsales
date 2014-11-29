import sys
import urllib2, json

#Constants
cc = ['us', 'ca', 'fr', 'it', 'uk', 'au', 'br'] #Countries to check.  Each one requires an extra lookup.
cardcheck = {
	'id': '29',
	'description':'Steam Trading Cards'
}

#Set filename and appids from arguments
filename = sys.argv[1]
appids = sys.argv[2:]

#Initially, everything is considered invalid
is_valid = [False for x in xrange(len(appids))]

def main():
	#Open output file and write empty string
	with open(filename, "w") as myfile:
		myfile.write('')

	#Issue warning on speed/requests
	print "Please wait. You're checking " + str(len(appids)) + " games with " + str(len(cc)) + " countries. Each requires a separate request so this may take a while. If you get rate-limited, try reducing the number of IDs in one query."

	#Fetch/build data
	table = get_table(appids)

	#Print output
	print table

	#Write file
	for idx, line in enumerate(table):
		#Skip line if invalid
		if (idx >= 2 and not is_valid[idx - 2]):
			continue
		l = "|" + u"|".join(line).encode('utf-8').strip() + "|"
		with open(filename, "a") as myfile:
			myfile.write(l+"\n")

#Get a table with the appIDs or subIDs
def get_table(appids):
	#Initialize the table
	table = [['' for x in xrange(12)] for x in xrange(len(appids)+2)]
	table[0] = ['**Title**', '**Disc.**', '**$USD**', '**$CAD**', u'**\u20acEUR**', u'**\u00a3GBP**', '**AU ($USD)**', '**BRL$**', '**Metascore**', '**Platform**', '**Cards**',   '**PCGW**']
	table[1] = [':-',        '-:',        '-:',       '-:',        '-:',             '-:',            '-:',            '-:',       '-:',            ':-:',          ':-:',         ':-:']

	#Loop through countries
	for idx1, country in enumerate(cc):

		#Default is that the ID refers to an app, because most IDs will be
		data_orig = {}
		for current_id in appids: #Loop through appids individually (due to Steam change), merge together into data_orig afterwards
			response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + current_id + '&cc='+country)
			data_orig_temp = json.load(response)
			data_orig = dict(data_orig.items() + data_orig_temp.items()) #Merge dicts

		for idx2, appid in enumerate(appids):
			#Skip processing if already known to be invalid

			sub_appid = None

			#If it's not an app, try it as a sub
			if (data_orig[str(appid)]['success'] == False):
				(table, sub_appid) = sub_get_info(table, idx1, country, idx2, appid)
				#appid = sub_appid
				#appid as returned by sub_get_info() appears wrong...  Commenting out.

				data_orig_new = {}
				for current_id in appids: #Loop through appids individually (due to Steam change), merge together into data_orig_new afterwards
					response = urllib2.urlopen('http://store.steampowered.com/api/appdetails?appids=' + current_id + '&cc='+country)
					data_orig_new_temp = json.load(response)
					data_orig_new = dict(data_orig_new.items() + data_orig_new_temp.items()) #Merge dicts

				if (data_orig_new[str(appid)]['success'] == True):
					data = data_orig_new[str(appid)]['data']
				else:
					data = {}
			else:
				data = data_orig[str(appid)]['data']
				table = app_get_info(table, idx1, country, idx2, appid, data)

			if (idx1 == 0):
				if ('metacritic' in data):
					metacritic = data['metacritic']
					table[2 + idx2][8] = '[' + str(metacritic['score']) + '](' + metacritic['url'] + ')'
				else:
					table[2 + idx2][8] = 'N/A'

				if ('platforms' in data):
					platforms = data['platforms']
					pl = []
					for key, value in platforms.iteritems():
						if value:
							pl.append(key.capitalize()[0])
					table[2 + idx2][9] = '/'.join(map(str, pl))

				if ('categories' in data):
					cards = data['categories']
					if (cardcheck in cards):
						table[2 + idx2][10] = 'Yes'
					else:
						table[2 + idx2][10] = 'No'

				#PCGW Article
				pcgw_response = urllib2.urlopen('http://pcgamingwiki.com/wiki/Special:Ask/-5B-5BSteam-20AppID::' + str(appid) + '-5D-5D/format%3Djson')
				try:
					pcgw_data = json.load(pcgw_response)
					if ('fullurl' in pcgw_data.get('results', {}).itervalues().next()):
						table[2 + idx2][11] = '[Yes](' + pcgw_data['results'].itervalues().next()['fullurl'].replace('(', '\(').replace(')', '\)') + ')'
				except ValueError:
					table[2 + idx2][11] = 'No'
	return table

def app_get_info(table, idx1, country, idx2, appid, data):
	if ('name' in data):
		if (is_valid[idx2] == False):
			is_valid[idx2] = 'True'
		if (table[2 + idx2][0] == ''):
			table[2 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/app/' + str(appid) + '/)'

	if ('price_overview' in data):
		pricedata = data['price_overview']
		if (table[2 + idx2][1] == ''):
			table[2 + idx2][1] = str(pricedata['discount_percent']) + '%'
		if (idx1 < 3):
			table[2 + idx2][2 + idx1] = str(float(pricedata['final']) / 100)
		#Combine EU Tiers 1 and 2 into one cell
		elif (idx1 == 3):
			#If the prices in EU Tiers 1 and 2 aren't the same, show Tier 2's price
			if ((str(float(pricedata['final']) / 100)) != table[2 + idx2][4]):
				table[2 + idx2][4] = table[2 + idx2][4] + "/" + str(float(pricedata['final']) / 100)
		elif (idx1 > 3):
			table[2 + idx2][2 + (idx1 - 1)] = str(float(pricedata['final']) / 100)

	return table

def sub_get_info(table, idx1, country, idx2, subid):
	sub_appid = subid
	response = urllib2.urlopen('http://store.steampowered.com/api/packagedetails?packageids=' + str(subid) + '&cc='+country)
	data_orig = json.load(response)

	if (data_orig[str(subid)]['success'] == False):
		print 'ID ' + str(subid) + ' invalid for region \'' + cc[idx1] + '\', marking as \'N/A\'...'
		if (idx1 < 2):
			table[2 + idx2][2 + idx1] = 'N/A'
		elif (idx1 == 2):
			if ('N/A' != table[2 + idx2][3]):
				table[2 + idx2][3] = table[2 + idx2][3] + "/" + 'N/A'
		elif (idx1 > 2):
			table[2 + idx2][2 + (idx1 - 1)] = 'N/A'
		return (table, sub_appid)

	data = data_orig[str(subid)]['data']
	if ('name' in data):
		if (is_valid[idx2] == False):
			is_valid[idx2] = 'True'
		if (table[2 + idx2][0] == ''):
			table[2 + idx2][0] = '[' + data['name'] + '](http://store.steampowered.com/sub/' + str(subid) + '/)'

	if ('price' in data):
		pricedata = data['price']
		if (table[2 + idx2][1] == ''):
			table[2 + idx2][1] = str(pricedata['discount_percent']) + '%'
		if (idx1 < 2):
			table[2 + idx2][2 + idx1] = str(float(pricedata['final']) / 100)
		elif (idx1 == 2):
			if ((str(float(pricedata['final']) / 100)) != table[2 + idx2][3]):
				table[2 + idx2][3] = table[2 + idx2][3] + "/" + str(float(pricedata['final']) / 100)
		elif (idx1 > 2):
			table[2 + idx2][2 + (idx1 - 1)] = str(float(pricedata['final']) / 100)

	#Set the appid to the first app in the sub (usually the primary app)
	if ('apps' in data):
		sub_appid = data['apps'][0]['id']

	return (table, sub_appid)

#Call main
if __name__ == '__main__':
	main()
