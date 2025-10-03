#!/usr/bin/env python3
"""
Start the complete observability stack
"""

import subprocess
import time
import requests
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e}")
        return False

def wait_for_service(url, name, timeout=60):
    """Wait for a service to be ready"""
    print(f"⏳ Waiting for {name} to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    print(f"❌ {name} failed to start within {timeout} seconds")
    return False

def main():
    print("🚀 Starting Observability Stack")
    print("=" * 50)
    
    # Check if Docker is running
    if not run_command("docker --version"):
        print("❌ Docker is not installed or not running")
        return
    
    if not run_command("docker-compose --version"):
        print("❌ Docker Compose is not installed")
        return
    
    # Start the observability stack
    print("🐳 Starting Docker containers...")
    if not run_command("docker-compose up -d", cwd="."):
        print("❌ Failed to start Docker containers")
        return
    
    # Wait for services to be ready
    services = [
        ("http://localhost:9090/-/ready", "Prometheus"),
        ("http://localhost:9200", "OpenSearch"),
        ("http://localhost:5601", "OpenSearch Dashboards"),
        ("http://localhost:16686", "Jaeger"),
        ("http://localhost:3001", "Grafana"),
        ("http://localhost:8000/health", "AI Agent")
    ]
    
    for url, name in services:
        if not wait_for_service(url, name):
            print(f"⚠️ {name} may not be fully ready, but continuing...")
    
    print("\n🎉 Observability Stack Started Successfully!")
    print("=" * 50)
    print("📊 Services Available:")
    print("   • Prometheus: http://localhost:9090")
    print("   • OpenSearch: http://localhost:9200")
    print("   • OpenSearch Dashboards: http://localhost:5601")
    print("   • Jaeger: http://localhost:16686")
    print("   • Grafana: http://localhost:3001 (admin/admin)")
    print("   • AI Agent Dashboard: http://localhost:8000")
    print("\n🚀 To start your instrumented Flask app:")
    print("   python app_instrumented.py")
    print("\n🛑 To stop the stack:")
    print("   docker-compose down")

if __name__ == "__main__":
    main()
