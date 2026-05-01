#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8080/api"

def test_weak_passwords():
    print("[*] Initializing password policy evaluation")
    
    weak_passwords = ["a", "12", "test", "123456", "password"]
    run_id = int(time.time())
    
    for i, password in enumerate(weak_passwords, 1):
        email = f"test_acc_{run_id}_{i}@test.com"
        payload = {"email": email, "password": password}
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_preview = response.json().get('token', 'N/A')[:30]
                print(f"[+] Registration successful | Email: {email} | Pass: {password} | Token: {token_preview}...")
            else:
                error_msg = response.json().get('message', 'Unknown error')
                print(f"[-] Registration rejected | Pass: {password} | Reason: {error_msg}")
                
        except Exception as e:
            print(f"[!] Connection error for payload '{password}': {e}")

if __name__ == "__main__":
    test_weak_passwords()
