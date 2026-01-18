import requests
import json

import json
import os
import requests

def change_proxy_by_name(device_name):
    url = 'http://192.168.223.144:9000/android/change_proxy_by_name'
    headers = {'Content-Type': 'application/json'}
    data = [device_name]
    
    response = requests.post(url, headers=headers, json=data)
    return response

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    info_list = config.get('info_list', [])
    
    for item in info_list:
        phone_number = item[0]
        index = item[1]
        device_name = f"T100{index}-{phone_number}"
        print(f"Processing device: {device_name}")
        result = change_proxy_by_name(device_name)
        print(f"Status Code: {result.status_code}")
        print(f"Response: {result.text}")
        print("-" * 50)
