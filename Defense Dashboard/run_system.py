#!/usr/bin/env python3
"""
Unified launcher for Smart Campus Project
Runs all services in parallel using multiprocessing
"""
import multiprocessing
import sys
import os
from pathlib import Path
import time

def run_app2():
    """Run the smart home control application (app2.py)"""
    print("[LAUNCHER] Starting app2.py on port 5001...")
    sys.path.insert(0, str(Path(__file__).parent / "Vuln"))
    os.chdir(str(Path(__file__).parent / "Vuln"))
    
    # Import and run app2
    from app2 import app
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

def run_ssh_monitor():
    """Run SSH monitoring service"""
    print("[LAUNCHER] Starting ssh_monitor.py on port 5002...")
    sys.path.insert(0, str(Path(__file__).parent / "siem-dashboard" / "backend"))
    os.chdir(str(Path(__file__).parent / "siem-dashboard" / "backend"))
    
    # Import and run ssh_monitor
    from ssh_monitor import app
    app.run(host='0.0.0.0', port=5002, debug=False)

def run_unified_backend():
    """Run unified backend service"""
    print("[LAUNCHER] Starting unified_backend.py on port 5003...")
    sys.path.insert(0, str(Path(__file__).parent / "siem-dashboard" / "backend"))
    os.chdir(str(Path(__file__).parent / "siem-dashboard" / "backend"))
    
    # Import and run unified_backend
    from unified_backend import app
    app.run(host='0.0.0.0', port=5003, debug=False)

def run_dos_dashboard():
    """Run DoS dashboard"""
    print("[LAUNCHER] Starting dos_dashboard.py on port 5005...")
    sys.path.insert(0, str(Path(__file__).parent / "dashboard"))
    os.chdir(str(Path(__file__).parent / "dashboard"))
    
    # Import and run dos_dashboard
    from dos_dashboard import app
    app.run(host='0.0.0.0', port=5005, debug=False)

def run_frontend_server():
    """Run frontend HTTP server"""
    print("[LAUNCHER] Starting frontend server on port 8080...")
    os.chdir(str(Path(__file__).parent / "siem-dashboard" / "frontend"))
    
    import http.server
    import socketserver
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    with socketserver.TCPServer(("", 8080), MyHTTPRequestHandler) as httpd:
        print("[LAUNCHER] Frontend server ready at http://192.168.31.106:8080")
        httpd.serve_forever()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 SMART CAMPUS PROJECT - UNIFIED LAUNCHER")
    print("="*80)
    print("\nStarting all services in parallel...\n")
    
    # Create processes for each service
    processes = []
    
    services = [
        ("Smart Home App (app2.py)", run_app2),
        ("SSH Monitor", run_ssh_monitor),
        ("Unified Backend", run_unified_backend),
        ("DoS Dashboard", run_dos_dashboard),
        ("Frontend Server", run_frontend_server)
    ]
    
    for name, func in services:
        p = multiprocessing.Process(target=func, name=name)
        p.daemon = True
        processes.append((name, p))
        p.start()
        print(f"✅ Started: {name}")
        time.sleep(0.5)  # Small delay between starts
    
    print("\n" + "="*80)
    print("🎯 ALL SERVICES RUNNING")
    print("="*80)
    print("\n📊 Access Points:")
    print("  • Smart Home Control: http://192.168.31.106:5001")
    print("  • SSH Monitor API:    http://192.168.31.106:5002")
    print("  • Unified Backend:    http://192.168.31.106:5003")
    print("  • DoS Dashboard:      http://192.168.31.106:5005")
    print("  • Unified Dashboard:  http://192.168.31.106:8080/unified_dashboard.html")
    print("\n⚠️  Press Ctrl+C to stop all services")
    print("="*80 + "\n")
    
    # Keep main process alive
    try:
        for name, p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all services...")
        for name, p in processes:
            print(f"  Stopping: {name}")
            p.terminate()
        print("\n✅ All services stopped. Goodbye!\n")
        sys.exit(0)
