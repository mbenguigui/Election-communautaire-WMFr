import json, requests, os

jfile = open('config.json')
jconfig = json.load(jfile)

users = jconfig['users']
start_date = jconfig['start_date']
end_date = jconfig['end_date']
total_contribs = jconfig['total_contribs']
period_contribs = jconfig['period_contribs']
ofile = open(jconfig['result_file'])

for user in users:
	xtools_json = requests.get('https://xtools.wmflabs.org/api/user/globalcontribs/{}/all//{}'.format(user, end_date))

	global_contribs = xtools_json['globalcontribs']
	print(global_contribs)