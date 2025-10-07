#!/usr/bin/env python3
"""
Tech Detection Dashboard Launcher
Starts the Flask API server and opens the web dashboard
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """Main launcher function"""
    print(" Starting Tech Detection Dashboard...")
    print("=" * 50)
    
    # Check if API server is already running
    try:
        import requests
        response = requests.get('http://localhost:9000/api/status', timeout=2)
        if response.status_code == 200:
            print(" API server is already running")
            print("🌐 Dashboard available at: http://localhost:9000")
            print(" API endpoints available at: http://localhost:9000/api/")
            print("🌐 External access: http://159.65.65.140:9000")
            return
    except:
        pass
    
    # Start the API server
    print(" Starting API server...")
    try:
        # Start the server in background
        process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(10)
        
        # Check if server is running
        try:
            import requests
            response = requests.get('http://localhost:9000/api/status', timeout=5)
            if response.status_code == 200:
                print(" API server started successfully!")
                print(" System Status:")
                status = response.json()
                print(f"   - Technologies: {status.get('technologies_count', 0)}")
                print(f"   - Patterns: {status.get('patterns_count', 0)}")
                print(f"   - Pattern Matching: {'' if status.get('engines', {}).get('pattern_matching') else '❌'}")
                print(f"   - WhatWeb: {'' if status.get('engines', {}).get('whatweb') else '❌'}")
                print(f"   - CMSeeK: {'' if status.get('engines', {}).get('cmseek') else '❌'}")
                
                print("\n🌐 Dashboard Information:")
                print("   - Main Dashboard: http://localhost:9000")
                print("   - External Access: http://159.65.65.140:9000")
                print("   - API Status: http://localhost:9000/api/status")
                print("   - Health Check: http://localhost:9000/api/health")
                
                print("\n Quick Test:")
                print("   - Try analyzing: dskbank.bg")
                print("   - Try analyzing: wordpress.com")
                print("   - Try analyzing: joomla.org")
                
                print("\n📱 Opening dashboard in browser...")
                try:
                    webbrowser.open('http://localhost:9000')
                except:
                    print("   (Could not open browser automatically)")
                
                print("\n" + "=" * 50)
                print("🎉 Tech Detection Dashboard is ready!")
                print("   Press Ctrl+C to stop the server")
                
                # Keep the server running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping server...")
                    process.terminate()
                    process.wait()
                    print(" Server stopped")
            else:
                print("❌ Server failed to start properly")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
