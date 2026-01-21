import os
import sys

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from setting import *
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
from Autolization.SovleCaptch import *
from Autolization.AutoXhs import XhsAutomation

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
    """循环请求短信验证码直到获取到，带重试逻辑处理SSL错误"""
    import re
    from requests.exceptions import SSLError, RequestException
    
    max_attempts = 18
    max_retries = 3
    
    for attempt in range(max_attempts):
        for retry in range(max_retries):
            try:
                response = requests.get(sms_url, timeout=10)
                data = response.json()
                print(data)
                
                json_str = json.dumps(data)
                match = re.search(r'\b(\d{6})\b', json_str)
                if match:
                    print(f"获取到验证码: {match.group(1)}")
                    return match.group(1)
                break
                
            except (SSLError, RequestException) as e:
                wait_time = 2 ** (retry + 1)
                print(f"\033[91m连接错误 (重试 {retry + 1}/{max_retries}): {e}\033[0m")
                if retry < max_retries - 1:
                    time.sleep(wait_time)
        
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

def relogin_process(device_info: list):
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
        
        xhs = XhsAutomation(phone)
        xhs.reinto_loginface()
        xhs.send_sms(phone_number)
        "check point for solve verficate img by human's hand"
        #Todo: add am ask process that pause the thread until user input 'y'
        #wait_for_user_confirmation(phone_number)  # Pauses this thread until 'y'
        code = call_SmsUrl(sms_url)        
        if not code:
            for retry_count in range(2):
                xhs.resend_sms(phone_number)
                code = call_SmsUrl(sms_url)
                if code:
                    break

        print(f"[{phone_number}] 获取到验证码: {code}")
        time.sleep(5) #assum as human type 
        xhs.input_sms(code)
        time.sleep(10)

        if not xhs.check_loginState():
            append_configs("failure_list",device_info)
        
        phone._disconnect_device()
    except Exception as e:
        print(f"Error in login_process for {device_info[0]}: {e}")
        pass


if __name__ == '__main__':

    from concurrent.futures import ProcessPoolExecutor

    # Use multiprocessing to process multiple devices in parallel
    with ProcessPoolExecutor(max_workers=3) as executor:
        executor.map(relogin_process, config["info_list"])
