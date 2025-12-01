#!/usr/bin/env python3
"""
Aggressive Network Scanning Script for Smart Campus Security Testing
"""
import sys
import subprocess
import json
from datetime import datetime

def run_nmap_scan(target_ip, scan_type):
    """Execute aggressive nmap scans"""
    print(f"[*] Starting {scan_type} scan on {target_ip}")
    print(f"[*] Timestamp: {datetime.now()}")
    
    scans = []
    
    if scan_type == "basic":
        scans = [
            # Quick port scan
            f"nmap -p- --min-rate 5000 {target_ip}",
            # Service version detection
            f"nmap -sV -p 1-10000 {target_ip}",
            # OS detection
            f"nmap -O {target_ip}"
        ]
    elif scan_type == "aggressive":
        scans = [
            # Aggressive all-ports scan
            f"nmap -p- -T5 --min-rate 10000 -A {target_ip}",
            # Service enumeration
            f"nmap -sV -sC -p 1-65535 --version-intensity 9 {target_ip}",
            # Vulnerability scan
            f"nmap --script vuln -p- {target_ip}",
            # OS detection aggressive
            f"nmap -O --osscan-guess -T5 {target_ip}",
            # Script scan for common vulnerabilities
            f"nmap --script=default,discovery,auth,exploit -p- {target_ip}"
        ]
    
    results = []
    for cmd in scans:
        print(f"\n[+] Executing: {cmd}")
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            print(result.stdout)
            results.append(result.stdout)
            
            if result.returncode != 0:
                print(f"[!] Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[!] Scan timed out")
        except Exception as e:
            print(f"[!] Exception: {str(e)}")
    
    # Parse and display open ports
    print("\n" + "="*60)
    print("[*] SCAN SUMMARY")
    print("="*60)
    
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 nmap_scan.py <target_ip> <scan_type>")
        print("Scan types: basic, aggressive")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    scan_type = sys.argv[2]
    
    run_nmap_scan(target_ip, scan_type)

if __name__ == "__main__":
    main()