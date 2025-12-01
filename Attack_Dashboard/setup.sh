#!/bin/bash

# Smart Campus Attack Dashboard - Setup Script (Kali Linux 2024+)
# Handles externally-managed Python environments

echo "============================================"
echo "  Smart Campus Attack Dashboard Setup"
echo "  Kali Linux Compatible"
echo "============================================"
echo ""

# Check if running as root for setup
if [ "$EUID" -eq 0 ]; then 
    echo "[!] Please run WITHOUT sudo for initial setup"
    echo "[!] Usage: ./setup.sh"
    echo "[!] (sudo is only needed when running the app)"
    exit 1
fi

echo "[*] Verifying required system tools..."
echo ""

# Check each tool
tools=("nmap" "hping3" "hydra" "crunch" "ab")
all_present=true

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ✗ $tool (missing - install with: sudo apt install ${tool})"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "[!] Some tools are missing. Install them with:"
    echo "    sudo apt update"
    echo "    sudo apt install nmap hping3 hydra crunch apache2-utils"
    exit 1
fi

echo ""
echo "[*] All system tools present!"
echo ""
echo "[*] Setting up Python virtual environment..."

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "[!] python3-venv not installed. Installing..."
    sudo apt install python3-venv -y
fi

# Create virtual environment
if [ -d "venv" ]; then
    echo "[*] Virtual environment already exists"
else
    python3 -m venv venv
    echo "[+] Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "[*] Installing Python dependencies in virtual environment..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[!] Failed to install dependencies"
    exit 1
fi

echo ""
echo "[*] Making attack scripts executable..."
chmod +x attacks/*.py

echo ""
echo "[*] Creating necessary directories..."
mkdir -p logs wordlists results

echo ""
echo "[*] Setting up database..."
python3 << 'EOF'
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print("[+] Database initialized successfully")
except Exception as e:
    print(f"[!] Database initialization error: {e}")
    print("[*] Database will be created on first run")
EOF

# Deactivate venv
deactivate

echo ""
echo "============================================"
echo "  Installation Complete!"
echo "============================================"
echo ""
echo "✓ System tools verified (nmap, hydra, etc.)"
echo "✓ Python virtual environment created"
echo "✓ Dependencies installed"
echo "✓ Project structure ready"
echo ""
echo "To start the dashboard:"
echo ""
echo "  Method 1 (Recommended - with venv):"
echo "    source venv/bin/activate"
echo "    sudo venv/bin/python3 app.py"
echo ""
echo "  Method 2 (Direct):"
echo "    sudo venv/bin/python3 app.py"
echo ""
echo "Then access at: http://localhost:5000"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠️  Note: sudo is required for raw socket access"
echo "    (needed for DoS attacks and some scans)"
echo ""
echo "============================================"