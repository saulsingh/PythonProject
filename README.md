# 💊 Medicine Validator with API Detection

A Flask-based web application that validates medicine barcodes using real-time API detection from OpenFDA, RxNorm, and product databases.

## 🌟 Features

### Real-Time API Integration
- **OpenFoodFacts API** - Global product barcode lookup
- **OpenFDA API** - FDA drug database verification
- **RxNorm API** - NIH medicine validation
- **UPC Database** - Alternative product lookup

### Key Capabilities
- 📷 **Live barcode scanning** using device camera
- 🔍 **Medicine name search** across multiple databases
- 📅 **Expiry date validation** with color-coded alerts
- ✅ **Multi-source verification** for authenticity
- 📱 **Responsive design** - works on all devices
- 🎨 **Beautiful UI** with real-time updates

---

## 📁 Project Structure

```
medicine-validator/
│
├── app.py                      # Flask backend with API integration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── templates/
│   └── index.html             # Frontend HTML
│
└── static/
    ├── style.css              # CSS styling
    └── script.js              # JavaScript logic
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Create Project Directory

```bash
mkdir medicine-validator
cd medicine-validator
```

### Step 2: Create Folder Structure

```bash
mkdir templates
mkdir static
```

### Step 3: Add All Files

Create the following files in their respective locations:

**Root directory:**
- `app.py`
- `requirements.txt`
- `README.md`

**templates/ folder:**
- `index.html`

**static/ folder:**
- `style.css`
- `script.js`

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask==3.0.0 flask-cors==4.0.0 requests==2.31.0
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Access the App

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🎯 How to Use

### Method 1: Barcode Scanning

1. Click **"Start Camera"** button
2. Point camera at medicine barcode
3. App automatically scans and validates
4. View detailed results

### Method 2: Manual Barcode Entry

1. Enter barcode number in the input field
2. Optionally add expiry date
3. Click **"Scan"** button
4. View results

### Method 3: Search by Name

1. Enter medicine name (e.g., "Aspirin")
2. Click **"Search"** button
3. View FDA and RxNorm data

---

## 🧪 Demo Features

### Test Barcodes

Try these real product barcodes:

| Barcode | Description |
|---------|-------------|
| 5000112576306 | Paracetamol (UK) |
| 0363824792170 | US Medicine Product |
| 8901030835506 | Indian Product |

### Medicine Search Examples

- **Aspirin** - Pain reliever
- **Ibuprofen** - Anti-inflammatory
- **Amoxicillin** - Antibiotic
- **Metformin** - Diabetes medication

---

## 🔌 API Endpoints

### POST /api/scan
Scan and validate a barcode

**Request:**
```json
{
  "barcode": "5000112576306",
  "expiry_date": "2026-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "barcode": "5000112576306",
  "barcode_lookup": {
    "found": true,
    "name": "Paracetamol 500mg",
    "source": "OpenFoodFacts"
  },
  "fda_data": {
    "found": true,
    "brand_name": "Paracetamol",
    "manufacturer": "Generic Pharma"
  },
  "rxnorm": {
    "validated": true,
    "rxcui": "161",
    "name": "Acetaminophen"
  },
  "expiry_status": {
    "status": "valid",
    "message": "✅ Valid for 750 days",
    "days_remaining": 750
  }
}
```

### POST /api/search
Search medicine by name

**Request:**
```json
{
  "name": "Aspirin"
}
```

**Response:**
```json
{
  "success": true,
  "medicine_name": "Aspirin",
  "fda_data": { ... },
  "rxnorm": { ... }
}
```

---

## 📊 Status Indicators

The app provides color-coded expiry status:

| Color | Status | Description |
|-------|--------|-------------|
| 🟢 Green | Valid | More than 90 days remaining |
| 🟡 Yellow | Warning | 30-90 days remaining |
| 🟠 Orange | Expiring Soon | Less than 30 days |
| 🔴 Red | Expired | Past expiry date |

---

## 🔧 Configuration

### Changing Port

Edit `app.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### API Timeout Settings

Modify timeout in `app.py`:
```python
response = requests.get(url, timeout=10)  # Increase timeout
```

---

## 🌐 API Information

### OpenFDA API
- **URL:** https://api.fda.gov/drug/ndc.json
- **Limit:** 240 requests per minute
- **Documentation:** https://open.fda.gov/apis/

### RxNorm API
- **URL:** https://rxnav.nlm.nih.gov/REST
- **Free to use**
- **Documentation:** https://rxnav.nlm.nih.gov/

### OpenFoodFacts API
- **URL:** https://world.openfoodfacts.org/api
- **Free and open source**
- **Documentation:** https://wiki.openfoodfacts.org/

---

## 🛡️ Security & Privacy

### Current Implementation
- ✅ No data stored on server
- ✅ CORS enabled for API calls
- ✅ Input validation on all endpoints
- ✅ Error handling for API failures

### For Production

1. **Disable Debug Mode**
```python
app.run(debug=False)
```

2. **Add Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per hour"])
```

3. **Use Environment Variables**
```python
import os
SECRET_KEY = os.getenv('SECRET_KEY')
```

4. **Enable HTTPS**
```bash
gunicorn --certfile=cert.pem --keyfile=key.pem app:app
```

---

## 🚀 Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t medicine-validator .
docker run -p 5000:5000 medicine-validator
```

---

## 🐛 Troubleshooting

### Camera Not Working
- **Issue:** Browser blocks camera access
- **Solution:** 
  - Use HTTPS (required for camera on most browsers)
  - Check browser permissions
  - Try different browser (Chrome recommended)

### API Timeouts
- **Issue:** APIs not responding
- **Solution:**
  - Check internet connection
  - Increase timeout in code
  - APIs might be temporarily down

### Barcode Not Found
- **Issue:** Product not in databases
- **Solution:**
  - Try different barcode
  - Use medicine name search instead
  - Some products may not be in global databases

### Port Already in Use
- **Issue:** Port 5000 occupied
- **Solution:**
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## 📈 Future Enhancements

- [ ] User authentication system
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Medicine interaction checker
- [ ] Batch recall notifications
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] QR code generation for custom medicines
- [ ] Export reports to PDF
- [ ] Analytics dashboard
- [ ] Push notifications for expiry alerts

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

---

## 📝 License

This project is open source and available for educational purposes.

---

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation
- Review troubleshooting section

---

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**. 

**Important Notes:**
- Not a substitute for professional medical advice
- Always consult healthcare professionals
- Verify medicine information with official sources
- Use at your own risk

---

## 🙏 Acknowledgments

- **OpenFDA** - FDA drug database
- **RxNorm** - NIH medicine database
- **OpenFoodFacts** - Open product database
- **html5-qrcode** - Barcode scanning library

---

**Built with ❤️ using Flask, Python, and Open APIs**

**Version:** 1.0.0  
**Last Updated:** 2025