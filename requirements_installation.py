
"""
Installation script for CPU Scheduler Simulator with Algorithm Comparison feature
"""

import subprocess
import sys
import os

def check_pip():
    """Check if pip is installed"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_requirements():
    """Install required packages for the CPU Scheduler Simulator"""
    required_packages = [
        'tabulate',
        'colorama'
    ]
    
    print("Checking and installing required packages...")
    
    if not check_pip():
        print("Error: pip is not installed. Please install pip first.")
        sys.exit(1)
    
    for package in required_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            print(f"Successfully installed {package}.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)
    
    print("\nAll required packages are installed successfully!")
    print("You can now run the CPU Scheduler Simulator.")

if __name__ == "__main__":
    print("=" * 60)
    print("  CPU Scheduler Simulator - Dependency Installation")
    print("=" * 60)
    
    install_requirements()
    
    print("\nSetup complete! You can now run the simulator with:")
    print("python main.py")
    print("=" * 60)