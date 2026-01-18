import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import asyncio
import pprint
import redis
from SMSLogin.Auto import AutoPhone
import requests
from multiprocessing import Pool
from functools import partial
from MachineManage.tools import change_login_state,TransName
import json
from xhs_crawler.XhsInterfaceService import XhsInterfaceService

# Load configuration from JSON file
CONFIG_FILE = "config.json"  # Change this to switch between configs
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract configuration variables
ip_dict = config["ip_dict"]
domain = config["domain"]
image = config["image"]
host_local = config["host_local"]
host_rpc = config["host_rpc"]
redis_url = config["redis_url"]
update_account_url = config["update_account_url"]
ip = config["ip"]
info_list = config["info_list"]

gateway_route = "http://36.133.80.179:7152/"+ip_dict[ip]+"-T100{index}" # 远程RPC地址 

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
        
        if not result.get("data", {}).get("upload_cert_success", False)\
        or "随机设备信息失败" in result.get("msg", ""):
            return False
        return True

def create_docker(phone: str, index: int,sendCodeUrl,verifyCodeUrl):

    url = f"{self.domain}/android/create/?apk_name=xhs9.15.0.apk&yaml_name=xhs.9.15.0.spawn.resp.yaml"
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
            refresh = random_device(_index, _phone)
            retry_count = 0
            while not refresh and retry_count < 4:
                refresh = random_device(_index, _phone)
                retry_count += 1
            
            if refresh:
                break  # Success, exit the for loop
            else:
                # Failed after 3 retries, delete docker and try again
                delete_docker(_index, _phone)
                if attempt < 3:  # Don't print on last attempt
                    print(f"Attempt {attempt + 1} failed, retrying...")
        
        if not refresh:
            print(f"Failed to refresh after 3 attempts for phone: {_phone}")
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


