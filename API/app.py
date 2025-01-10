from flask import Flask

import server

app = Flask(__name__)

@app.route('/countries')
def countries():
    return 
    
if __name__=="__main__":
    app.run(debug=True)
