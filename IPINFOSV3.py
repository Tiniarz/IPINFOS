import os
import time
import requests
import ctypes
import socket
import json
import subprocess
import platform
import concurrent.futures
from colorama import init, Fore, Style

init(autoreset=True)

DARK_PURPLE = Fore.MAGENTA + Style.DIM  
LIGHT_PURPLE = Fore.MAGENTA + Style.BRIGHT
ERROR_RED = Fore.RED + Style.BRIGHT

ASCII_ART = """
██╗██████╗     ██╗███╗   ██╗███████╗ ██████╗ ███████╗    ██╗   ██╗██████╗ 
██║██╔══██╗    ██║████╗  ██║██╔════╝██╔═══██╗██╔════╝    ██║   ██║╚════██╗
██║██████╔╝    ██║██╔██╗ ██║█████╗  ██║   ██║███████╗    ██║   ██║ █████╔╝
██║██╔═══╝     ██║██║╚██╗██║██╔══╝  ██║   ██║╚════██║    ╚██╗ ██╔╝ ╚═══██╗
██║██║         ██║██║ ╚████║██║     ╚██████╔╝███████║     ╚████╔╝ ██████╔╝
╚═╝╚═╝         ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚══════╝      ╚═══╝  ╚═════╝ 
"""

GDI_ASCII = """
 ██████╗ ██████╗ ██╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗
██╔════╝ ██╔══██╗██║    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝
██║  ███╗██║  ██║██║    ██╔████╔██║██║   ██║██║  ██║█████╗  
██║   ██║██║  ██║██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  
╚██████╔╝██████╔╝██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
 ╚═════╝ ╚═════╝ ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_ip_info(ip_address):
    url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,reverse,mobile,proxy,hosting,query"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"status": "fail", "message": f"HTTP Error {response.status_code}"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def get_threat_intel(ip_address):
    url = f"https://rdap.arin.net/registry/ip/{ip_address}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            name = data.get("name", "Unknown")
            handle = data.get("handle", "Unknown")
            return f"Network: {name} ({handle})"
        return "No registry data found"
    except:
        return "Registry threat verification timeout"

def check_port(ip_address, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        result = s.connect_ex((ip_address, port))
        s.close()
        if result == 0:
            return port
    except:
        pass
    return None

def scan_ports(ip_address):
    extended_ports = [
        21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1025, 
        1433, 1723, 3306, 3389, 5900, 8080, 8443, 9000, 27017
    ]
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(check_port, ip_address, port) for port in extended_ports]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res is not None:
                open_ports.append(str(res))
    return ", ".join(sorted(open_ports, key=int)) if open_ports else "None detected"

def calculate_cidr_range(ip_address):
    try:
        octets = ip_address.split('.')
        if len(octets) == 4:
            return f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
        return "Unknown"
    except:
        return "Unknown"

def ping_host(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
        if output.returncode == 0:
            return "Active / Online"
        return "No Response (Filtered/Offline)"
    except:
        return "Execution Error"

def get_dns_records(ip_address):
    try:
        host = socket.gethostbyaddr(ip_address)[0]
        return f"Resolved Hostname: {host}"
    except:
        return "No explicit DNS records mapped"

def parse_as_details(as_string):
    if not as_string:
        return "Unknown", "Unknown"
    try:
        parts = as_string.split(' ', 1)
        asn = parts[0]
        name = parts[1] if len(parts) > 1 else "Unknown"
        return asn, name
    except:
        return "Unknown", "Unknown"

def verify_ip_version(ip_address):
    if ":" in ip_address:
        return "IPv6"
    return "IPv4"

def check_bogon_status(ip_address):
    try:
        octets = [int(x) for x in ip_address.split('.')]
        if octets[0] in [0, 10, 127] or (octets[0] == 172 and 16 <= octets[1] <= 31) or (octets[0] == 192 and octets[1] == 168):
            return "Yes (Private/Bogon IP)"
        return "No (Public Routable IP)"
    except:
        return "Unknown"

def draw_text_gdi(lines):
    hdc = ctypes.windll.user32.GetDC(0)
    for i, line in enumerate(lines):
        ctypes.windll.gdi32.TextOutW(hdc, 50, 100 + (i * 25), line, len(line))
    ctypes.windll.user32.ReleaseDC(0, hdc)

def main():
    clear_screen()
    
    for line in ASCII_ART.splitlines():
        if line.strip():
            print(DARK_PURPLE + line)
            time.sleep(0.05)
            
    print(LIGHT_PURPLE + "Type ip address here: ", end="", flush=True)
    target_ip = input().strip()
    
    if target_ip == "GDI Mode":
        clear_screen()
        for line in GDI_ASCII.splitlines():
            if line.strip():
                print(DARK_PURPLE + line)
                time.sleep(0.05)
                
        print(LIGHT_PURPLE + "Welcome to GDI Mode a secret menu")
        time.sleep(0.05)
        print(LIGHT_PURPLE + "Type ip address here: ", end="", flush=True)
        target_ip = input().strip()
        
        data = get_ip_info(target_ip)
        gdi_lines = []
        
        if data.get("status") == "success":
            resolved_ip = data.get("query")
            open_ports_str = scan_ports(resolved_ip)
            threat_status = get_threat_intel(resolved_ip)
            cidr_range = calculate_cidr_range(resolved_ip)
            ping_status = ping_host(resolved_ip)
            dns_status = get_dns_records(resolved_ip)
            asn_num, asn_name = parse_as_details(data.get("as"))
            ip_ver = verify_ip_version(resolved_ip)
            bogon_status = check_bogon_status(resolved_ip)
            
            display_fields = {
                "IP Address": resolved_ip,
                "IP Version": ip_ver,
                "Bogon Status": bogon_status,
                "ICMP Status": ping_status,
                "Reverse DNS": data.get("reverse"),
                "DNS Mapping": dns_status,
                "Estimated CIDR": cidr_range,
                "Registry Object": threat_status,
                "ASN Registry": asn_num,
                "ASN Operator": asn_name,
                "Country": f"{data.get('country')} ({data.get('countryCode')})",
                "Region/State": f"{data.get('regionName')} ({data.get('region')})",
                "City": data.get("city"),
                "Zip Code": data.get("zip"),
                "Latitude": str(data.get("lat")),
                "Longitude": str(data.get("lon")),
                "Timezone": data.get("timezone"),
                "ISP": data.get("isp"),
                "Organization": data.get("org"),
                "Mobile Connection": "Yes" if data.get("mobile") else "No",
                "Proxy/VPN/Tor": "Yes" if data.get("proxy") else "No",
                "Hosting/DataCenter": "Yes" if data.get("hosting") else "No",
                "Open Ports": open_ports_str
            }
            gdi_lines.append("IP address information")
            for key, value in display_fields.items():
                gdi_lines.append(f"{key}: {value}")
        else:
            error_msg = data.get("message", "Unknown error occurred.")
            gdi_lines.append(f"Error: Failed to retrieve data ({error_msg})")
            
        while True:
            draw_text_gdi(gdi_lines)
            time.sleep(1)
            
    print(LIGHT_PURPLE + "\nIP address information\n")
    time.sleep(0.05)
    
    data = get_ip_info(target_ip)
    
    if data.get("status") == "success":
        resolved_ip = data.get("query")
        open_ports_str = scan_ports(resolved_ip)
        threat_status = get_threat_intel(resolved_ip)
        cidr_range = calculate_cidr_range(resolved_ip)
        ping_status = ping_host(resolved_ip)
        dns_status = get_dns_records(resolved_ip)
        asn_num, asn_name = parse_as_details(data.get("as"))
        ip_ver = verify_ip_version(resolved_ip)
        bogon_status = check_bogon_status(resolved_ip)
        
        display_fields = {
            "IP Address": resolved_ip,
            "IP Version": ip_ver,
            "Bogon Status": bogon_status,
            "ICMP Status": ping_status,
            "Reverse DNS": data.get("reverse"),
            "DNS Mapping": dns_status,
            "Estimated CIDR": cidr_range,
            "Registry Object": threat_status,
            "ASN Registry": asn_num,
            "ASN Operator": asn_name,
            "Country": f"{data.get('country')} ({data.get('countryCode')})",
            "Region/State": f"{data.get('regionName')} ({data.get('region')})",
            "City": data.get("city"),
            "Zip Code": data.get("zip"),
            "Latitude": data.get("lat"),
            "Longitude": data.get("lon"),
            "Timezone": data.get("timezone"),
            "ISP": data.get("isp"),
            "Organization": data.get("org"),
            "Mobile Connection": "Yes" if data.get("mobile") else "No",
            "Proxy/VPN/Tor": "Yes" if data.get("proxy") else "No",
            "Hosting/DataCenter": "Yes" if data.get("hosting") else "No",
            "Open Ports": open_ports_str
        }
        
        for key, value in display_fields.items():
            print(LIGHT_PURPLE + f"  {key:<22}: {value}")
            time.sleep(0.05)
    else:
        error_msg = data.get("message", "Unknown error occurred.")
        print(ERROR_RED + f"  Error: Failed to retrieve data ({error_msg})")
        time.sleep(0.05)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()