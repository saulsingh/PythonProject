from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
DB_NAME = 'medicine_inventory.db'
RXNORM_API_URL = "https://rxnav.nlm.nih.gov/REST/drugs.json"

# --- CONFIGURATION CONSTANTS ---
# Minimum shelf life required for the pharmaceutical company to accept the drug for recycling.
MIN_SHELF_LIFE_DAYS = 180  # 6 months

# --- 1. Database Setup & Access ---

def setup_database():
    """Initializes the SQLite database table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            gtin TEXT, 
            name TEXT,              
            rxcui TEXT,             
            batch TEXT,
            expiry_date TEXT,       
            is_sealed INTEGER,      
            status TEXT             
        )
    ''')
    conn.commit()
    conn.close()

def get_inventory(status=None):
    """Fetches records, optionally filtered by status."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM inventory WHERE status=? ORDER BY expiry_date ASC', (status,))
    else:
        cursor.execute('SELECT * FROM inventory ORDER BY expiry_date ASC')
        
    records = cursor.fetchall()
    conn.close()
    return records

# --- 2. Core Decoding and API Logic ---

def extract_gs1_data(raw_barcode_string):
    """
    Simulates decoding a GS1 DataMatrix to extract Expiry Date and Batch.
    In a real system, the scanner provides this data.
    """
    # Expiry Date (AI 17) - 6 digits (YYMMDD)
    ai17_index = raw_barcode_string.find('(17)')
    expiry_date_str = raw_barcode_string[ai17_index + 4 : ai17_index + 10] if ai17_index != -1 else None

    # Batch/Lot Number (AI 10) - Variable length
    ai10_index = raw_barcode_string.find('(10)')
    if ai10_index != -1:
        # Batch runs from after '(10)' until the next AI or end of string
        batch_end = raw_barcode_string.find('(', ai10_index + 4)
        batch = raw_barcode_string[ai10_index + 4 : batch_end] if batch_end != -1 else raw_barcode_string[ai10_index + 4:]
    else:
        batch = "N/A"
    
    # GTIN/Product ID (AI 01)
    ai01_index = raw_barcode_string.find('(01)')
    gtin = raw_barcode_string[ai01_index + 4 : ai01_index + 18] if ai01_index != -1 else None

    if expiry_date_str and len(expiry_date_str) == 6:
        # Assume 21st century (e.g., 251231 -> 2025-12-31)
        full_date = '20' + expiry_date_str
        return full_date, batch, gtin
    return None, batch, gtin

def get_standardized_name(name):
    """Uses RxNorm API to standardize the medicine name."""
    try:
        response = requests.get(RXNORM_API_URL, params={"name": name})
        if response.status_code == 200:
            data = response.json()
            if 'drugGroup' in data and 'conceptGroup' in data['drugGroup']:
                drug_info = data['drugGroup']['conceptGroup'][0]['conceptProperties'][0]
                return drug_info['name'], drug_info['rxcui']
    except requests.exceptions.RequestException:
        pass  # Handle network errors silently for demo
    return name, 'N/A'

# --- 3. Flask Routes ---

@app.route('/')
def index():
    setup_database()
    return render_template('index.html')

@app.route('/scan_data', methods=['POST'])
def handle_scan():
    """Receives barcode data, processes it, and returns status."""
    data = request.get_json()
    raw_barcode = data.get('barcode', '')
    is_sealed = data.get('is_sealed', False) # True/False from frontend checkbox

    # --- Decode Barcode ---
    expiry_date_full, batch, gtin = extract_gs1_data(raw_barcode)
    
    if not expiry_date_full:
        return jsonify({"error": "Barcode invalid or Expiry Date not found (AI 17)."}), 400

    # --- Check Expiry & Standardization ---
    try:
        expiry_date = datetime.strptime(expiry_date_full, '%Y%m%d').date()
        today = datetime.now().date()
        
        # NOTE: Using a placeholder name 'SCAN_PRODUCT' since we can't search RxNorm by GTIN directly
        name, rxcui = get_standardized_name("Paracetamol") # Replace with actual logic to derive name from GTIN
        
        remaining_days = (expiry_date - today).days

        # Determine Status for DB
        if remaining_days < 0:
            status = 'expired'
        elif not is_sealed:
             # Cannot be recycled if unsealed, regardless of date
            status = 'unsealed_disposal'
        elif remaining_days >= MIN_SHELF_LIFE_DAYS:
            status = 'ready_for_recycle'
        else:
            status = 'available' # Too short shelf-life for recycling, but still usable

        # --- Save Record (Simple INSERT) ---
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (gtin, name, rxcui, batch, expiry_date, is_sealed, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (gtin, name, rxcui, batch, expiry_date_full, 1 if is_sealed else 0, status))
        conn.commit()
        conn.close()

        # --- Return Final Status to Frontend ---
        message = f"{name} (RxCUI: {rxcui}) Batch {batch}: "
        if status == 'expired':
            message += "❌ EXPIRED. Must be disposed."
        elif status == 'unsealed_disposal':
            message += "⚠️ UNSEALED. Disposal required, ineligible for recycling."
        elif status == 'ready_for_recycle':
            message += f"✅ READY FOR RECYCLING! Expires {expiry_date_full}. Meets 6-month minimum."
        else:
            message += f"⏳ VALID, but insufficient time for recycling ({remaining_days} days left)."
            
        return jsonify({
            "name": name,
            "expiry_date": expiry_date_full,
            "status": status,
            "message": message
        })

    except Exception as e:
        return jsonify({"error": f"Internal Processing Error: {str(e)}"}), 500

@app.route('/manifest')
def view_manifest():
    """Displays the list of drugs ready to be transferred back to the company."""
    
    # Only show items that are 'ready_for_recycle'
    recyclable_items = get_inventory(status='ready_for_recycle')
    
    return render_template('manifest.html', items=recyclable_items, min_days=MIN_SHELF_LIFE_DAYS)

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)