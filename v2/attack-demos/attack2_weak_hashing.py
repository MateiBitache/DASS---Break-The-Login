#!/usr/bin/env python3
import hashlib

def evaluate_hashing():
    print("[*] Initiating hash algorithm evaluation")
    
    password = "password123"
    md5_hash = hashlib.md5(password.encode()).hexdigest()
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()
    
    print(f"[*] Source string: {password}")
    print(f"[*] Generated MD5: {md5_hash}")
    print(f"[*] Generated SHA1: {sha1_hash}")
    print("[*] Reference BCrypt: $2a$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW")
    print("[*] Evaluation complete.")

if __name__ == "__main__":
    evaluate_hashing()