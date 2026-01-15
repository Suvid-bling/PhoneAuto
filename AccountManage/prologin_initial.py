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

if __name__ == "__main__":

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    domain = config['domain']
    host_local = config['host_local']
    ip = config['ip']
    info_list = config['info_list']
    
    for phone, index, _, _ in info_list:
        #start_lamda(index, phone) AVOID START LAMDAT IF IN RELOGIN TASK
        device_name = f"T100{index}-{phone}"
        change_login_state([device_name])
