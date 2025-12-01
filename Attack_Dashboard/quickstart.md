# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y nmap hydra crunch hping3 apache2-utils python3 python3-pip
```

### Step 2: Install Python Requirements

```bash
pip3 install -r requirements.txt
```

### Step 3: Run Setup Script

```bash
chmod +x setup.sh
sudo ./setup.sh
```

### Step 4: Start the Dashboard

```bash
sudo python3 app.py
```

### Step 5: Access Dashboard

Open your browser and go to: **http://localhost:5000**

Login with:
- **Username**: admin
- **Password**: admin123

---

## 📋 Quick Commands

### Run Individual Attacks from Command Line

**Network Scan:**
```bash
python3 attacks/nmap_scan.py 192.168.1.100 aggressive
```

**Brute Force SSH:**
```bash
python3 attacks/brute_force.py 192.168.1.100 ssh root
```

**DoS Attack:**
```bash
sudo python3 attacks/dos_attack.py 192.168.1.100 80 syn_flood
```

**View SQL Payloads:**
```bash
python3 attacks/sql_injection.py
```

---

## 🎯 Testing Your Smart Campus

### 1. Initial Network Discovery

1. Go to **Network Scan** page
2. Enter Raspberry Pi IP: `192.168.1.100`
3. Select "Aggressive Scan"
4. Click "Start Scan"
5. Wait for results showing open ports

### 2. Brute Force Attack

1. Go to **Brute Force** page
2. Enter target IP: `192.168.1.100`
3. Select service: `SSH`
4. Enter username: `pi` or `multi`
5. Click "Launch Brute Force"
6. Monitor for successful credentials

### 3. DoS Testing

1. Go to **DoS Attack** page
2. Enter target IP: `192.168.1.100`
3. Select port: `80` (HTTP)
4. Choose attack: `http_flood`
5. Click "Launch DoS Attack"
6. Observe service disruption

### 4. SQL Injection

1. Go to **SQL Injection** page
2. Enter target URL: `http://192.168.1.100/login.php`
3. Select: `Authentication Bypass`
4. Choose payload: `admin' OR '1'='1`
5. Click "Launch SQL Injection"
6. Opens target with payload in new tab

---

## 🔧 Configuration

### Update Target IPs

Edit `config.py` to match your setup:

```python
SMART_CAMPUS_TARGETS = {
    'raspberry_pi': {
        'ip': '192.168.1.100',  # Change this
        ...
    }
}
```

### Change Dashboard Port

Edit `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port here
```

---

## ⚠️ Troubleshooting

**Permission Denied?**
```bash
sudo python3 app.py
```

**Tools Not Found?**
```bash
which nmap hydra crunch hping3
# If any missing, reinstall:
sudo apt install nmap hydra crunch hping3
```

**Port Already in Use?**
```bash
sudo lsof -i :5000
# Kill the process or change port
```

**Database Errors?**
```bash
rm attack_dashboard.db
python3 app.py  # Recreates database
```

---

## 📊 Dashboard Features

### Main Dashboard
- View all attack statistics
- Monitor running attacks
- Quick access to all modules
- Real-time status updates

### Network Scan
- Basic and aggressive scans
- Port discovery
- Service enumeration
- Vulnerability detection

### Brute Force
- Multiple protocol support
- Auto wordlist generation
- Multi-user testing
- Real-time results

### DoS Attacks
- 7 different attack types
- Port-specific targeting
- Multi-vector option
- Automatic duration control

### SQL Injection
- Pre-built payload library
- Multiple injection types
- Direct browser redirection
- Custom payload support

---

## 🎓 Learning Resources

### Understand the Attacks

1. **Nmap**: Learn network reconnaissance
2. **Hydra**: Master credential attacks
3. **SQL Injection**: Understand database vulnerabilities
4. **DoS**: Learn service disruption techniques

### Best Practices

✅ Always get written authorization
✅ Test in isolated environments
✅ Document all findings
✅ Follow responsible disclosure
✅ Keep tools updated

❌ Never attack unauthorized systems
❌ Don't disrupt production services
❌ Avoid illegal activities
❌ Don't share credentials

---

## 💡 Pro Tips

1. **Start with Basic Scans**: Understand the target before attacking
2. **Use Multi-User Brute Force**: Test common usernames first
3. **Monitor System Resources**: Some attacks are resource-intensive
4. **Save Attack Logs**: Review results in the dashboard
5. **Test Incrementally**: Start small, then escalate

---

## 🆘 Need Help?

1. Check README.md for detailed documentation
2. Review attack script comments for usage
3. Check logs directory for error details
4. Verify all tools are installed correctly

---

## ⚖️ Legal Reminder

This tool is for **EDUCATIONAL and AUTHORIZED TESTING ONLY**

- Get written permission before testing
- Only test systems you own or have explicit authorization
- Understand local laws regarding security testing
- Use responsibly and ethically

**Remember**: Unauthorized access is illegal and can result in criminal charges.

---

**Happy (Ethical) Hacking! 🛡️**