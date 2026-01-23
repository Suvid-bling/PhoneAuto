<<<<<<< HEAD
import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def delete_docker(index: int, phone: str, config):
    name = f"T100{index}-{phone}"
    url = f"http://{config['host_local']}/dc_api/v1/remove/{config['ip']}/{name}"
    response = requests.get(url)
    print(f"delete_docker T100{index}-{phone} >>>>{response.text}")

def main():
    config = load_config()
    info_list = config["info_list"]
    
    for device_info in info_list:
        phone, index = device_info[0], device_info[1]
        delete_docker(index, phone, config)

if __name__ == "__main__":
=======
import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def delete_docker(ip: str, host_local: str, index: int, phone: str):
    """Delete a specific Docker container
    
    Args:
        ip: IP address for the machine
        host_local: Local host address for API calls
        index: Device index
        phone: Phone number
    """
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/remove/{ip}/{name}"
    response = requests.get(url)
    print(f"delete_docker T100{index}-{phone} >>>>{response.text}")

def main():
    config = load_config()
    # Extract IP-specific configuration
    if 'ips' in config:
        # Multi-IP configuration
        for ip, ip_config in config['ips'].items():
            print(f"\nProcessing IP: {ip}")
            host_local = ip_config['host_local']
            info_list = ip_config.get('info_list', [])
            for device_info in info_list:
                phone, index = device_info[0], device_info[1]
                delete_docker(ip, host_local, index, phone)
    else:
        # Legacy single-IP configuration
        ip = config['ip']
        host_local = config['host_local']
        info_list = config.get('info_list', [])
        for device_info in info_list:
            phone, index = device_info[0], device_info[1]
            delete_docker(ip, host_local, index, phone)

if __name__ == "__main__":
>>>>>>> 79f43efe8f97865b82f4301ee99fd82b75e4f048
    main()