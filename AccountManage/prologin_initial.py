import json
import requests
import os
import sys

# Add parent directory to path to import MachineManage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from MachineManage.tools import change_login_state,TransName

def start_lamda(index:int,phone:str):
    url = f"{domain}/rpc/startLamda/"
    data = {
        "host": host_local,
        "ip": ip,
        "index": index,
        "name": f"T100{index}-{phone}",
    }
    response = requests.post(url, json=data)
    print(f"start_lamda T100{index}-{phone} >>>>{response.text}")

def batch_changeLogin_state(ip: str, host_local: str, device_info_list: list):
    """
    Update login state for all devices in the batch.
    
    Args:
        ip: IP address for the devices
        host_local: Local host address
        device_info_list: List of device info [phone, index, "", ""]
    """
    for phone, index, _, _ in device_info_list:
        #start_lamda(index, phone) AVOID START LAMDAT IF IN RELOGIN TASK
        device_name = f"T100{index}-{phone}"
        change_login_state([device_name])

if __name__ == "__main__":

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    ip = "172.16.42.55"
    ip_config = config["ips"][ip]
    host_local = config["global"]["host_local"]
    info_list = ip_config["info_list"]

    batch_changeLogin_state(ip, host_local, info_list)