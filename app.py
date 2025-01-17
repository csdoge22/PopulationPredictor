from flask import Flask, jsonify
from server import load_statistic, fit_line, predict_data, get_statistic

app = Flask(__name__)

# API endpoint to retrieve the predicted population or other field for a specific year
@app.route('/predict/<country>/<col>/<year>', methods=['GET'])
def predict(country, col, year):
    try:
        year = int(year)  # Ensure year is an integer
        result = predict_data(country, col, year)
        return jsonify({"status": "success", "predicted_value": result}), 200
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid year format."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to retrieve the statistic data (e.g., population, density) for a country and column
@app.route('/statistic/<country>/<col>', methods=['GET'])
def statistic(country, col):
    try:
        result = get_statistic(country, col)
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 404
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
