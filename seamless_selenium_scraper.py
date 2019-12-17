from selenium import webdriver
import time
import re
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait

#open driver page for initial search - all popular restaurants in east village vicinity
driver = webdriver.Chrome()
driver.get("https://www.seamless.com/search?orderMethod=delivery&locationMode=DELIVERY&facetSet=umamiV2&pageSize=20&hideHateos=true&searchMetrics=true&latitude=40.73114395&longitude=-73.98957825&preciseLocation=true&sortSetId=umamiV2&sponsoredSize=3&countOmittingTimes=true")

#get total number of search results pages
total_pages = driver.find_element_by_xpath('//p[@class="u-text-secondary u-center"]').text
total_pages = int(total_pages.split()[-1])
total_pages

#scrape all search results pages to obtain urls for each of the 20 restaurants per page; print out progress
urls = []
index = 1
while index <=total_pages:
    print("Scraping Page Number" + str(index))
    index = index+1
    
    restaurants = driver.find_elements_by_xpath('//div[@at-restaurant-card-title="true"]/a')
    for restaurant in restaurants:
        url = restaurant.get_attribute('href')
        urls.append(url)
    
    button = driver.find_element_by_xpath('//a[@aria-label="Next"]')
    button.click()
    time.sleep(2)

##export list of urls to csv
import pandas as pd
urldf = pd.DataFrame(urls, columns =['urls'])
urldf.to_csv('./urls.csv', index=False)

#scrape 8 key variables from each restaurant page and output to pandas df
driver = webdriver.Chrome()
all_data = pd.DataFrame(columns=['name','rating', 'quality_perc','ontime_perc','accuracy_perc', 'num_ratings','price','category'])

for url in urls:
    driver.get(url)

    time.sleep(5)

    #get name variable
    try:
        name = driver.find_element_by_xpath('//h1[@itemprop="name"]').text
    except:
        continue
    
    #get rating variable
    try:
        starpix=driver.find_element_by_xpath('//ghs-stars/div').get_attribute('style')
        rating = float(re.search('-[0-9]+',starpix).group()[1:])/48+1
    except:
        continue

    #get percentages variables
    try:
        quality_perc = driver.find_elements_by_xpath('//span[@class="u-stack-y-1 ratingsFacet-percent h6"]')[0].text
        ontime_perc = driver.find_elements_by_xpath('//span[@class="u-stack-y-1 ratingsFacet-percent h6"]')[1].text
        accuracy_perc = driver.find_elements_by_xpath('//span[@class="u-stack-y-1 ratingsFacet-percent h6"]')[2].text
    except:
        continue

    #get number of ratings
    
    try:
        num_ratings = int(re.search('[0-9]+',driver.find_element_by_xpath('//span[@at-star-rating-text="true"]').text).group()) 
    except:
        continue

    #get price level
    try:
        price = len(driver.find_element_by_xpath('//div[@class="priceRating-value"]').text)
    except:
        continue

    #get cuisines category
    try:
        cuisines = driver.find_elements_by_xpath('//span[@itemprop="servesCuisine"]')
        category = [re.search('[a-zA-Z]+',cuisine.text).group() for cuisine in cuisines]
    except:
        continue

    #create dictionary containing all variables
    data = {'name': name,
            'rating': rating,
            'quality_perc': quality_perc,
            'ontime_perc': ontime_perc,
            'accuracy_perc': accuracy_perc,
            'num_ratings': num_ratings,
            'price': price,
            'category': [category]}

    df = pd.DataFrame(data)
    all_data=all_data.append(df,ignore_index=True)

#export scraped data to csv    
all_data.to_csv('./rest_data2.csv', index=False)