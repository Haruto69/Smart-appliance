from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import subprocess
import re
from datetime import datetime
from collections import defaultdict
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Store attack logs in memory
attack_logs = []
attack_stats = {
    'total_attempts': 0,
    'unique_ips': set(),
    'failed_logins': 0,
    'active_attacks': 0
}
lock = threading.Lock()

def parse_ssh_log_line(line):
    """Parse SSH log lines for failed login attempts"""
    patterns = [
        # Failed password
        r'Failed password for (?:invalid user )?(\w+) from ([\d.]+) port (\d+)',
        # Invalid user
        r'Invalid user (\w+) from ([\d.]+) port (\d+)',
        # Connection closed (potential brute force)
        r'Connection closed by authenticating user (\w+) ([\d.]+) port (\d+)',
        # Disconnected from invalid user
        r'Disconnected from invalid user (\w+) ([\d.]+) port (\d+)',
        # Authentication failure
        r'authentication failure.*ruser=(\w+).*rhost=([\d.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            return {
                'timestamp': datetime.now().isoformat(),
                'username': groups[0] if groups[0] else 'unknown',
                'ip': groups[1] if len(groups) > 1 else 'unknown',
                'port': groups[2] if len(groups) > 2 else '22',
                'status': 'failed',
                'raw_log': line.strip()
            }
    return None

def monitor_ssh_logs():
    """Background thread to continuously monitor SSH logs"""
    global attack_logs, attack_stats
    
    # Start journalctl process
    process = subprocess.Popen(
        ['journalctl', '-u', 'ssh', '-f', '-n', '0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    print("SSH log monitoring started...")
    
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                log_entry = parse_ssh_log_line(line)
                if log_entry:
                    with lock:
                        attack_logs.insert(0, log_entry)
                        # Keep only last 100 logs
                        attack_logs[:] = attack_logs[:100]
                        
                        # Update stats
                        attack_stats['total_attempts'] += 1
                        attack_stats['unique_ips'].add(log_entry['ip'])
                        attack_stats['failed_logins'] += 1
                        
                        print(f"Attack detected: {log_entry['username']}@{log_entry['ip']}")
    except Exception as e:
        print(f"Error monitoring logs: {e}")
    finally:
        process.terminate()

@app.route('/')
def index():
    """Serve a simple HTML page with links to endpoints"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSH Brute Force Monitor API</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #1a1a1a; color: #fff; }
            h1 { color: #4a9eff; }
            .endpoint { 
                background: #2a2a2a; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px;
                border-left: 4px solid #4a9eff;
            }
            code { background: #000; padding: 5px; border-radius: 3px; }
            a { color: #4a9eff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🛡️ SSH Brute Force Monitor API</h1>
        <p>Backend service for monitoring SSH brute force attacks</p>
        
        <div class="endpoint">
            <h3>GET <code>/api/ssh-logs</code></h3>
            <p>Get recent SSH attack attempts</p>
            <a href="/api/ssh-logs" target="_blank">Try it →</a>
        </div>
        
        <div class="endpoint">
            <h3>GET <code>/api/stats</code></h3>
            <p>Get attack statistics</p>
            <a href="/api/stats" target="_blank">Try it →</a>
        </div>
        
        <div class="endpoint">
            <h3>GET <code>/api/top-attackers</code></h3>
            <p>Get top attacking IP addresses</p>
            <a href="/api/top-attackers" target="_blank">Try it →</a>
        </div>
        
        <div class="endpoint">
            <h3>GET <code>/api/health</code></h3>
            <p>Check API health status</p>
            <a href="/api/health" target="_blank">Try it →</a>
        </div>
        
        <hr style="margin: 30px 0; border: 1px solid #444;">
        <p><strong>Note:</strong> This service monitors SSH logs in real-time using journalctl.</p>
        <p>Make sure to run with appropriate permissions: <code>sudo python app.py</code></p>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/ssh-logs')
def get_ssh_logs():
    """Get recent SSH attack logs"""
    with lock:
        return jsonify({
            'success': True,
            'logs': attack_logs[:50],  # Return last 50 logs
            'count': len(attack_logs)
        })

@app.route('/api/stats')
def get_stats():
    """Get attack statistics"""
    with lock:
        return jsonify({
            'success': True,
            'stats': {
                'total_attempts': attack_stats['total_attempts'],
                'unique_ips': len(attack_stats['unique_ips']),
                'failed_logins': attack_stats['failed_logins'],
                'active_attacks': attack_stats['total_attempts']  # Can be refined
            }
        })

@app.route('/api/top-attackers')
def get_top_attackers():
    """Get top attacking IPs"""
    with lock:
        ip_counts = defaultdict(int)
        for log in attack_logs:
            ip_counts[log['ip']] += 1
        
        top_attackers = sorted(
            [{'ip': ip, 'attempts': count} for ip, count in ip_counts.items()],
            key=lambda x: x['attempts'],
            reverse=True
        )[:10]
        
        return jsonify({
            'success': True,
            'top_attackers': top_attackers
        })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SSH Brute Force Monitor',
        'monitoring': True,
        'logs_captured': len(attack_logs)
    })

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Clear all logs (for testing)"""
    global attack_logs, attack_stats
    with lock:
        attack_logs.clear()
        attack_stats = {
            'total_attempts': 0,
            'unique_ips': set(),
            'failed_logins': 0,
            'active_attacks': 0
        }
    return jsonify({'success': True, 'message': 'Logs cleared'})

if __name__ == '__main__':
    # Start log monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_ssh_logs, daemon=True)
    monitor_thread.start()
    
    # Run Flask app
    # Use 0.0.0.0 to allow access from other devices on network
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
