import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_machine_namelist(ip: str, host_local: str):
    """Get list of machine names from API
    
    Args:
        ip: IP address for the machines
        host_local: Local host address for API calls
        
    Returns:
        List of machine names
    """
    url = f"http://{host_local}/dc_api/v1/get/{ip}"
    response = requests.get(url)
    data = response.json()
    
    if data.get('code') == 200:
        names = [item['name'] for item in data.get('data', [])]
        print(f"Found {len(names)} machines: {names}")
        return names
    else:
        print(f"Failed to get machine list: {data}")
        return []


def stop_machines_all(ip: str, host_local: str, names: list):
    """Stop all machines in the name list
    
    Args:
        ip: IP address for the machines
        host_local: Local host address for API calls
        names: List of machine names to stop
    """
    for name in names:
        url = f"http://{host_local}/dc_api/v1/stop/{ip}/{name}"
        response = requests.get(url)
        print(f"stop_docker {name} >>>> {response.text}")

def stop_docker(ip: str, host_local: str, index: int, phone: str):
    """Stop a specific Docker container
    
    Args:
        ip: IP address for the machine
        host_local: Local host address for API calls
        index: Device index
        phone: Phone number
    """
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/stop/{ip}/{name}"
    response = requests.get(url)
    print(f"stop_docker T100{index}-{phone} >>>>{response.text}")

def stop_batch(ip: str, host_local: str, device_info_list: list):
    """Stop all machines in a batch
    
    Args:
        ip: IP address for the machines
        host_local: Local host address for API calls
        device_info_list: List of device info [phone, index, "", ""]
    """
    for device_info in device_info_list:
        phone, index = device_info[0], device_info[1]
        stop_docker(ip, host_local, index, phone)

if __name__ == "__main__":
    print("stop_machine excuting:")
    config = load_config()
    # Extract IP-specific configuration
    if 'ips' in config:
        # Multi-IP configuration
        for ip, ip_config in config['ips'].items():
            print(f"\nProcessing IP: {ip}")
            host_local = ip_config['host_local']
            names = get_machine_namelist(ip, host_local)
            stop_machines_all(ip, host_local, names)
    else:
        # Legacy single-IP configuration
        ip = config['ip']
        host_local = config['host_local']
        names = get_machine_namelist(ip, host_local)
        stop_machines_all(ip, host_local, names)
