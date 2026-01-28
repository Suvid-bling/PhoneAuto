import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import asyncio
import pprint
import redis
from multiprocessing import Pool
from functools import partial
from MachineManage.tools import change_login_state,TransName
import json
#from xhs_crawler.XhsInterfaceService import XhsInterfaceService
import requests

# Load configuration from JSON file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: Could not load config.json at {config_path}: {e}")
    config = {'global': {}}

# Extract configuration values from global section
global_config = config.get('global', {})
domain = global_config.get('domain', '')
host_local = global_config.get('host_local', '')
host_rpc = global_config.get('host_rpc', '')
redis_url = global_config.get('redis_url', '')
update_account_url = global_config.get('update_account_url', '')

# These need to be specified - using placeholder for now
ip = None  # TODO: Specify which IP to use
info_list = []  # TODO: Specify which info_list to use
async def initial_test(number: str, index: str):
    """测试账号是否可用"""
    await XhsInterfaceService.init(redis_url)
    resp = await XhsInterfaceService.user_feed(user_profile_id="67853ac9000000000801b179", account_id=f"T100{index}-{number}")
    #pprint.pprint(resp)
    await XhsInterfaceService.close()
    return resp

def start_lamda(index: int, phone: str):
    """启动lamda服务"""
    url = f"{domain}/rpc/startLamda/"
    data = {
        "host": host_local,
        "ip": ip,
        "index": index,
        "name": f"T100{index}-{phone}",
    }
    response = requests.post(url, json=data)
    print(f"start_lamda T100{index}-{phone} >>>>{response.text}")

def update_accountlist(ip: str, host_rpc: str, device_info_list: list, update_account_url: str) -> list:
    """
    Update account list on server and return failed devices.
    
    Args:
        ip: IP address for the devices
        host_rpc: RPC host address
        device_info_list: List of device info [phone, index, "", ""]
        update_account_url: URL for updating account list
        
    Returns:
        List of Device_Info that failed (logged out devices)
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "host": host_rpc,
        "ip": ip
    }
    
    try:
        response = requests.post(update_account_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        device_statuses = {}
        logout_devices = []
        
        if result.get("code") == 0 and "data" in result:
            # 将响应数据转换为字典
            for entry in result["data"]:
                device_statuses.update(entry)
            
            # 打印所有设备状态并收集需要重新登录的设备
            for phone, index, _, _ in device_info_list:
                device_name = f"T100{index}-{phone}"
                status = device_statuses.get(device_name, "未找到")
                print(f"{device_name}: {status}")
                
                # 检查是否包含退出登录的描述
                if "-100 账号退出登录,请删除或者重新登陆" in status:
                    logout_devices.append([phone, index, "", ""])
        
        return logout_devices
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating account list: {e}")
        return []

def check_accountlist_hook(ip: str, host_rpc: str, device_info_list: list, update_account_url: str) -> list:
    """
    Update account list on server and return failed devices.
    
    Args:
        ip: IP address for the devices
        host_rpc: RPC host address
        device_info_list: List of device info [phone, index, "", ""]
        update_account_url: URL for updating account list
        
    Returns:
        List of Device_Info that failed (logged out devices)
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "host": host_rpc,
        "ip": ip
    }
    
    try:
        response = requests.post(update_account_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        device_statuses = {}
        hookout_devices = []
        
        if result.get("code") == 0 and "data" in result:
            # 将响应数据转换为字典
            for entry in result["data"]:
                device_statuses.update(entry)
            
            # 打印所有设备状态并收集需要重新登录的设备
            for phone, index, _, _ in device_info_list:
                device_name = f"T100{index}-{phone}"
                status = device_statuses.get(device_name, "未找到")
                print(f"{device_name}: {status}")
                
                # 检查是否包含退出登录的描述
                if "hook RPC异常,lamda是否启动:True" in status:
                    print("hook RPC异常,lamda是否启动:True")
                    return False

        return True
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating account list: {e}")
        return []


def test_account():
    """Test account status for each phone number in the config"""
    print(f"Testing accounts for IP: {ip}")
    
    # Get all device statuses at once
    #device_statuses = update_accountlist(ip, host_rpc, info_list, update_account_url)

    
    print("-" * 50)

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    ip = "192.168.124.68"


    status = update_accountlist(ip, host_rpc, info_list, update_account_url)

