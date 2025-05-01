"""
Installation script for CPU Scheduler Simulator with Algorithm Comparison feature.
Installs all required packages for both terminal and web interface versions.
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
        # Terminal interface requirements
        'tabulate',      # For formatted table output
        'colorama',      # For colored terminal output
        
        # Web interface requirements
        'flask',         # Web framework
        'pandas',        # For data manipulation and Excel file handling
        'openpyxl',     # For Excel file support
        'numpy',        # For numerical computations
        'plotly',       # For interactive visualizations
        'werkzeug',     # For file uploads and web utilities
        
        # Jupyter notebook support (for documentation)
        'jupyter',       # For running documentation notebooks
        'ipykernel',    # For Jupyter notebook kernel
        
        # Development utilities
        'pytest',        # For running tests
        'black',        # For code formatting
        'flake8'        # For code linting
    ]
    
    print("Checking and installing required packages...")
    
    if not check_pip():
        print("Error: pip is not installed. Please install pip first.")
        sys.exit(1)
    
    # Create requirements.txt file
    with open('requirements.txt', 'w') as f:
        for package in required_packages:
            f.write(f"{package}\n")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("Successfully installed all packages.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)
    
    print("\nAll required packages are installed successfully!")
    print("\nYou can now run either:")
    print("1. Terminal version: python main.py")
    print("2. Web interface: python -m flask --app interface/interface run")

if __name__ == "__main__":
    print("=" * 60)
    print("  CPU Scheduler Simulator - Dependency Installation")
    print("=" * 60)
    
    install_requirements()
    
    print("\nSetup complete!")
    print("For detailed instructions, please refer to README.md")
    print("=" * 60)