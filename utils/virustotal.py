import requests
import base64
import time
import os

VIRUSTOTAL_API_KEY = os.environ.get('VT_API_KEY', '76b648f00869606d24f69fdc50190d160abf3d46d4354e104b1a58db224592de')

def check_url_virustotal(url):
    """
    Check URL using VirusTotal API
    Returns dict with analysis results
    """
    try:
        if VIRUSTOTAL_API_KEY == 'YOUR_VIRUSTOTAL_API_KEY_HERE':
            return {'error': 'VirusTotal API key not configured on server'}
        
        # Submit URL to VirusTotal
        headers = {
            'x-apikey': VIRUSTOTAL_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        submit_response = requests.post(
            'https://www.virustotal.com/api/v3/urls',
            headers=headers,
            data={'url': url},
            timeout=10
        )
        
        if submit_response.status_code != 200:
            return {'error': 'Failed to submit URL to VirusTotal'}
        
        # Wait for analysis to complete
        time.sleep(3)
        
        # Get analysis results
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip('=')
        
        analysis_response = requests.get(
            f'https://www.virustotal.com/api/v3/urls/{url_id}',
            headers={'x-apikey': VIRUSTOTAL_API_KEY},
            timeout=10
        )
        
        if analysis_response.status_code != 200:
            return {'error': 'Failed to retrieve analysis results'}
        
        result = analysis_response.json()
        stats = result['data']['attributes']['last_analysis_stats']
        details = result['data']['attributes']['last_analysis_results']
        
        # Determine safety level
        safety_level = 'safe'
        if stats['malicious'] > 0 or stats['suspicious'] > 2:
            safety_level = 'dangerous'
        elif stats['suspicious'] > 0:
            safety_level = 'suspicious'
        
        return {
            'url': url,
            'malicious': stats.get('malicious', 0),
            'suspicious': stats.get('suspicious', 0),
            'harmless': stats.get('harmless', 0),
            'undetected': stats.get('undetected', 0),
            'total': len(details),
            'details': details,
            'safety_level': safety_level
        }
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout - VirusTotal API took too long to respond'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


def get_cache_key(url):
    """Generate cache key for URL"""
    return base64.urlsafe_b64encode(url.encode()).decode().strip('=')
