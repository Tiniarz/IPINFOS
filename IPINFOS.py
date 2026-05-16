import os
import time
import requests
import ctypes
from colorama import init, Fore, Style

init(autoreset=True)

DARK_PURPLE = Fore.MAGENTA + Style.DIM  
LIGHT_PURPLE = Fore.MAGENTA + Style.BRIGHT
ERROR_RED = Fore.RED + Style.BRIGHT

ASCII_ART = """
██╗██████╗     ██╗███╗   ██╗███████╗ ██████╗ ███████╗
██║██╔══██╗    ██║████╗  ██║██╔════╝██╔═══██╗██╔════╝
██║██████╔╝    ██║██╔██╗ ██║█████╗  ██║   ██║███████╗
██║██╔═══╝     ██║██║╚██╗██║██╔══╝  ██║   ██║╚════██║
██║██║         ██║██║ ╚████║██║     ╚██████╔╝███████║
╚═╝╚═╝         ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚══════╝
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
    url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "fail", "message": f"HTTP Error {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "fail", "message": str(e)}

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
            display_fields = {
                "IP Address": data.get("query"),
                "Country": f"{data.get('country')} ({data.get('countryCode')})",
                "Region/State": f"{data.get('regionName')} ({data.get('region')})",
                "City": data.get("city"),
                "Zip Code": data.get("zip"),
                "Latitude": data.get("lat"),
                "Longitude": data.get("lon"),
                "Timezone": data.get("timezone"),
                "ISP": data.get("isp"),
                "Organization": data.get("org"),
                "AS Number/Name": data.get("as")
            }
            gdi_lines.append("IP address information:")
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
        display_fields = {
            "IP Address": data.get("query"),
            "Country": f"{data.get('country')} ({data.get('countryCode')})",
            "Region/State": f"{data.get('regionName')} ({data.get('region')})",
            "City": data.get("city"),
            "Zip Code": data.get("zip"),
            "Latitude": data.get("lat"),
            "Longitude": data.get("lon"),
            "Timezone": data.get("timezone"),
            "ISP": data.get("isp"),
            "Organization": data.get("org"),
            "AS Number/Name": data.get("as")
        }
        
        for key, value in display_fields.items():
            print(LIGHT_PURPLE + f"  {key:<18}: {value}")
            time.sleep(0.05)
    else:
        error_msg = data.get("message", "Unknown error occurred.")
        print(ERROR_RED + f"  Error: Failed to retrieve data ({error_msg})")
        time.sleep(0.05)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()