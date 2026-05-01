#!/usr/bin/env python3
import requests
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8080/api"

def brute_force_attack():
    print("[*] Initializing authentication brute-force module")
    
    test_email = "target@test.com"
    test_password = "secret123"
    
    requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": test_email, "password": test_password}
    )
    
    passwords = [
        "123456", "password", "12345678", "qwerty", "abc123",
        "monkey", "letmein", "trustno1", "dragon", "master", "secret123"
    ]
    
    print(f"[*] Target: {test_email}")
    print(f"[*] Loaded {len(passwords)} payloads")
    
    start_time = time.time()
    
    for attempts, password in enumerate(passwords, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": test_email, "password": password},
                timeout=5
            )
            
            if response.status_code == 200:
                elapsed = time.time() - start_time
                token = response.json().get('token', '')[:30]
                print(f"[+] Match found: {password}")
                print(f"[*] Authentication successful in {elapsed:.2f}s after {attempts} attempts")
                print(f"[*] Session token: {token}...")
                break
            else:
                print(f"[-] Attempt {attempts}: {password} - Denied")
                
        except requests.exceptions.Timeout:
            print(f"[!] Attempt {attempts}: {password} - Timeout (Rate limit potential)")
            break
        except Exception as e:
            print(f"[!] Error: {e}")

def parallel_brute_force():
    print("[*] Initializing parallel execution module (10 threads)")
    
    def try_login(i):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "target@test.com", "password": f"payload_{i}"},
                timeout=5
            )
            return f"Thread-{i} status: {response.status_code}"
        except Exception as e:
            return f"Thread-{i} error: {e}"
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(try_login, range(1, 21)))
    
    for result in results:
        print(f"[*] {result}")

if __name__ == "__main__":
    brute_force_attack()
    parallel_brute_force()