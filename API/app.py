import os
from flask import Flask, jsonify
import requests
import pandas as pd

# app = Flask(__name__)

# @app.route('/population/<country>', methods=['GET','POST'])
def population(country,year):
    logs_dir = os.path.join(os.getcwd(), "Logs")+f"/{country}.csv"    
    frame = pd.read_csv(logs_dir)
    print(frame)
    years = frame['Year']
    

        
    return None
    
population('india',2015)
# if __name__=="__main__":
#     app.run(debug=True)
