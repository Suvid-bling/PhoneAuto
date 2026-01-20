import json
import os
import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def start_docker(index: int, phone: str, config):
    name = f"T100{index}-{phone}"
    #get /dc_api/v1/run/{ip}/{name}
    url = f"http://{config['host_local']}/dc_api/v1/run/{config['ip']}/{name}"
    response = requests.get(url)
    print(f"run_docker T100{index}-{phone} >>>>{response.text}")

def start_batch(config:dict):
    info_list = config["info_list"]
    
    for device_info in info_list:
        phone, index = device_info[0], device_info[1]
        start_docker(index, phone, config)

if __name__ == "__main__":
    config = load_config()
    start_batch(config)