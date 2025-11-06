"""
SMS Provider Setup Guide and Installer
Helps users install and configure Twilio and AWS SNS for SMS alerts
"""

import subprocess
import sys
import os

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully installed {package_name}")
            return True
        else:
            print(f"Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("SMS PROVIDER SETUP FOR CATALYST SCANNER")
    print("=" * 60)
    print()
    
    # Check current status
    print("Checking current SMS provider libraries...")
    print()
    
    twilio_installed = check_package('twilio')
    boto3_installed = check_package('boto3')
    
    print(f"Twilio library: {'INSTALLED' if twilio_installed else 'NOT INSTALLED'}")
    print(f"AWS boto3 library: {'INSTALLED' if boto3_installed else 'NOT INSTALLED'}")
    print()
    
    if twilio_installed and boto3_installed:
        print("All SMS provider libraries are already installed!")
        print()
    else:
        print("Missing SMS provider libraries detected.")
        print()
        
        install_choice = input("Would you like to install missing libraries? (y/n): ").lower().strip()
        if install_choice in ['y', 'yes']:
            print()
            
            if not twilio_installed:
                print("Installing Twilio library...")
                install_package('twilio')
                print()
            
            if not boto3_installed:
                print("Installing AWS boto3 library...")
                install_package('boto3')
                print()
            
            print("Installation complete!")
            print()
    
    # Provider setup instructions
    print("=" * 60)
    print("SMS PROVIDER CONFIGURATION GUIDE")
    print("=" * 60)
    print()
    
    print("1. TWILIO SETUP (Recommended)")
    print("-" * 30)
    print("   • Sign up: https://www.twilio.com/try-twilio")
    print("   • Get a free trial account ($15 credit)")
    print("   • Purchase a phone number (~$1/month)")
    print("   • SMS cost: ~$0.0075 per message")
    print()
    print("   Required credentials:")
    print("   • Account SID (starts with 'AC')")
    print("   • Auth Token (32-character string)")
    print("   • From Phone Number (e.g., +1234567890)")
    print()
    print("   Configuration in SMS settings:")
    print("   • Select 'Twilio' provider")
    print("   • Enter credentials in settings")
    print("   • Test SMS functionality")
    print()
    
    print("2. AWS SNS SETUP (Alternative)")
    print("-" * 30)
    print("   • AWS account required")
    print("   • SMS cost: ~$0.00645 per message")
    print("   • More complex setup")
    print()
    print("   Required credentials:")
    print("   • AWS Access Key ID")
    print("   • AWS Secret Access Key")
    print("   • AWS Region (e.g., us-east-1)")
    print()
    print("   Configuration steps:")
    print("   • Create IAM user with SNS permissions")
    print("   • Generate access keys")
    print("   • Configure in SMS settings")
    print()
    
    print("3. MOCK MODE (Testing)")
    print("-" * 30)
    print("   • Already enabled by default")
    print("   • No cost, no real SMS sent")
    print("   • Perfect for development/testing")
    print("   • Logs messages to console")
    print()
    
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Run the main Catalyst Scanner application")
    print("2. Go to Settings > SMS Alerts tab")
    print("3. Choose your SMS provider:")
    print("   • Mock (for testing)")
    print("   • Twilio (easiest for real SMS)")
    print("   • AWS SNS (for AWS users)")
    print("4. Enter your credentials")
    print("5. Test SMS functionality")
    print()
    
    print("For immediate testing, Mock mode is ready to use!")
    print("For production SMS alerts, Twilio is recommended for beginners.")

if __name__ == "__main__":
    main()