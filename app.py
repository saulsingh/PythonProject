from flask import Flask, request, render_template, jsonify
from datetime import datetime
import requests
from barcode_db import BARCODE_DB

app = Flask(__name__)
RXNORM_API_URL = "https://rxnav.nlm.nih.gov/REST/drugs.json"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan_barcode', methods=['POST'])
def scan_barcode():
    data = request.get_json()
    barcode = data.get('barcode', '')

    # Step 1: Get medicine info from barcode database
    med_info = BARCODE_DB.get(barcode)
    if not med_info:
        return jsonify({"error": "Medicine not found"}), 404

    medicine_name = med_info['name']
    expiry_date = med_info['expiry_date']

    # Step 2: Validate medicine via RxNorm API
    response = requests.get(RXNORM_API_URL, params={"name": medicine_name})
    if response.status_code == 200:
        try:
            drug_info = response.json()['drugGroup']['conceptGroup'][0]['conceptProperties'][0]
            standardized_name = drug_info['name']
        except:
            standardized_name = medicine_name
    else:
        standardized_name = medicine_name

    # Step 3: Check expiry
    exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    today = datetime.now().date()
    status = "expired" if today > exp_date else "valid"

    return jsonify({
        "name": standardized_name,
        "expiry_date": expiry_date,
        "status": status
    })

if __name__ == '__main__':
    app.run(debug=True)
