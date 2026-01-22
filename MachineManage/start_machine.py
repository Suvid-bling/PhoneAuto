import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def start_docker(ip: str, host_local: str, index: int, phone: str):
    """Start a specific Docker container
    
    Args:
        ip: IP address for the machine
        host_local: Local host address for API calls
        index: Device index
        phone: Phone number
    """
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/run/{ip}/{name}"
    response = requests.get(url)
    print(f"run_docker T100{index}-{phone} >>>>{response.text}")

def start_batch(ip: str, host_local: str, device_info_list: list):
    """Start all machines in a batch
    
    Args:
        ip: IP address for the machines
        host_local: Local host address for API calls
        device_info_list: List of device info [phone, index, "", ""]
    """
    for device_info in device_info_list:
        phone, index = device_info[0], device_info[1]
        start_docker(ip, host_local, index, phone)

if __name__ == "__main__":
    config = load_config()
    # Extract IP-specific configuration
    if 'ips' in config:
        # Multi-IP configuration
        for ip, ip_config in config['ips'].items():
            print(f"\nProcessing IP: {ip}")
            host_local = ip_config['host_local']
            info_list = ip_config.get('info_list', [])
            if info_list:
                start_batch(ip, host_local, info_list)
    else:
        # Legacy single-IP configuration
        ip = config['ip']
        host_local = config['host_local']
        info_list = config.get('info_list', [])
        if info_list:
            start_batch(ip, host_local, info_list)