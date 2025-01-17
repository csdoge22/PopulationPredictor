import os
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

COLUMN_MAPPINGS = {
    "Year": "Year",
    "Population": "Population",
    "Yearly %\nChange": "Yearly Percentage Change",
    "Yearly\nChange": "Yearly Change",
    "Migrants (net)": "Migrants (net)",
    "Median Age": "Median Age",
    "Fertility Rate": "Fertility Rate",
    "Density (P/Km²)": "Density",
    "Urban\nPop %": "Urban Population Percentage",
    "Urban Population": "Urban Population",
    "Country's Share of\nWorld Pop": "Country's Share of World Population",
    "World Population": "World Population",
    "Global Rank": "Global Rank"
}

# Function to load countries
def load_countries() -> list:
    driver = webdriver.Firefox()
    logs_dir = os.path.join(os.getcwd(), "Logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    url = "https://www.worldometers.info/world-population/population-by-country/"
    driver.get(url)
    country_elements = driver.find_elements(by='xpath', value="//td[@style='font-weight: bold; font-size:15px; text-align:left']")
    countries = [element.text for element in country_elements]
    driver.quit()
    return countries

# Function to load statistics for a given country
def load_statistic(country):

    print("MAPPINGS:",COLUMN_MAPPINGS)
    try:
        driver = webdriver.Firefox()
        logs_dir = os.path.join(os.getcwd(), "Logs")
        os.makedirs(logs_dir, exist_ok=True)

        csv_file = os.path.join(logs_dir, f"{country}.csv")
        json_file = os.path.join(logs_dir, f"{country}.json")
        
        sub_url = f"https://www.worldometers.info/world-population/{country}-population/"
        driver.get(sub_url)

        stats = dict()
        column_elements = driver.find_elements(by="xpath", value="//table[@class='table table-striped table-bordered table-hover table-condensed table-list']//th")[:14]
        print("LENGTH:",len(column_elements))
        
        column_names = []
        for i in range(len(column_elements)-2):
            print("ELMT:",column_elements[i].text)
            column_names.append(COLUMN_MAPPINGS.get(column_elements[i].text))
        column_names.append(COLUMN_MAPPINGS.get("Global Rank"))
        print(column_names)
        print(len(column_names))
        for col_name in column_names:
            stats[col_name] = []

        table_data = driver.find_elements(by="xpath", value="//table[@class='table table-striped table-bordered table-hover table-condensed table-list']//tr//td")
        for i, cell in enumerate(table_data):
            text = cell.text.strip()
            value = float(text.replace("%", "").replace(",", "").replace(" ", "")) if text != '' and text != 'N.A.' else np.nan
            stats[column_names[i % len(column_names)]].append(value)
        
        len_stats = dict()
        for entry in stats:
            len_stats[entry] = len(stats[entry])
        print(stats)
        frame = pd.DataFrame(stats)
        frame = frame.interpolate()

        # Convert percent change columns to growth factors
        percent_change_columns = [col for col in column_names if "Change" in col]  # Example dynamic detection
        for col_name in percent_change_columns:
            frame[col_name] = 1 + (frame[col_name] / 100.0)

        # Convert specific columns to integers
        int_columns = [col for col in column_names if col=="Year" or col=="Population" or col=="World Population" or col=="Global Rank"]  # Example dynamic detection
        for col_name in int_columns:
            frame[col_name] = frame[col_name].astype(int)
        
        print(frame)
        # Save to CSV

        frame.to_csv(csv_file, index=False)
        frame.to_json(json_file, orient="records")
        
        driver.quit()
        return {"message": f"Data for {country} saved successfully.", "csv": csv_file}
    except NoSuchElementException as e:
        return {"error": "Data extraction failed. Check website structure.", "details": str(e)}
    except Exception as e:
        return {"error": "An unexpected error occurred.", "details": str(e)}

# Function to calculate line of best fit for a given country and column
def fit_line(country: str, year: int, col: str):
    logs_dir = os.path.join(os.getcwd(), "Logs", f"{country}.csv")
    frame = pd.read_csv(logs_dir)
    
    x = np.array(frame['Year'])
    y = np.array(frame[col])

    slope, intercept, r, p, std_err = stats.linregress(x, y)

    # Generate the model
    my_model = list(map(lambda y: slope * y + intercept, x))

    # Create plot
    plt.scatter(x, y)
    plt.plot(x, my_model, color='red')
    plt.title(f"Yearly {col} of {country}")
    plt.xlabel("Year")
    plt.ylabel(col)
    plt.savefig(f"{country}_{col}_fit.png")
    plt.close()

    return {"slope": slope, "intercept": intercept}

# Function to predict data for a given year
def predict_data(country: str, col: str, year: int):
    line_of_best_fit = fit_line(country, col)
    slope = line_of_best_fit["slope"]
    intercept = line_of_best_fit["intercept"]

    prediction = slope * year + intercept
    return max(0, prediction)  # Ensure the prediction is not negative

# Function to retrieve a statistic based on a field (column)
def get_statistic(country: str, col: str):
    logs_dir = os.path.join(os.getcwd(), "Logs", f"{country}.csv")
    if not os.path.exists(logs_dir):
        return {"error": f"No data available for {country}"}

    frame = pd.read_csv(logs_dir)
    if col not in frame.columns:
        return {"error": f"Column '{col}' not found for {country}"}

    data = frame[col].dropna().tolist()  # Remove NaN values
    return {"country": country, "column": col, "data": data}

print(load_statistic('india'))