#!/usr/bin/env python3
import subprocess
import sys

def install_dependencies():
    packages = ['requests>=2.31.0', 'PyJWT>=2.8.0']
    
    print("[*] Checking system dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"[+] Verified module: {package.split('>=')[0]}")
        except subprocess.CalledProcessError:
            print(f"[-] Failed to install module: {package}")

if __name__ == "__main__":
    install_dependencies()