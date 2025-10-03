#!/usr/bin/env python3
"""
Simple startup script for the Insurance Claims Agent
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if .env file exists
if not os.path.exists('.env'):
    print("❌ .env file not found!")
    print("Please run 'python deploy.py' first to set up the environment")
    sys.exit(1)

# Import and run the Flask app
if __name__ == "__main__":
    from app import app
    
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'
    
    print(f"🚀 Insurance Claims Agent (Python) starting...")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌐 Application: http://localhost:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print("")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
