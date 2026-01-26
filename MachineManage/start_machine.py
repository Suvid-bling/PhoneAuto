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

def check_machinestate(ip: str, host_local: str, name: str):
    url = f"http://{host_local}/get_android_boot_status/{ip}/{name}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get('code') == 200
    except Exception as e:
        print(f"Error checking machine state: {e}")
        return False

def wait_machines_ready(ip: str, host_local: str, device_info_list: list, max_wait_time: int = 300, check_interval: int = 10):
    """Wait for all machines to boot up
    
    Args:
        ip: IP address for the machines
        host_local: Local host address for API calls
        device_info_list: List of device info [phone, index, "", ""]
        max_wait_time: Maximum wait time in seconds (default: 300)
        check_interval: Check interval in seconds (default: 10)
    
    Returns:
        bool: True if all machines ready, False if timeout
    """
    import time
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        all_ready = True
        for device_info in device_info_list:
            phone, index = device_info[0], device_info[1]
            name = f"T100{index}-{phone}"
            if not check_machinestate(ip, host_local, name):
                all_ready = False
                break
        
        if all_ready:
            return True
        
        time.sleep(check_interval)
        elapsed_time += check_interval
    
    return False

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
