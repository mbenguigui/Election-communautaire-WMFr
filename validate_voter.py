import json, requests, sys

jfile = open('config.json')
jconfig = json.load(jfile)

headers = {
    'User-Agent': jconfig['ua'],
    'From': jconfig['email']
}

site = jconfig['site']
pages = jconfig['pages']
start_date = jconfig['start_date']
end_date = jconfig['end_date']
total_contribs = jconfig['total_contribs']
period_contribs = jconfig['period_contribs']
output = ''

if period_contribs > total_contribs:
	print('Config error: period contributions is superior to total contributions. Aborting.', file = sys.stderr)
	exit(1)

output += 'Conditions for a user to be OK:\n* have at least {} contributions before {}\n* have at least {} contributions between {} and {}\n\n'.format(total_contribs, end_date, period_contribs, start_date, end_date)

page_get = requests.get('{}/w/api.php?action=query&format=json&prop=contributors&pageids={}&pclimit=500'.format(site, '|'.join(pages)))
page_json = page_get.json()

users = []
for page in page_json['query']['pages']:
	for user in page_json['query']['pages'][page]['contributors']:
		if user['name'] not in users:
			users.append(user['name'])

for user in users:
	print('Checking user {}'.format(user))

	valid_total = False
	valid_period = False

	xtools_get = requests.get('https://xtools.wmflabs.org/api/user/globalcontribs/{}/all//{}'.format(user, end_date), headers=headers)
	xtools_json = xtools_get.json()
	user_contribs = len(xtools_json['globalcontribs'])

	if user_contribs >= period_contribs:
		valid_period = True

	if user_contribs >= total_contribs:
		valid_total = True
	elif total_contribs > 50 and not (xtools_json.get('continue') is None):
		offset = xtools_json['continue']

		while not (xtools_json.get('continue') is None):
			xtools_get = requests.get('https://xtools.wmflabs.org/api/user/globalcontribs/{}/all//{}/{}'.format(user, end_date, offset), headers=headers)
			xtools_json = xtools_get.json()
			user_contribs += len(xtools_json['globalcontribs'])

			print('user_contribs: {} | total_contribs: {}'.format(user_contribs, total_contribs))

			if user_contribs >= total_contribs:
				valid_period = True
				valid_total = True
				break

			offset = xtools_json['continue']

	if valid_total and valid_period:
		print('User {} is OK.\n'.format(user))
		output += 'User {} is OK. CentralAuth: https://meta.wikimedia.org/wiki/Special:CentralAuth/{}\n'.format(user, user.replace(' ', '_'))
	else:
		print('User {} is KO.\n'.format(user))
		output += 'User {} is KO.\n'.format(user)

ofile = open(jconfig['result_file'], 'w')
ofile.write(output)