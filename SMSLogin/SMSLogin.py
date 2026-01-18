import base64
import json
import time
import aircv as ac
import requests
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
from Auto import AutoPhone
import os
import random

# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

def call_SmsUrl(sms_url: str):
    """循环请求短信验证码直到获取到"""
    import re
    
    max_attempts = 15
    
    for attempt in range(max_attempts):
        response = requests.get(sms_url, timeout=10)
        data = response.json()
        print(data)
        
        # Search for 6-digit verification code anywhere in the entire JSON response
        json_str = json.dumps(data)
        match = re.search(r'\b(\d{6})\b', json_str)
        if match:
            code = match.group(1)
            print(f"获取到验证码: {code}")
            return code
        
        print(f"尝试 {attempt + 1}/{max_attempts}, 等待验证码...")
        time.sleep(2)
    
    print("超时未获取到验证码")
    return False


def get_SmsUrl(phone_number: str, file_path: str = "active_phonenumber.txt") -> str:
    import os
    import ast
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    full_path = os.path.join(project_root, "resources", file_path)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            data = ast.literal_eval(line.rstrip(','))
            if len(data) >= 4 and data[0] == phone_number:
                return data[3]

def login_process(device: dict):
    """Process login for a single device"""
    try:
        phone_number, index = device_info[0], device_info[1]
        sms_url = get_SmsUrl(phone_number)
        
        phone = AutoPhone(
            ip=config["ip"], 
            port=f"500{index}",
            host=config["host_local"],
            name=f"T100{index}-{phone_number}",
            auto_connect=False
        )
        
        phone._connect_device()
        #phone.clear_app_cache()
        phone.into_loginface()
        phone.send_sms(phone_number)
        code = call_SmsUrl(sms_url)        
        if not code:
            for retry_count in range(2):
                phone.resend_sms(phone_number)
                code = call_SmsUrl(sms_url)
                if code:
                    break
             
        phone.input_sms(code)   
        phone._disconnect_device()
    except Exception as e:
        print(f"Error in login_process for {device_info[0]}: {e}")
        pass



if __name__ == '__main__':
    import redis
    # Use info_list from config instead of hardcoded devices
    for device_info in config["info_list"]:
            login_process(device_info)