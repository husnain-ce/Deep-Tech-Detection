#!/usr/bin/env python3
"""
Ultimate Tech Detection System - Main Runner
"""

import os
import sys
import argparse
from pathlib import Path

def run_server():
    """Run the Flask server"""
    print("🚀 Starting Ultimate Tech Detection Server...")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("Please copy env.example to .env and configure your API keys")
        return False
    
    # Import and run the server
    try:
        from api_server import app
        print("✅ Server starting on http://localhost:9000")
        print("📱 Dashboard: http://localhost:9000")
        print("🔧 API: http://localhost:9000/api/")
        print("🌐 External: http://159.65.65.140:9000")
        print("\nPress Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=9000, debug=True)
    except ImportError as e:
        print(f"❌ Error importing server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True

def run_setup():
    """Run the setup script"""
    print("🔧 Running setup...")
    try:
        import setup
        setup.main()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Ultimate Tech Detection System')
    parser.add_argument('command', nargs='?', default='server', 
                       choices=['server', 'setup', 'test'],
                       help='Command to run (default: server)')
    
    args = parser.parse_args()
    
    if args.command == 'server':
        run_server()
    elif args.command == 'setup':
        run_setup()
    elif args.command == 'test':
        print("🧪 Running tests...")
        os.system('python -m pytest tests/ -v')
    else:
        print(f"❌ Unknown command: {args.command}")

if __name__ == "__main__":
    main()
