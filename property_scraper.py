from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import re, time, tldextract, random, csv, json
from datetime import datetime, timezone
from tqdm import tqdm
import pandas as pd

def main(url):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1366x768')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')

    # Uncomment below option, if you want chromedriver in headless mode (run in background).
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    action = ActionChains(driver)
    
    driver.get(url)

    props = WebDriverWait(driver,random.randint(30,45),ignored_exceptions=ignored_exceptions).until(ec.visibility_of_element_located((By.CSS_SELECTOR,"li.property")))
    
    #click load-more button until all properties shown
    is_stop = 0
    while is_stop == 0:
        try:
            load_more = WebDriverWait(driver,random.randint(15,30),ignored_exceptions=ignored_exceptions).until(ec.visibility_of_element_located((By.ID,"load-more")))
            action.move_to_element(load_more).perform()
            time.sleep(random.randint(3,7))
            load_more.click()
        except Exception as err:
            is_stop = 1
            # print(f"load_more error: {err}")
            break

    # count all properties available
    prop_list = driver.find_elements_by_class_name('property')
    print(len(prop_list))

    # grab properties detail available in this page, include the properties_url_detail
    prop_list_details = []
    for num in tqdm(range(len(prop_list)),ncols=75,desc="Grab property details"):
        detail = {}
        detail['scraped_date'] = datetime.now().strftime("%Y-%m-%d")
        try:
            WebDriverWait(driver,random.randint(15,30),ignored_exceptions=ignored_exceptions).until(ec.presence_of_element_located((By.CSS_SELECTOR,"h2")))
            detail['Title'] = prop_list[num].find_element_by_css_selector('h2').text
        except Exception as err:
            detail['Title'] = ""
        
        detail['Address'] = prop_list[num].find_element_by_css_selector('h6').text
        price_txt = prop_list[num].find_element_by_class_name('prop-price').text
        detail['Currency'] = price_txt[0]
        detail['Price'] = int(re.sub(r'[^0-9]+', '', price_txt))
        detail['detail_url'] = prop_list[num].find_element_by_css_selector('a').get_attribute('href')
        detail['img_url'] = prop_list[num].get_attribute('style').replace('background-image: url("','').replace('");','').strip()
        prop_list_details.append(detail)
    
    # visit each property url detail and grab other details information
    for prop in tqdm(prop_list_details,ncols=75,desc="Grab property details page"):
        driver.get(prop['detail_url'])

        #Wait until desired element visible on page
        WebDriverWait(driver,random.randint(18,45),ignored_exceptions=ignored_exceptions).until(ec.visibility_of_element_located((By.CSS_SELECTOR,"div.prop-feature")))

        # complete details: 'Property Area', 'Land Area', 'Rooms', 'Bedrooms', 'Bathrooms', 'Heating', 'Reference'.
        for spec in driver.find_elements_by_class_name('prop-feature'):
            spec_text = spec.text.split('\n')
            try:
                prop[spec_text[1]] = spec_text[0]
            except Exception as err:
                print(f"spec detail error: {err}")
        try:
            #Wait until desired element visible on page
            WebDriverWait(driver,random.randint(18,45),ignored_exceptions=ignored_exceptions).until(ec.visibility_of_element_located((By.CSS_SELECTOR,'div.mod-column-2')))
            description = driver.find_element_by_class_name('mod-column-2')
            prop['Description'] = description.text.replace('\n',' ').replace('\r',' ').strip()
        except Exception as err:
            prop['Description'] = ""

        #give delayed time before visiting next url
        time.sleep(random.randint(2,4))

    #Parsing only needed details in each property
    prop_list_details_new = []
    'scraped_date', 'Title','Address', 'Currency', 'Price', 'Property Area', 'Land Area', 'Total Area', 'Rooms', 'Bedrooms', 'Bathrooms', 'Heating', 'Reference', 'img_url', 'detail_url'

    for k1 in prop_list_details:
        new_dict = {}
        new_dict['scraped_date'] = k1['scraped_date']
        new_dict['Title'] = k1['Title']
        new_dict['Address'] = k1['Address']
        new_dict['Currency'] = k1['Currency']
        new_dict['Price'] = k1['Price']
        new_dict['detail_url'] = k1['detail_url']
        new_dict['img_url'] = k1['img_url']

        if 'Property Area' in k1: new_dict['Property Area'] = k1['Property Area']
        else: new_dict['Property Area'] = ""

        if 'Land Area' in k1: new_dict['Land Area'] = k1['Land Area']
        else: new_dict['Land Area'] = ""

        if 'Property Area' in k1: new_dict['Property Area'] = k1['Property Area']
        else: new_dict['Property Area'] = ""

        if 'Total Area' in k1: new_dict['Total Area'] = k1['Total Area']
        else: new_dict['Total Area'] = ""

        if 'Rooms' in k1: new_dict['Rooms'] = k1['Rooms']
        else: new_dict['Rooms'] = ""

        if 'Bedrooms' in k1: new_dict['Bedrooms'] = k1['Bedrooms']
        else: new_dict['Bedrooms'] = ""

        if 'Bathrooms' in k1: new_dict['Bathrooms'] = k1['Bathrooms']
        else: new_dict['Bathrooms'] = ""

        if 'Heating' in k1: new_dict['Heating'] = k1['Heating']
        else: new_dict['Heating'] = ""

        if 'Reference' in k1: new_dict['Reference'] = k1['Reference']
        else: new_dict['Reference'] = ""

        new_dict['Description'] = k1['Description']

        prop_list_details_new.append(new_dict)

    # Save all parsed property_details to JSON file with today date
    date_now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    with open(f'{date_now}_maxwellbaynes_properties.json', 'w') as fp:
        # json.dump(prop_list_details_new, fp, indent=4, ensure_ascii=False)
        json.dump(prop_list_details_new, fp, indent=4)

    # To CSV file
    df = pd.DataFrame(prop_list_details)
    columns = ['scraped_date','Title','Address','Currency','Price','Property Area','Land Area','Total Area','Rooms','Bedrooms','Bathrooms','Heating','Reference','img_url','detail_url','Description']
    # columns = ['scraped_date','Title','Address','Price','Property Area','Land Area','Total Area','Rooms','Bedrooms','Bathrooms','Heating','Reference','img_url','detail_url','Description']
    df.to_csv('maxwellbaynes_properties.csv', columns=columns,index=False, mode='a', header=False)
    
    #close the browser driver
    driver.quit()

if __name__ == '__main__':
    url = "https://maxwellbaynes.com/for-sale/?keyword=&property_subtype=&area=&sort-order=price-desc&price_min=500000&price_max=5000000&size_min=50&size_max=500&offset=12&curr_lang=en"
    main(url)