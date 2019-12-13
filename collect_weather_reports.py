import json
import numpy as np
import urllib3
from bs4 import BeautifulSoup
from socket import timeout

test3 = 'outbound_activity_info_forecasts.txt'

with open('outbound_activity_info.txt') as json_file:
    data = json.load(json_file)
    print(len(data))
    for idx, activity in enumerate(data):
    	if(np.mod(idx,50) == 0):
    		print(idx)
    	# if(idx > 0):
    	# 	break
    	location = activity['Location']
    	lat = np.around(location[0],3)
    	lon = np.around(location[1],3)
    	weather_url = "https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&latitude=" + str(lat) + "&longitude=" + str(lon) + "&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"

    	#weather_url = "/weather/1.0/report.json?product=forecast_7days&latitude=39.142&longitude=-120.229&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"
    	req = urllib3.PoolManager()

    	try:
    	    res = req.request('GET', weather_url)
    	except:
    	    print('Error with url:')
    	    print(weather_url)
    	    continue
    	# except timeout:
    	#     logging.error('socket timed out - URL %s', url)
    	# else:
    	#res = req.request('GET', weather_url)

    	soup = BeautifulSoup(res.data, 'html.parser')

    	newDictionary=json.loads(str(soup))['forecasts']['forecastLocation']
    	forcast_distance = newDictionary['distance']

    	n_forecasts = len(newDictionary['forecast'])
    	forecasts  = newDictionary['forecast']
    	activity['Forecast'] = forecasts
    with open(test3, 'w') as fout:
    	json.dump(data, fout)

