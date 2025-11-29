from flask import Flask, render_template, jsonify
from flask_cors import CORS
import psutil
import time
import os
from collections import deque
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for unified dashboard

# Keep recent history for graphs (last 30 samples, 1/s)
HISTORY_LENGTH = 30
cpu_history = deque([0]*HISTORY_LENGTH, maxlen=HISTORY_LENGTH)
net_history_5001 = deque([0]*HISTORY_LENGTH, maxlen=HISTORY_LENGTH)
net_history_6083 = deque([0]*HISTORY_LENGTH, maxlen=HISTORY_LENGTH)

# DoS attack logs for SIEM integration
dos_attack_logs = deque(maxlen=100)  # Keep last 100 attacks

last_net = psutil.net_io_counters(pernic=True)

def get_port_bytes(port):
    """Returns approximate TCP RX+TX bytes for a given port (simple method using lsof)"""
    try:
        data = os.popen(f"sudo lsof -i TCP:{port} 2>/dev/null | grep ESTABLISHED").read()
        # Count every established connection as ~1500 bytes worst-case; for demo
        return len(data.splitlines()) * 1500
    except:
        return 0

def get_port_connections(port):
    """Count established connections on a port"""
    try:
        data = os.popen(f"sudo lsof -i TCP:{port} 2>/dev/null | grep ESTABLISHED").read()
        return len(data.splitlines())
    except:
        return 0

def refresh_histories():
    cpu = psutil.cpu_percent(interval=None)
    cpu_history.append(cpu)

    # For demo, use connection count as "traffic" (can be faked by hping/DoS).
    net_5001 = get_port_bytes(5001)
    net_6083 = get_port_bytes(6083)
    net_history_5001.append(net_5001)
    net_history_6083.append(net_6083)

    # Simple DoS detection logic:
    dos_detected = False
    reason = ""
    target_port = None
    
    if cpu > 70 or net_5001 > 10000 or net_6083 > 10000:
        dos_detected = True
        if cpu > 70:
            reason = "High CPU usage"
            target_port = "system"
        elif net_5001 > 10000:
            reason = "Heavy traffic at port 5001"
            target_port = 5001
        elif net_6083 > 10000:
            reason = "Heavy traffic at port 6083"
            target_port = 6083
        
        # Log the DoS attack
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'sourceIP': 'unknown',  # Can be enhanced to track IPs
            'requestCount': net_5001 if target_port == 5001 else net_6083 if target_port == 6083 else int(cpu),
            'targetPort': target_port,
            'status': 'detected',
            'reason': reason,
            'cpu': cpu,
            'traffic_5001': net_5001,
            'traffic_6083': net_6083
        }
        
        # Only log if it's a new attack (not same as last entry)
        if not dos_attack_logs or dos_attack_logs[-1]['reason'] != reason:
            dos_attack_logs.append(log_entry)
            print(f"\n🚨 [DoS ATTACK DETECTED]")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Reason: {reason}")
            print(f"   CPU: {cpu}% | Port 5001: {net_5001} bytes | Port 6083: {net_6083} bytes\n")

@app.after_request
def add_header(response):
    """Allow embedding in iframe and CORS"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/metrics")
def metrics():
    refresh_histories()
    curr_cpu = cpu_history[-1]
    curr_5001 = net_history_5001[-1]
    curr_6083 = net_history_6083[-1]

    # Simple DoS detection logic:
    dos_detected = False
    reason = ""
    if curr_cpu > 70 or curr_5001 > 10000 or curr_6083 > 10000:
        dos_detected = True
        if curr_cpu > 70:
            reason = "High CPU usage"
        elif curr_5001 > 10000:
            reason = "Heavy traffic at port 5001"
        elif curr_6083 > 10000:
            reason = "Heavy traffic at port 6083"

    return jsonify({
        "cpu": list(cpu_history),
        "net_5001": list(net_history_5001),
        "net_6083": list(net_history_6083),
        "current_cpu": curr_cpu,
        "current_5001": curr_5001,
        "current_6083": curr_6083,
        "dos_detected": dos_detected,
        "dos_reason": reason
    })

# ---------------- SIEM INTEGRATION ENDPOINTS (NO AUTH REQUIRED) ----------------
@app.route("/api/dos-logs")
def get_dos_logs():
    """Get DoS attack logs for SIEM dashboard - NO AUTH REQUIRED"""
    return jsonify({
        'success': True,
        'logs': list(dos_attack_logs)
    })

@app.route("/api/dos-stats")
def get_dos_stats():
    """Get DoS attack statistics for SIEM dashboard - NO AUTH REQUIRED"""
    total_attacks = len(dos_attack_logs)
    
    # Count unique target ports
    target_ports = set(str(log.get('targetPort', 'unknown')) for log in dos_attack_logs)
    
    # Calculate average CPU during attacks
    avg_cpu = sum(log.get('cpu', 0) for log in dos_attack_logs) / total_attacks if total_attacks > 0 else 0
    
    # Get current system status
    current_cpu = psutil.cpu_percent(interval=0.1)
    conn_5001 = get_port_connections(5001)
    conn_6083 = get_port_connections(6083)
    
    return jsonify({
        'success': True,
        'stats': {
            'total_attempts': total_attacks,
            'unique_targets': len(target_ports),
            'active_attacks': 1 if (current_cpu > 70 or conn_5001 > 10 or conn_6083 > 10) else 0,
            'avg_cpu_during_attacks': round(avg_cpu, 2),
            'current_cpu': round(current_cpu, 2),
            'current_connections': {
                'port_5001': conn_5001,
                'port_6083': conn_6083
            }
        }
    })

@app.route("/api/health")
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DoS Attack Monitor',
        'monitoring': True
    })

if __name__ == "__main__":
    print("\n" + "="*70)
    print("⚡ DoS ATTACK MONITOR")
    print("="*70)
    print("\n📊 Monitoring:")
    print("   • CPU usage")
    print("   • Network traffic on port 5001")
    print("   • Network traffic on port 6083")
    print("\n🚨 DoS Detection Triggers:")
    print("   • CPU > 70%")
    print("   • Port 5001 traffic > 10000 bytes")
    print("   • Port 6083 traffic > 10000 bytes")
    print("\n🔗 SIEM Integration Endpoints:")
    print("   • /api/dos-logs  - Get attack logs")
    print("   • /api/dos-stats - Get statistics")
    print("   • /api/health    - Health check")
    print("\n✅ Server running on http://0.0.0.0:5005")
    print("   Dashboard available at http://192.168.31.106:5005")
    print("   CORS enabled for unified SIEM dashboard")
    print("="*70 + "\n")
    
    # To allow lsof without password for demo
    os.system("sudo chmod +r /proc/*/fd 2>/dev/null")
    
    app.run(host="0.0.0.0", port=5005, debug=True)