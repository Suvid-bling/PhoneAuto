import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import asyncio
import pprint
import redis
import requests
from multiprocessing import Pool
from functools import partial
from MachineManage.tools import change_login_state,TransName
from Autolization.AutoOperate import AutoPhone
import json

# Load configuration from JSON file
CONFIG_FILE = "config.json"
SELECTED_IP = "192.168.124.60"  # Change this to select different IP

config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract global configuration variables
ip_dict = config["global"]["ip_dict"]
domain = config["global"]["domain"]
image = config["global"]["image"]
host_local = config["global"]["host_local"]
host_rpc = config["global"]["host_rpc"]
redis_url = config["global"]["redis_url"]
update_account_url = config["global"]["update_account_url"]

# Extract IP-specific configuration
ip = "192.168.124.68"
if ip not in config["ips"]:
    raise ValueError(f"IP {ip} not found in config.json")

ip_config = config["ips"][ip]
info_list = ip_config["info_list"]

gateway_route = "http://36.133.80.179:7152/"+ip_dict[ip]+"-T100{index}" # 远程RPC地址 

def reupload_cert(index, phone):
    """Re-upload certificate"""
    url = f"{domain}/keybox/upload_cert"
    data = {
        "host": host_rpc,
        "ip": ip,
        "name": f"T100{index}-{phone}",
    }
    response = requests.post(url, json=data)
    print(f"reupload_cert T100{index}-{phone} >>>>{response.text}")
    
    try:
        result = response.json()
        message = result.get("message", "")
        print(f"Response message: {message}")
        return "上传证书成功" in message
    except Exception as e:
        print(f"Error parsing response: {e}")
        return False

def random_device(index, phone):
        """Randomize device information"""
        url = f"{domain}/android/refreshDevice/"
        data = {
            "host": host_local,
            "ip": ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"random_device T100{index}-{phone} >>>>{response.text}")
        result = response.json()
        
        if not result.get("data", {}).get("upload_cert_success", False):
            for attempt in range(3):  # Try up to 3 times
                if reupload_cert(index, phone):
                    break
                time.sleep(1)
            else:
                # Loop completed without break - all retries failed
                print(f"Failed to upload cert after 3 attempts for T100{index}-{phone}")
                return False

        msg = result.get("msg", "")
        if "随机设备信息失败" in msg or "设置代理失败" in msg:
            return False

        
        return True

def create_docker(phone: str, index: int,sendCodeUrl,verifyCodeUrl):

    url = f"{domain}/android/create/?apk_name=xhs9.15.0.apk&yaml_name=xhs.9.15.0.spawn.resp.yaml"
    data = {
        "phone": phone,
        "country_code": "+1",
        "verify_code_url": verifyCodeUrl,
        "send_code_url": sendCodeUrl,
        "expire_time": "2026-01-27",
        "proxy": "",
        "gateway_route": gateway_route.format(index=index),
        "sid": "",
        "device_id": "",
        "is_login": 0,
        "login_count": 0,
        "operation": {
            "host": host_rpc,
            "ip": ip,
            "index": index,
            "name": f"T100{index}-{phone}",
            "image": image,
        }
    }

    response = requests.post(url, json=data)
    print(f"create_docker T100{index}-{phone} >>>>{response.text}")
    return response.text


def delete_docker(index: int, phone: str):
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/remove/{ip}/{name}"
    response=requests.get(url)
    print(f"delete_docker T100{index}-{phone} >>>>{response.text}")


def sid_login(index:int, phone:str):
    url = f"{domain}/xhs/login_by_sid/?sessionNum={phone}"
    data = {
        "host": host_local,
        "ip": ip,
        "index": index,
        "name": f"T100{index}-{phone}",
    }
    response = requests.post(url, json=data)
    print(f"sid_login T100{index}-{phone} >>>>{response.text}")

def process_device(info,IFlogin):
    """处理单个设备的函数"""
    try:
        _phone, _index, _sendCodeUrl, _verifyCodeUrl = info
        print("===============================================================")
        print(f"phone:{_phone},index:{_index}")

        for attempt in range(3):  # Try up to 3 times
            create_result = create_docker(_phone, _index, _sendCodeUrl, _verifyCodeUrl)
            
            if random_device(_index, _phone):
                # Success, break out of loop
                print(f"\033[92mSuccessfully created android docker: T100{_index}-{_phone}\033[0m")
                break
            else:                    
                # Failed, delete docker and retry
                delete_docker(_index, _phone)
                if attempt < 2:  # Don't print on last attempt
                    print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
        else:
            # Loop completed without break - all retries failed
            print(f"\033[91mFailed to create android docker after 3 attempts: T100{_index}-{_phone}\033[0m")
            return False

        """设置锁屏和指纹"""
        phone = AutoPhone(
            ip=ip, 
            port=f"500{_index}",
            host=host_local, 
            name=f"T100{_index}-{_phone}",
            auto_connect=False
        )
        phone.set_screenlock("1234")
        phone.set_fingerprint()
        
        # """sid登录"""    
        # if IFlogin:
        #     phone.Agree_GoHome()
        #     sid_login(index=_index, phone=_phone)
        
        # """phoneNumber登录"""
        # if IFlogin:
        #     phone.Agree_GoHome()
        #     sid_login(index=_index, phone=_phone)
        
        print("===============================================================")
    except Exception as e:
        print(e)
        """http://36.133.80.179:8890/static/?wework_cfm_code=OKWADzu9TeaQeTN%2FFPtcxbhoGb4%2FvzQFGazBzl6W6ugKLUHLDErCphQPvV3mI%2FomqshQZUKMAlqRVQe7XjQj2LtiYqyTZ763YOZQjgOOV2Ho#/proxies/tcp"""


if __name__ == '__main__':

    with Pool(processes=2) as pool:
        pool.map(partial(process_device, IFlogin=False), info_list)


