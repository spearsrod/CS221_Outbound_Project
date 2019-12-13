import urllib3
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time

def pull_reports():
	snow_url = 'https://www.onthesnow.com/california/skireport.html'

	browser = webdriver.Chrome()
	browser.get(snow_url)
	WebDriverWait(browser, timeout=20).until(lambda x: x.find_element_by_xpath("//td[@class = 'rLeft a resort']"))
	content = browser.find_elements_by_xpath("//table[@class = 'resortList']/tbody/tr")
	resort_dict_list = []
	for idx, resort in enumerate(content):
		resort_dict = {}
		titles = resort.find_element_by_xpath(".//div/div[@class = 'name link-light']/a")
		url = titles.get_attribute("href")
		title = titles.get_attribute("title")
		resort_dict['Name'] = title
		resort_dict['URL'] = url
		last_update = resort.find_element_by_xpath(".//div/div[@class = 'lUpdate']")
		update_text = last_update.get_attribute('innerHTML')
		date = update_text.split('>')[-2].split('<')[0].split('/')
		month = int(date[0])
		day = int(date[1])
		resort_dict['Last Update'] = str(month) + '/' + str(day)
		status = resort.find_element_by_xpath(".//td[@class = 'rMid z openstate']/div")#/div")
		colors = status.get_attribute("style").split(":")[-1].split("(")[-1].split(")")[0].split(",")
		cur_r = int(colors[0])
		if(cur_r == 255):
			resort_dict['Status'] = 'Weekend Only'
		elif(cur_r == 252):
			resort_dict['Status'] = 'Closed'
		else:
			resort_dict['Status'] = 'Open'

		new_snow = resort.find_elements_by_xpath(".//td[@class = 'rLeft b nsnow']/div/div/b")#/div")

		snow_24 = int(new_snow[0].text[:-1])
		snow_72 = int(new_snow[1].text[:-1])
		resort_dict['24 Hour Inches'] = snow_24
		resort_dict['72 Hour Inches'] = snow_72

		base_depth = resort.find_element_by_xpath(".//td[@class = 'rMid c']/div/b").text.split("\"")
		if(len(base_depth) == 1):
			lower_base_depth = 'N/A'
			upper_base_depth = 'N/A'
		elif(len(base_depth) == 2):
			lower_base_depth = base_depth[0].split("-")[0][:-1]
			upper_base_depth = base_depth[0].split("-")[0][1:]
		else:
			lower_base_depth = int(base_depth[0])
			upper_base_depth = int(base_depth[1].split(" ")[-1])
		resort_dict['Base Depth Inches'] = lower_base_depth
		resort_dict['Upper Depth Inches'] = upper_base_depth

		lifts_open = resort.find_element_by_xpath(".//td[@class = 'rMid open_lifts']/div").text#/div")
		cur_open = lifts_open.split("/")[0]
		if(len(cur_open) == 0):
			cur_open = 0
		else:
			cur_open = int(cur_open[:-1])
		total_lifts = int(lifts_open.split("/")[1][1:])
		resort_dict['Open Lifts'] = cur_open
		resort_dict['Total Lifts'] = total_lifts
		resort_dict_list += [resort_dict]

	browser.close()
	return resort_dict_list
# resort_dict_list = []
# for idx, resort in enumerate(content):
# 	resort_dict = {}
# 	titles = resort.find_element_by_xpath(".//div/div[@class = 'name link-light']/a")#/div[@class = 'name link-light']")
# 	url = titles.get_attribute("href")
# 	title = titles.get_attribute("title")
# 	resort_dict['Name'] = title
# 	resort_dict['URL'] = url
# 	last_update = resort.find_element_by_xpath(".//div/div[@class = 'lUpdate']")
# 	update_text = last_update.get_attribute('innerHTML')
# 	date = update_text.split('>')[-2].split('<')[0].split('/')
# 	month = int(date[0])
# 	day = int(date[1])
# 	resort_dict['Last Update'] = str(month) + '/' + str(day)
# 	status = resort.find_element_by_xpath(".//div/div[@class = 'name link-light']")
# 	#color_circle = status.get_attribute("style")
	
# 	WebDriverWait(browser, timeout=20).until(lambda x: x.find_element_by_xpath(".//div[@style = 'border-radius: 6px; height: 12px; width: 12px; margin: 0px 0px 0px 5px; background-color: rgb(252, 57, 46); position: absolute; display: inline-block;']"))
# 	test = status.find_element_by_xpath(".//*")
# 	print(test.get_attribute("style"))

# 	#print(color_circle)
# 	resort_dict_list += []

#content = browser.find_elements_by_xpath("//td[@class = 'rLeft a resort']")



	#print(update_text.strip())

#print(len(content))
#browser.close()
def write_report_dict(dict_list, filename):
    with open(filename, 'w') as fout:
        json.dump(dict_list, fout)


def main():
	report_dict_list = pull_reports()
	print(report_dict_list[0])
	print(len(report_dict_list))
	write_report_dict(report_dict_list, 'snow_reports.txt')
	# return
	# snow_url = 'https://www.onthesnow.com/sierra-nevada/skireport.html'
	
	# browser = webdriver.Chrome()
	# browser.get(snow_url)

	# req = urllib3.PoolManager()

	# try:
	#     res = req.request('GET', snow_url)
	#     soup = BeautifulSoup(res.data, 'html.parser')
	#     #newDictionary=json.loads(str(soup))
	#     test = soup.find_all('td', {'class' : 'rLeft a resort'})
	#     print(test)
	# except:
	#     print('Error with url:')
	#     print(weather_url)



	return

if __name__ == '__main__':
	main()