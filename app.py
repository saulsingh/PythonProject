from flask import Flask, request, jsonify, render_template
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from virustotal import check_url_virustotal

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/api/check-url', methods=['POST'])
def check_url():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        result = check_url_virustotal(url)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🛡️  Phishing Guard Server Starting...")
    print("📝 Make sure VT_API_KEY environment variable is set!")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)