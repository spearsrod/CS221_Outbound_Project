from contextlib import closing
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import json
from bs4 import BeautifulSoup
import urllib3
import numpy as np

def find_all_surf_activities(act_list):
	surf_activites = [act for act in act_list if 'Surfing' in act['Activities']]
	count = 0
	# for act in act_list:
	# 	if('Surfing' in act['Activities']):
	# 		count += 1
	# 		print(act['Title'])
			#print(act['Location'])
		#print(act['Activities'])
	return surf_activites

def load_activities(file):
	data = []
	with open(file) as json_file:
	    data = json.load(json_file)
	    data = data[:]
	return data

def extract_msw_california_urls():
	site_map_url = 'https://magicseaweed.com/site-map.php'
	url_base = 'https://magicseaweed.com'
	CAL_REGIONS = ['Orange County Surf Reports', 'Los Angeles County Surf Reports', 'Northern California Surf Reports', 'San Diego County Surf Reports',' Ventura County Surf Reports', 'Santa Barbara County Surf Reports', 'Central California Surf Reports']
	req = urllib3.PoolManager()
	res = req.request('GET', site_map_url)

	soup = BeautifulSoup(res.data, 'html.parser')
	test = soup.find_all('h1', {'class' : 'header'})
	desired_regions = [node for node in test if node.contents[0] in CAL_REGIONS]
	all_urls = []
	for region in desired_regions:
		sub_node = region.nextSibling
		cur_urls = [url_base + cur['href'] for cur in sub_node.find_all('a', href=True)]
		all_urls += cur_urls
	return all_urls

def save_all_surf_urls(url_list, filename):
	with open(filename, 'w') as f:
	    for item in url_list:
	        f.write("%s\n" % str(item))

def load_surf_urls(filename):
	#with open(filename) as json_file:
	data = [line.rstrip('\n') for line in open(filename)]
	    #data = json.load(json_file)
	return data

def extract_report(spot_url):
	req = urllib3.PoolManager()
	res = req.request('GET', spot_url)
	soup = BeautifulSoup(res.data, 'html.parser')
	#test = soup.find_all('h1', {'class' : 'header'})
	test = soup.find('table', {'class' : 'table table-primary table-forecast allSwellsActive msw-js-table'})
	day_forecasts = test.find_all('tbody')#, {'class' : 'tbody-title'})
	swell_forecast = {}
	for idx, day in enumerate(day_forecasts):
		day_forecast = {}
		day_ratings = day.find_all('ul', {'class' : 'rating clearfix'})
		#extract only hours 6AM to 6PM
		daylight_ratings = day_ratings[2:-1]
		n_daylight_sections = len(daylight_ratings)*1.0
		star_sum = 0
		max_day = 0
		min_day = 5
		for rating in daylight_ratings:
			n_active = rating.find_all('li' , {'class' : 'active'})
			n_stars = len(n_active)
			if(n_stars > max_day):
				max_day = n_stars
			if(n_stars < min_day):
				min_day = n_stars
			star_sum += n_stars
		day_forecast['avg rating'] = star_sum/n_daylight_sections
		day_forecast['max rating'] = max_day
		day_forecast['min rating'] = min_day
		swell_forecast[idx] = day_forecast
	return swell_forecast

def extract_all_reports(url_list):
	all_forecasts = []
	for idx, spot in enumerate(url_list):
		if(np.mod(idx, 5) == 0):
			print('done ' + str(idx + 1) +  ' of ' + str(len(url_list)))
		spot_forecast = extract_report(spot)
		all_forecasts += [spot_forecast]
	return all_forecasts

def get_outbound_locations(url_list, surf_acts):
	matches = 0
	n_acts = 20
	for act in surf_acts[:n_acts]:
		cur_matches = 0
		cur_list = []
		print(act['Title'])
		print(act['Title'].split(' '))
		for cur_url in url_list:
			spot_title = cur_url.split('/')[3]
			spot_words = spot_title.split('-')[:-2]
			#print(spot_words)
			for word in spot_words:
				if(word in act['Title'].split(' ') and word != 'Park' and word != 'Cove' and word != 'The' and word != 'Point' and word != 'Beach' and word != 'Surf' and word != 'State' and word != 'St'):
					matches += 1
					cur_matches += 1
					cur_list += [spot_words]

		if(cur_matches < 1):
			print('No Matches:')
			print(cur_list)
					# print('Match Found')
					# print('total matches')
					# print(matches)
					# print('current matchs')
					# print(cur_matches)
					# print(spot_words)
					# print(word)
					# print(act['Title'])



def main():
	filename = 'outbound_activity_info_forecasts.txt'
	activity_data = load_activities(filename)
	surf_activities = find_all_surf_activities(activity_data)
	# data_urls = extract_msw_california_urls()
	# save_all_surf_urls(data_urls, 'msw_test1.txt')
	reloaded_urls = load_surf_urls('msw_test1.txt')
	# all_forecasts = extract_all_reports(reloaded_urls)
	# print(all_forecasts[:5])
	#print(reloaded_urls)
	get_outbound_locations(reloaded_urls, surf_activities)

main()