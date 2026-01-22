import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_machine_namelist(config):
    """Get list of machine names from API"""
    url = f"http://{config['host_local']}/dc_api/v1/get/{config['ip']}"
    response = requests.get(url)
    data = response.json()
    
    if data.get('code') == 200:
        names = [item['name'] for item in data.get('data', [])]
        print(f"Found {len(names)} machines: {names}")
        return names
    else:
        print(f"Failed to get machine list: {data}")
        return []

def stop_machines_all(names, config):
    """Stop all machines in the name list"""
    for name in names:
        url = f"http://{config['host_local']}/dc_api/v1/stop/{config['ip']}/{name}"
        response = requests.get(url)
        print(f"stop_docker {name} >>>> {response.text}")

def stop_docker(index: int, phone: str, config):
    name = f"T100{index}-{phone}"
    #get /dc_api/v1/run/{ip}/{name}
    url = f"http://{config['host_local']}/dc_api/v1/stop/{config['ip']}/{name}"
    response = requests.get(url)
    print(f"stop_docker T100{index}-{phone} >>>>{response.text}")

def stop_batch(config:dict):
    info_list = config["info_list"]
    for device_info in info_list:
        phone, index = device_info[0], device_info[1]
        stop_docker(index, phone, config)

if __name__ == "__main__":
    print("stop_machine excuting:")
    config = load_config()
    names = get_machine_namelist(config)
    stop_machines_all(names, config)
