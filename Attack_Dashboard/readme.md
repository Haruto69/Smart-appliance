# Smart Campus Attack Dashboard

A comprehensive Flask-based security testing dashboard for simulating attacks on smart campus infrastructure with ESP32 sensors and Raspberry Pi.

## 🎯 Features

- **Network Scanning**: Aggressive nmap scans with port discovery and service enumeration
- **Brute Force Attacks**: Crunch + Hydra for credential testing
- **DoS Attacks**: Multiple attack vectors (SYN flood, UDP flood, HTTP flood, Slowloris, etc.)
- **SQL Injection**: Automated payload generation and testing
- **Modern UI**: Cyberpunk-themed dashboard with real-time monitoring
- **Attack History**: Track all security tests with detailed logs

## 📋 Prerequisites

Install the following tools on your system:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nmap hydra crunch hping3 apache2-utils python3 python3-pip

# Fedora/RHEL
sudo dnf install -y nmap hydra crunch hping3 httpd-tools python3 python3-pip
```

## 🚀 Installation

1. **Clone or create the project directory:**

```bash
mkdir smart-campus-attack-dashboard
cd smart-campus-attack-dashboard
```

2. **Create the directory structure:**

```bash
mkdir -p attacks templates static
```

3. **Copy all files to their respective locations:**

```
smart-campus-attack-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── attacks/
│   ├── nmap_scan.py
│   ├── brute_force.py
│   ├── dos_attack.py
│   └── sql_injection.py
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── scan.html
    ├── brute_force.html
    ├── dos.html
    └── sql_injection.html
```

4. **Install Python dependencies:**

```bash
pip3 install -r requirements.txt
```

5. **Make attack scripts executable:**

```bash
chmod +x attacks/*.py
```

## 🔧 Configuration

1. **Update Flask secret key** in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this-to-something-secure'
```

2. **Configure target IPs** in the dashboard to match your smart campus setup

3. **Ensure you have root/sudo privileges** for running some attacks (hping3, nmap)

## 🎮 Usage

### Starting the Dashboard

```bash
# Development mode
python3 app.py

# Production mode with sudo (for privileged attacks)
sudo python3 app.py
```

Access the dashboard at: `http://localhost:5000`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### Running Individual Attack Scripts

You can also run attack scripts directly from the command line:

```bash
# Network scan
python3 attacks/nmap_scan.py 192.168.1.100 aggressive

# Brute force
python3 attacks/brute_force.py 192.168.1.100 ssh root

# DoS attack
python3 attacks/dos_attack.py 192.168.1.100 80 syn_flood

# View SQL injection payloads
python3 attacks/sql_injection.py
```

## 📊 Attack Types

### 1. Network Scanning
- **Basic Scan**: Quick port discovery (1-10000)
- **Aggressive Scan**: Full port scan with vulnerability detection

### 2. Brute Force
- **Services**: SSH, FTP, HTTP, MySQL, PostgreSQL, RDP, SMB
- **Wordlist**: Auto-generated with Crunch + common passwords
- **Multi-user mode**: Tests multiple common usernames

### 3. DoS Attacks
- **SYN Flood**: TCP SYN packet flooding
- **UDP Flood**: UDP packet bombardment
- **ICMP Flood**: Ping flood attack
- **HTTP Flood**: Application layer attack
- **Slowloris**: Connection exhaustion
- **Port Exhaustion**: All ports attacked simultaneously
- **Multi-Vector**: All attacks combined

### 4. SQL Injection
- **Authentication Bypass**: Login form exploitation
- **UNION-based**: Data extraction via UNION queries
- **Error-based**: Error message information disclosure
- **Time-based Blind**: Delayed response testing
- **Data Extraction**: Database enumeration
- **Command Execution**: OS command injection

## 🔒 Security Notes

⚠️ **CRITICAL WARNINGS:**

1. **Only use on authorized systems** - Unauthorized access is illegal
2. **This is for educational/testing purposes only**
3. **DoS attacks can crash systems** - Use responsibly
4. **Run in isolated network environment** - Don't affect production
5. **Obtain written permission** before testing any system

## 🎯 Smart Campus Setup

Configure your test environment:

1. **Raspberry Pi** (192.168.1.100)
   - Main controller
   - Runs sensor dashboard
   - SSH, HTTP, FTP services

2. **ESP32 Devices** (192.168.1.101-104)
   - Connected sensors
   - Temperature, humidity, motion sensors
   - WiFi enabled

3. **Attack VM**
   - Kali Linux or Ubuntu
   - All tools installed
   - Network access to Pi and ESP32s

## 📝 Database

The application uses SQLite for storing attack logs and scan results. Database file: `attack_dashboard.db`

To reset the database:
```bash
rm attack_dashboard.db
python3 app.py  # Recreates database
```

## 🐛 Troubleshooting

**Permission Denied Errors:**
```bash
sudo python3 app.py
```

**Hydra/Crunch Not Found:**
```bash
sudo apt install hydra crunch
```

**Port Already in Use:**
```python
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Attack Scripts Not Executing:**
```bash
chmod +x attacks/*.py
sudo pip3 install -r requirements.txt
```

## 📚 Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Nmap Documentation](https://nmap.org/docs.html)
- [Hydra Documentation](https://github.com/vanhauser-thc/thc-hydra)
- [SQL Injection Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)

## ⚖️ Legal Disclaimer

This tool is provided for educational and authorized security testing purposes only. The creators are not responsible for any misuse or damage caused by this software. Always obtain proper authorization before testing any systems you do not own.

## 🤝 Contributing

Contributions are welcome! Please ensure all attack scripts include proper safety checks and warnings.

## 📄 License

MIT License - Use at your own risk

---

**Remember: With great power comes great responsibility. Use wisely! 🛡️**
