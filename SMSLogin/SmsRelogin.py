import os
import sys

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import json
import time
import aircv as ac
import requests
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
import random
import threading

from Autolization.AutoOperate import AutoPhone

# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
user_confirmation_lock = threading.Lock()

def wait_for_user_confirmation(phone_number: str):
    """Thread-safe user confirmation - only one thread can ask at a time"""
    with user_confirmation_lock:
        while True:
            response = input(f"[{phone_number}] Solve verification image, then press 'y' to continue: ").strip().lower()
            if response == 'y':
                print(f"[{phone_number}] Continuing...")
                break
            else:
                print(f"[{phone_number}] Invalid input. Please enter 'y'")

def call_SmsUrl(sms_url: str):
    """循环请求短信验证码直到获取到"""
    import re
    
    max_attempts = 18
    
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
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                data = ast.literal_eval(line.rstrip(','))
                if len(data) >= 4 and data[0] == phone_number:
                    return data[3]
        
        # If we reach here, phone_number was not found
        raise ValueError(f"Phone number '{phone_number}' not found in {file_path}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found")
    except (ValueError, SyntaxError) as e:
        if "not found" in str(e):
            raise e
        raise ValueError(f"Error parsing data in {file_path}: {e}")

def login_process(device_info: list):
    """Process login for a single device
    Args:
        device_info: List in format [phone_number, index, "", ""] matching info_list format
    """
    try:
        phone_number, index = device_info[0], device_info[1]
        sms_url = get_SmsUrl(phone_number)
        print(f"[{phone_number}] Starting login...")

        phone = AutoPhone(
            ip=config["ip"], 
            port=f"500{index}",
            host=config["host_local"],
            name=f"T100{index}-{phone_number}",
            auto_connect=False
        )
        
        phone._connect_device()
        phone.clear_app_cache("com.xingin.xhs")  # Clear only xiaohongshu cache
        phone.reinto_loginface()
        phone.send_sms(phone_number)
        "check point for solve verficate img by human's hand"
        #Todo: add am ask process that pause the thread until user input 'y'
        wait_for_user_confirmation(phone_number)  # Pauses this thread until 'y'
        code = call_SmsUrl(sms_url)        
        if not code:
            for retry_count in range(2):
                phone.resend_sms(phone_number)
                code = call_SmsUrl(sms_url)
                if code:
                    break

        print(f"[{phone_number}] 获取到验证码: {code}")
        time.sleep(5)
        phone.input_sms(code)   
        phone._disconnect_device()
    except Exception as e:
        print(f"Error in login_process for {device_info[0]}: {e}")
        pass


if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor
    manual_mode = False
    if manual_mode:
        for device_info in config["info_list"]:
            login_process(device_info)
    else:
        # Use threading to process multiple devices in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(login_process, config["info_list"])
    