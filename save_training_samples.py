import numpy as np 
import random
from bs4 import BeautifulSoup
import urllib3
import json
import ast
activity_list = ['Backpacking', 'Bodysurfing', 'Camping', 'Chillin', 'Cycling', 'Diving', 'Fishing', 'Fitness', 'Hiking', 'Kayaking', 'Kiteboarding', 'Mountain Biking', 'Photography', 'Rafting', 'Rock Climbing', 'Running', 'Skiing', 'Snowboarding', 'Snowshoeing', 'Stand Up Paddle', 'Surfing', 'Survival', 'Swimming', 'Volunteering', 'Yoga']

def pull_random_geo():
	lat_min = -90
	lat_max = 90
	lon_min = -180
	lon_max = 180
	lat_val = random.uniform(lat_min, lat_max)
	lon_val = random.uniform(lon_min, lon_max)
	return (lat_val, lon_val)


def prettify_forecast(forecast):
	pretty_forecast = {}
	pretty_forecast['DOW'] = forecast['weekday']
	pretty_forecast['TOD'] = forecast['daySegment']
	pretty_forecast['Sky'] = forecast['iconName']
	pretty_forecast['Temp'] = forecast['temperature']
	pretty_forecast['P_prob'] = forecast['precipitationProbability']
	pretty_forecast['Rain'] = forecast['rainFall']
	pretty_forecast['Snow'] = forecast['snowFall']
	pretty_forecast['Wind'] = str(forecast['windSpeed']) + ' ' + forecast['windDescShort']
	pretty_forecast['Hum'] = forecast['humidity']
	pretty_forecast['Vis'] = forecast['visibility']
	pretty_forecast['Comfort'] = forecast['comfort']
	pretty_forecast['Air Info'] = forecast['airInfo']
	return pretty_forecast


def pull_weather_report(geo):
	lat = np.around(geo[0],3)
	lon = np.around(geo[1],3)
	weather_url = "https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&latitude=" + str(lat) + "&longitude=" + str(lon) + "&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"

	#weather_url = "/weather/1.0/report.json?product=forecast_7days&latitude=39.142&longitude=-120.229&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"
	req = urllib3.PoolManager()

	try:
	    res = req.request('GET', weather_url)
	except:
	    print('Error with url:')
	    print(weather_url)
	    return None



	soup = BeautifulSoup(res.data, 'html.parser')
	if(str(soup) == ''):
		print('Error reading report')
		return None	
	newDictionary=json.loads(str(soup))['forecasts']['forecastLocation']
	afternoon_forecasts = [cast for cast in newDictionary['forecast'] if cast['daySegment'] == 'Afternoon']
	random_forecast = random.choice(afternoon_forecasts)
	return random_forecast

def run_data_collection(activity):
	test_geo = pull_random_geo()
	forecast = pull_weather_report(test_geo)
	if(forecast != None):
		print('Activity:')
		print(activity)
		print(prettify_forecast(forecast))
		print('Your Score [-10 <-> 10]:')
		y = -1
		while(True):
			y_raw = input()
			try:
				y = float(y_raw)
				if(y >= -10 and y <= 10):
					break
				else:
					print('Enter value within range')
			except:
				print('Not a valid input, try again')
		return y, forecast
	else:
		print('failed forecast pull, trying again')
		return None, None

class ForecastDataset():
	def __init__(self, filename=None):
		self.filename = filename
		if self.filename:
			self.data_dict = self.read_data_file(self.filename)
		else:
			self.data_dict = {}
			for act in activity_list:
				self.data_dict[act] = []

	def read_data_file(self, filename):
		data = []
		with open(filename) as json_file:
		    data = json.load(json_file)
		return data[0]

	def write_data_file(self, filename):
		data_list = [self.data_dict]
		with open(filename, 'w') as fout:
			json.dump(data_list, fout)

	def add_datapoint(self, activity, forecast, y):
		cur_dict = {}
		cur_dict[str(forecast)] = y
		self.data_dict[activity] += [cur_dict]

	def get_item(self, activity, idx):
		act_list = self.data_dict[activity]
		sample = act_list[idx]
		k = list(sample.keys())[0]
		y = sample[k]
		forecast = ast.literal_eval(k)
		return forecast, y

	def get_act_length(self, activity):
		return len(self.data_dict[activity])

	def get_n_activities(self):
		return len(self.data_dict.keys())

data_type = ['train', 'test', 'validate']

def main():
	print('select data log type')
	print(data_type)
	while(True):
		dat = input()
		if(isinstance(dat, str) and dat in data_type):
			break
		else:
			print('try again')
	print('select_training_activity')
	print(activity_list)
	while(True):
		act = input()
		if(isinstance(act, str) and act in activity_list):
			break
		else:
			print('try again')

	data_file = dat + '_data.txt'
	#data_file = 'train_data.txt'
	loaded = 0
	try:
		print('loading old dataset')
		dataset = ForecastDataset(data_file)
		loaded = 1
		#new_data = dataset.read_data_file(data_file)
	except:
		print('old dataset not found')
		print('creating new dataset')
		print(data_file)
		dataset = ForecastDataset()
	# if(loaded):
	# 	print(dataset.get_item(act, 0))
	# 	print(dataset.get_act_length(act))
	# return


	# data_len = dataset.get_length()
	# for idx in range(data_len):
	# 	print(dataset[idx])
	# return 

	counter = 0
	save_frequency = 5

	while(True):
		y, forecast = run_data_collection(act)
		if(y == None):
			continue
		counter += 1
		print('Points until save:')
		print(save_frequency - np.mod(counter,save_frequency))
		dataset.add_datapoint(act, forecast, y)
		if(np.mod(counter, save_frequency) == 0):
			dataset.write_data_file(data_file)

if __name__ == '__main__':
	main()