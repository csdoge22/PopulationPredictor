# for processing/scraping data 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


import schedule
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

global g_col_names
g_col_names = []

def load_countries(driver) -> list:    
    url = "https://www.worldometers.info/world-population/population-by-country/"
    driver.get(url)
    country_elements = driver.find_elements(by='xpath',value="//td[@style='font-weight: bold; font-size:15px; text-align:left']")
    countries = []
    for element in country_elements:
        countries.append(element.text)
    for i in range(len(countries)):
        # replace all space tokens with hyphens
        countries[i] = countries[i].replace(" ","-").replace("&","and").replace("u.s.","us").lower()
        # we want to remove all parenthesis and the content inside it
        try:
            index_open = countries[i].index('(')
            index_close = countries[i].index(')')
        except ValueError as e:
            index_open = -1
            index_close = -1
        finally:
        # check to see if there are opening and closing parenthesis in the country name
            paren_phrase = ''
            if index_open!=-1 and index_close!=-1:
                paren_phrase = countries[i][index_open:index_close+1]
            countries[i] = countries[i].replace(paren_phrase,"")
            if countries[i]=="czech-republic-":
                countries[i] = "czech-republic"
            if countries[i]=="dr-congo":
                countries[i]=="democratic-republic-of-the-congo"
            if countries[i]=="st.-vincent-and-grenadines":
                countries[i] = "saint-vincent-and-the-grenadines"
            if countries[i]=="côte-d'ivoire":
                countries[i] = "cote-d-ivoire"
            if countries[i]=="réunion":
                countries[i] = "reunion"
                
    return countries

def load_statistic(country,driver):
    try:
        # Create Logs directory if it doesn't exist
        logs_dir = os.path.join(os.getcwd(), "Logs")
        os.makedirs(logs_dir, exist_ok=True)

        # File paths
        csv_file = os.path.join(logs_dir, f"{country}.csv")
        json_file = os.path.join(logs_dir, f"{country}.json")

        # URL to scrape
        sub_url = f"https://www.worldometers.info/world-population/{country}-population/"
        driver.get(sub_url)

        # Initialize stats dictionary
        stats = dict()

        # Extract column names
        column_elements = driver.find_elements(by="xpath", value="//table[@class='table table-striped table-bordered table-hover table-condensed table-list']//th")
        column_names = [col.text for col in column_elements[:len(column_elements)//2]]
        for i in range(len(column_names)):
            stats[column_names[i]] = []
            g_col_names.append(column_names[1])

        # Extract table data
        table_data = driver.find_elements(by="xpath", value="//table[@class='table table-striped table-bordered table-hover table-condensed table-list']//tr//td")
        for i, cell in enumerate(table_data):
            text = cell.text.strip()
            if text == '' or text == 'N.A.':
                value = np.nan
            else:
                value = float(text.replace("%", "").replace(",", "").replace(" ", ""))
            stats[column_names[i % len(column_names)]].append(value)

        # Create DataFrame
        frame = pd.DataFrame(stats)
        frame = frame.interpolate()

        # Convert percent change columns to growth factors
        percent_change_columns = [col for col in column_names if "Change" in col]  # Example dynamic detection
        for col_name in percent_change_columns:
            frame[col_name] = 1 + (frame[col_name] / 100.0)

        # Convert specific columns to integers
        int_columns = [col for col in column_names if col=="Year" or col=="Population"]  # Example dynamic detection
        for col_name in int_columns:
            frame[col_name] = frame[col_name].astype(int)
        print(frame)
        # Save to CSV
        frame.to_csv(csv_file, index=False)

        # Save to JSON
        frame.to_json(json_file, orient="records")

        return {"message": f"Data for {country} saved successfully.", "csv": csv_file, "json": json_file}
    except NoSuchElementException as e:
        return {"error": "Data extraction failed. Check website structure.", "details": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred.", "details": str(e)}

def job():
    """ Schedule to get all statistics """
    print("Scraping Country Data")
    # I specifically chose Firefox because it is cross-compatible through Windows, Mac, and Linux
    driver = webdriver.Firefox()
    countries = load_countries(driver=driver)
    for i in range(len(countries)):
        print(load_statistic(country=countries[i],driver=driver))
        print('\n')
    driver.quit()
    
def index(aset):
    names = ['year','population','yearly\n%\nchange','yearly change']
    return -1
    
def predict(country,year,chosen_set):
    """ This method uses linear regression to estimate/identify population, fertility rate, net migration, etc... for years not listed"""
    logs_dir = os.path.join(os.getcwd(), "Logs")
    country_url = os.path()
    try:
        frame = pd.read_csv(f"../Logs/{country}.csv")
        x = frame[0]
        y = frame[chosen_set]
        
        plt.scatter(x,y)
        
    except FileNotFoundError as e:
        print("Warning: File Not Found")

""" Testing Area """
driver = webdriver.Firefox()
print(load_statistic('martinique',driver))
# job()

# Scrapes data every day at midnight
""" schedule.every().days.do(job_func=job)
while True:
    schedule.run_pending() """