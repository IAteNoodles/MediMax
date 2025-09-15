#!/usr/bin/env python3
"""
Network Configuration Helper for FastAPI Cypher Query Generator
This script helps you find your local IP address and provides connection instructions.
"""

import socket
import subprocess
import platform
import os

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to determine"

def get_hostname():
    """Get the hostname of this machine"""
    return socket.gethostname()

def get_all_ips():
    """Get all network interfaces and their IP addresses"""
    hostname = socket.gethostname()
    try:
        # Get all IP addresses for this hostname
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        # Filter out loopback addresses
        ip_addresses = [ip for ip in ip_addresses if not ip.startswith("127.")]
        return ip_addresses
    except Exception:
        return []

def check_port_availability(port=8000):
    """Check if the specified port is available"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('0.0.0.0', port))
        s.close()
        return result != 0  # Port is available if connection fails
    except Exception:
        return False

def get_firewall_info():
    """Get firewall information based on the operating system"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return {
            "system": "macOS",
            "firewall_check": "System Preferences > Security & Privacy > Firewall",
            "command": "sudo pfctl -sr | grep 8000",
            "allow_command": "sudo pfctl -f /etc/pf.conf"
        }
    elif system == "Linux":
        return {
            "system": "Linux",
            "firewall_check": "Check ufw or iptables",
            "command": "sudo ufw status",
            "allow_command": "sudo ufw allow 8000"
        }
    elif system == "Windows":
        return {
            "system": "Windows",
            "firewall_check": "Windows Defender Firewall",
            "command": "netsh advfirewall show allprofiles",
            "allow_command": "netsh advfirewall firewall add rule name=\"FastAPI\" dir=in action=allow protocol=TCP localport=8000"
        }
    else:
        return {
            "system": "Unknown",
            "firewall_check": "Check your system's firewall settings",
            "command": "N/A",
            "allow_command": "N/A"
        }

def main():
    """Main function to display network configuration information"""
    print("🌐 FastAPI Cypher Query Generator - Network Configuration")
    print("=" * 60)
    
    # Basic network information
    hostname = get_hostname()
    local_ip = get_local_ip()
    all_ips = get_all_ips()
    port = 8000
    
    print(f"🖥️  Hostname: {hostname}")
    print(f"📍 Primary Local IP: {local_ip}")
    
    if all_ips:
        print(f"📡 All Network IPs: {', '.join(all_ips)}")
    
    print(f"🔌 Port: {port}")
    
    # Check port availability
    port_available = check_port_availability(port)
    if port_available:
        print(f"✅ Port {port} is available")
    else:
        print(f"❌ Port {port} is already in use")
    
    print("\n🔗 Access URLs:")
    print("-" * 30)
    print(f"📱 Localhost: http://127.0.0.1:{port}")
    print(f"🌐 Network: http://{local_ip}:{port}")
    
    if all_ips and len(all_ips) > 1:
        print("🔄 Alternative IPs:")
        for ip in all_ips:
            if ip != local_ip:
                print(f"   http://{ip}:{port}")
    
    print(f"\n📚 API Documentation:")
    print(f"   Swagger UI: http://{local_ip}:{port}/docs")
    print(f"   ReDoc: http://{local_ip}:{port}/redoc")
    
    # Firewall information
    print(f"\n🔥 Firewall Configuration:")
    print("-" * 30)
    firewall_info = get_firewall_info()
    print(f"System: {firewall_info['system']}")
    print(f"Check: {firewall_info['firewall_check']}")
    
    if firewall_info['allow_command'] != "N/A":
        print(f"Allow port command: {firewall_info['allow_command']}")
    
    # Client connection examples
    print(f"\n📱 Client Connection Examples:")
    print("-" * 30)
    
    # curl examples
    print("🔧 cURL:")
    print(f"   curl http://{local_ip}:{port}/")
    print(f"   curl -X POST http://{local_ip}:{port}/generate_simple \\")
    print(f"        -H \"Content-Type: application/json\" \\")
    print(f"        -d '{{\"query\": \"Find all users\"}}'")
    
    # Python requests example
    print("\n🐍 Python requests:")
    print(f"   import requests")
    print(f"   response = requests.post('http://{local_ip}:{port}/generate_simple',")
    print(f"                           json={{'query': 'Find all users'}})")
    print(f"   print(response.text)")
    
    # Mobile/tablet access
    print(f"\n📱 Mobile/Tablet Access:")
    print(f"   Open browser and go to: http://{local_ip}:{port}/docs")
    
    # QR Code suggestion
    print(f"\n📱 Pro Tip:")
    print(f"   Generate a QR code for: http://{local_ip}:{port}/docs")
    print(f"   This makes it easy to access from mobile devices!")
    
    # Network troubleshooting
    print(f"\n🔧 Troubleshooting:")
    print("-" * 30)
    print("1. Make sure the FastAPI server is running")
    print("2. Check firewall settings allow port 8000")
    print("3. Ensure devices are on the same network")
    print("4. Try accessing from different devices on your network")
    print("5. Check if your router blocks inter-device communication")
    
    # Security warning
    print(f"\n⚠️  Security Note:")
    print("-" * 30)
    print("🔒 Server is accessible to ALL devices on your local network")
    print("🔑 Make sure to set GEMINI_API_KEY in environment variables")
    print("🚫 Do NOT expose this server to the internet without proper security")
    print("🛡️  Consider using authentication for production deployments")

def test_network_connectivity():
    """Test network connectivity to the FastAPI server"""
    import requests
    import time
    
    local_ip = get_local_ip()
    port = 8000
    url = f"http://{local_ip}:{port}/"
    
    print(f"\n🧪 Testing connectivity to {url}")
    print("-" * 30)
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is accessible on the network!")
            data = response.json()
            print(f"📊 Response: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
    except requests.exceptions.Timeout:
        print("❌ Connection timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_network_connectivity()
    else:
        main()
        
        # Ask if user wants to test connectivity
        try:
            test_input = input("\n🧪 Test network connectivity? (y/n): ").lower().strip()
            if test_input in ['y', 'yes']:
                test_network_connectivity()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except:
            pass