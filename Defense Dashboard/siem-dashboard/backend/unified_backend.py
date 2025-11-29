from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configuration - UPDATE THESE IPs IF NEEDED
SSH_MONITOR_URL = 'http://127.0.0.1:5002'  # Changed to localhost since running on same machine
SQL_MONITOR_URL = 'http://127.0.0.1:5001'  # Changed to localhost
DOS_MONITOR_URL = 'http://127.0.0.1:5005'  # Changed to localhost

logging.basicConfig(level=logging.ERROR)

def fetch_monitor_data(url, logs_endpoint, stats_endpoint):
    try:
        logs = requests.get(f'{url}/{logs_endpoint}', timeout=5).json()
        stats = requests.get(f'{url}/{stats_endpoint}', timeout=5).json()
        return logs.get('logs', []), stats.get('stats', {})
    except Exception as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return [], {}

@app.route('/api/unified/dashboard')
def get_unified_dashboard():
    """Get aggregated data from all monitors"""
    data = {
        'ssh': {'logs': [], 'stats': {}, 'error': None},
        'sql': {'logs': [], 'stats': {}, 'error': None},
        'dos': {'logs': [], 'stats': {}, 'error': None},
        'overall': {
            'total_threats': 0,
            'critical_alerts': 0,
            'active_incidents': 0,
            'system_health': 100
        }
    }

    # Fetch data from SSH, SQL, DoS monitors
    data['ssh']['logs'], data['ssh']['stats'] = fetch_monitor_data(SSH_MONITOR_URL, 'api/ssh-logs', 'api/stats')
    data['sql']['logs'], data['sql']['stats'] = fetch_monitor_data(SQL_MONITOR_URL, 'api/sql-logs', 'api/sql-stats')
    data['dos']['logs'], data['dos']['stats'] = fetch_monitor_data(DOS_MONITOR_URL, 'api/dos-logs', 'api/dos-stats')

    # Calculate overall stats
    total_threats = len(data['ssh']['logs']) + len(data['sql']['logs']) + len(data['dos']['logs'])
    data['overall'] = {
        'total_threats': total_threats,
        'critical_alerts': total_threats,
        'active_incidents': min(total_threats, 10),
        'system_health': max(0, 100 - (total_threats * 0.5))
    }

    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

# NEW ENDPOINT: Get DoS metrics for real-time charts
@app.route('/api/dos/metrics')
def get_dos_metrics():
    """Proxy DoS metrics from dos_dashboard for real-time charts"""
    try:
        response = requests.get(f'{DOS_MONITOR_URL}/metrics', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        logging.error(f"Error fetching DoS metrics: {e}")
        return jsonify({
            'cpu': [0]*30,
            'net_5001': [0]*30,
            'net_6083': [0]*30,
            'current_cpu': 0,
            'current_5001': 0,
            'current_6083': 0,
            'dos_detected': False,
            'dos_reason': ''
        })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Unified SIEM Backend'
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛡️ UNIFIED SIEM BACKEND")
    print("="*70)
    print("\nAggregating data from:")
    print(f"  • SSH Monitor: {SSH_MONITOR_URL}")
    print(f"  • SQL Monitor: {SQL_MONITOR_URL}")
    print(f"  • DoS Monitor: {DOS_MONITOR_URL}")
    print("\n✅ Server running on http://0.0.0.0:5003")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
