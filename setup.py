#!/usr/bin/env python3
"""
Ultimate Tech Detection System Setup Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'data/datasets/organized',
        'data/datasets/raw',
        'data/datasets/individual',
        'data/external_tools',
        'output/reports',
        'static/fontawesome/css',
        'static/fontawesome/webfonts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def setup_environment():
    """Set up environment configuration"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("⚠️  No env.example found, please create .env manually")
    else:
        print("✅ .env file already exists")

def check_external_tools():
    """Check if external tools are available"""
    tools = {
        'whatweb': 'WhatWeb',
        'cmseek': 'CMSeeK',
        'wappalyzer': 'Wappalyzer'
    }
    
    for tool, name in tools.items():
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {name} is available")
            else:
                print(f"⚠️  {name} not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"⚠️  {name} not found - some features may be limited")

def main():
    """Main setup function"""
    print("🚀 Setting up Ultimate Tech Detection System...")
    print("=" * 50)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Setup failed - could not install dependencies")
        return False
    
    # Setup environment
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    # Check external tools
    print("\n🛠️  Checking external tools...")
    check_external_tools()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python3 api_server.py")
    print("3. Open: http://localhost:9000")
    print("\n🎉 Happy detecting!")

if __name__ == "__main__":
    main()
