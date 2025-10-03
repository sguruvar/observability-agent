#!/usr/bin/env python3
"""
Start both the observability stack and the main application
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, background=False):
    """Run a shell command"""
    try:
        if background:
            return subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Starting Complete Insurance Claims System")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("observability"):
        print("❌ Please run this script from the project root directory")
        print("   Expected structure: app/ and observability/ folders")
        sys.exit(1)
    
    print("1️⃣ Starting Observability Stack...")
    print("-" * 40)
    
    # Start observability stack
    if not run_command("python start_observability.py", cwd="observability"):
        print("❌ Failed to start observability stack")
        sys.exit(1)
    
    print("\n2️⃣ Starting Main Application...")
    print("-" * 40)
    
    # Start the main app in background
    print("🚀 Starting instrumented Flask app...")
    app_process = run_command("python app_instrumented.py", cwd="app", background=True)
    
    if not app_process:
        print("❌ Failed to start main application")
        sys.exit(1)
    
    print("\n🎉 System Started Successfully!")
    print("=" * 60)
    print("📊 Services Available:")
    print("   • Main App: http://localhost:3000")
    print("   • AI Dashboard: http://localhost:8000")
    print("   • Prometheus: http://localhost:9090")
    print("   • OpenSearch: http://localhost:5601")
    print("   • Jaeger: http://localhost:16686")
    print("   • Grafana: http://localhost:3001 (admin/admin)")
    print("\n🛑 To stop the system:")
    print("   Press Ctrl+C to stop the app")
    print("   Then run: cd observability && docker-compose down")
    print("\n" + "=" * 60)
    
    try:
        # Wait for the app process
        app_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping application...")
        app_process.terminate()
        print("✅ Application stopped")
        print("💡 Don't forget to stop the observability stack:")
        print("   cd observability && docker-compose down")

if __name__ == "__main__":
    main()
