from contextlib import closing
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import json
from bs4 import BeautifulSoup
import urllib3
import numpy as np

class Outbound_Data_Collector:
    """
    convert he annotations from the LVIS eeg_annotator
    into event lists or epoch

    c = AnnotationsConverter()
    c.load_json('annotations.json')
    events = c.to_event_list()

    TODO: add to_epoch()
    """
    def __init__(self, base_url, n_pages):
        self.homepage = base_url
        self.activities = ['Backpacking', 'Bodysurfing', 'Camping', 'Chillin', 'Cycling', 'Diving', 'Fishing', 'Fitness', 'Hiking', 'Kayaking', 'Kiteboarding', 'Mountain Biking', 'Photography', 'Rafting', 'Rock Climbing', 'Running', 'Skiing', 'Snowboarding', 'Snowshoeing', 'Stand Up Paddle', 'Surfing', 'Survival', 'Swimming', 'Volunteering', 'Yoga']
        self.nearby_urls = []
        self.activity_info_list = []

        ##TODO make this dynamic
        self.n_pages = n_pages

    def collect_nearby_activities(self):
        browser = webdriver.Chrome()
        for idx in range(0,self.n_pages):
            cur_url = self.homepage + "page="+ str(idx+1)

        
            browser.get(cur_url)

            WebDriverWait(browser, timeout=20).until(lambda x: x.find_element_by_class_name("TOC-card-content"))
            content = browser.find_elements_by_class_name("TOC-card-content")
            for cont in content:
                activity_url = cont.get_attribute("href")
                self.nearby_urls += [activity_url]

        browser.close()
            #self.nearby_urls += content


    def extract_activities(self, browser):
        WebDriverWait(browser, timeout=20).until(lambda x: x.find_element_by_class_name("adventure-data-big--chip"))
        content = browser.find_elements_by_class_name("adventure-data-big--chip")
        tag_list = []
        activity_list = []
        for cont in content:
            activity = cont.get_property("innerText")
            tag_list += [activity]
            if(activity in self.activities):
                activity_list += [activity]
        return tag_list, activity_list

    def extract_location(self, browser):
        WebDriverWait(browser, timeout=6).until(lambda x: x.find_element_by_class_name("container"))
        test = browser.find_elements_by_xpath("//a[@href]")
        map_url = [elem.get_attribute("href") for elem in test if "google.com/maps" in elem.get_attribute("href")][0]
        coors = map_url.split("/")[6]
        coors = coors.split(",")
        lat = float(coors[0])
        lon = float(coors[1])
        return lat, lon

    def extract_star_rating(self, browser):
        WebDriverWait(browser, timeout=6).until(lambda x: x.find_element_by_xpath("//div[@class='pad4t']"))
        stars = browser.find_elements_by_xpath("//div[@class='pad4t']/p/i")
        rating = len(stars)
        return rating

    def extract_n_reviews(self, browser):
        WebDriverWait(browser, timeout=6).until(lambda x: x.find_element_by_class_name("adventure-box--content"))
        test = browser.find_elements_by_xpath("//div[@class='adventure-box--content']/div/div[@class='review']")
        #review_list = test.find_elements_by_xpath("//div[@class='review']")
        n_review = len(test)
        test2 = browser.find_elements_by_xpath("//div[@class='adventure-box--content']/div/div")[-1]

        if(test2.get_property('attributes')[0]['value'] == 'row pagination pad2t'):
            #Do the things to find how many pages of reviews there are
            test3 = test2.find_elements_by_xpath("//nav/span[@class='page']")
            n_review += 3*len(test3)
            hi = 0
        else:
            n_review += 0
        return n_review

    def extract_title(self, browser):
        WebDriverWait(browser, timeout=6).until(lambda x: x.find_element_by_xpath("//h1[@class = 'adventure-title m00 pad00 lh1']"))
        content = browser.find_element_by_xpath("//h1[@class = 'adventure-title m00 pad00 lh1']")
        title = content.get_property('innerText')
        return title

    def extract_adventure_info(self, url, browser):
        browser.get(url)
        title = self.extract_title(browser)
        tags, activities = self.extract_activities(browser)
        lat, lon = self.extract_location(browser)
        rating = self.extract_star_rating(browser)
        n_reviews = self.extract_n_reviews(browser)
        cur_activity = {}
        cur_activity['Title'] = title
        cur_activity['Activities'] = activities
        cur_activity['Tags'] = tags
        cur_activity['Location'] = (lat, lon)
        cur_activity['Rating'] = (rating, n_reviews)
        cur_activity['url'] = str(url)
        return cur_activity

    def extract_all_activity_info(self):
        browser = webdriver.Chrome()
        for cur_url in self.nearby_urls:
            activity_info = self.extract_adventure_info(cur_url, browser)
            self.activity_info_list += [activity_info]

        browser.close()

    def write_url_list_to_file(self, filename):      
        with open(filename, 'w') as f:
            for item in self.nearby_urls:
                f.write("%s\n" % str(item))

    def write_activity_info_to_file(self, filename):
        with open(filename, 'w') as fout:
            json.dump(self.activity_info_list, fout)



class Weather_Data_Collector:
    def __init__(self, activity_list):
        self.weather_url_list = ["https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&latitude=", "&longitude=", "&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"]
        self.activity_list = activity_list

    def get_report(self, lat, lon):
        lat = np.around(lat,decimals=3)
        lon = np.around(lon,decimals=3)
        #weather_url = self.weather_url_list[0] + str('lat') + self.weather_url_list[1] + str('lon') + self.weather_url_list[2]
        # print(str(lat))
        # print(str(lon))
        weather_url = "https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days&latitude=" + str(lat) + "&longitude=" + str(lon) + "&oneobservation=true&metric=false&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg"
        # print(weather_url)
        request = urllib3.PoolManager()
        web = request.request('GET', weather_url)
        soup = BeautifulSoup(web.data, 'html.parser')
        # print(lat)
        # print(lon)
        # print(json.loads(str(soup)))
        # print(json.loads(str(soup)).keys())
        forecast_dict=json.loads(str(soup))['forecasts']['forecastLocation']
        forecast_distance = forecast_dict['distance']

        n_forecasts = len(forecast_dict['forecast'])
        return forecast_dict['forecast']

    def add_report_to_activity(self, activity):
        location = activity["Location"]
        lat = location[0]
        lon = location[1]
        forecast = self.get_report(lat, lon)
        activity['forecast'] = forecast

    def add_all_reports(self):test3 = 'outbound_activity_info_forecasts.txt'
        for activity in self.activity_list:
            self.add_report_to_activity(activity)

    def write_activities_to_file(self, filename):
        with open(filename, 'w') as fout:
            json.dump(self.activity_list, fout)