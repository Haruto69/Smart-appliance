"""
Smart Campus Attack Dashboard - Attack Modules Package
======================================================

This package contains all attack scripts for security testing:
- nmap_scan.py: Network reconnaissance and port scanning
- brute_force.py: Credential testing with Crunch + Hydra
- dos_attack.py: Denial of Service attack vectors
- sql_injection.py: SQL injection payload library

Usage:
    from attacks import nmap_scan, brute_force, dos_attack, sql_injection
    
    # Or import specific functions
    from attacks.nmap_scan import run_nmap_scan
    from attacks.brute_force import run_hydra_attack
    from attacks.dos_attack import syn_flood
    from attacks.sql_injection import get_all_payloads

Author: Smart Campus Security Team
License: Educational Use Only
"""

__version__ = '1.0.0'
__author__ = 'Smart Campus Security Team'

# Import attack modules for easy access
try:
    from . import nmap_scan
    from . import brute_force
    from . import dos_attack
    from . import sql_injection
except ImportError as e:
    print(f"[!] Warning: Could not import attack modules: {e}")

# Attack module registry
ATTACK_MODULES = {
    'nmap': 'nmap_scan',
    'brute_force': 'brute_force',
    'dos': 'dos_attack',
    'sql': 'sql_injection'
}

# Export all modules
__all__ = [
    'nmap_scan',
    'brute_force', 
    'dos_attack',
    'sql_injection',
    'ATTACK_MODULES'
]