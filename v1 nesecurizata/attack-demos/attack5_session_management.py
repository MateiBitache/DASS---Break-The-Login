#!/usr/bin/env python3
import requests
import jwt
import json
from datetime import datetime

BASE_URL = "http://localhost:8080/api"

def session_analysis():
    print("[*] Initializing session management analysis")
    
    email = "session_audit@test.com"
    password = "audit_password_123"
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
    token = response.json().get('token')
    
    if not token:
        print("[-] Failed to acquire session token")
        return

    print(f"[+] Session token acquired: {token[:30]}...{token[-15:]}")
    
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("[*] Extracting JWT claims:")
        print(json.dumps(decoded, indent=2, default=str))
        
        if 'exp' in decoded:
            exp_datetime = datetime.fromtimestamp(decoded['exp'])
            time_until_expiry = exp_datetime - datetime.now()
            print(f"[*] Token TTL: {time_until_expiry.total_seconds() / 3600:.2f} hours")
                
    except Exception as e:
        print(f"[!] JWT decode error: {e}")
    
    print("[*] Executing session termination (Logout)")
    requests.post(
        f"{BASE_URL}/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print("[*] Verifying token invalidation status")
    test_response = requests.get(
        f"{BASE_URL}/tickets",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if test_response.status_code == 200:
        print("[!] Token remains active post-termination (Stateless JWT detected)")
    else:
        print("[+] Token successfully invalidated")

if __name__ == "__main__":
    session_analysis()