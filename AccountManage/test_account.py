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
with open(config_path, 'r') as f:
    config = json.load(f)

# Extract configuration values
domain = config['domain']
host_local = config['host_local']
ip = config['ip']
host_rpc = config['host_rpc']
info_list = config['info_list']
redis_url = config['redis_url']
update_account_url = config['update_account_url']
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

def update_accountlist(info_list: list, ip: str) -> dict:
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
        
        if result.get("code") == 0 and "data" in result:
            # 将响应数据转换为字典
            for entry in result["data"]:
                device_statuses.update(entry)
            
            # 打印所有设备状态
            for phone, index, _, _ in info_list:
                device_name = f"T100{index}-{phone}"
                status = device_statuses.get(device_name, "未找到")
                print(f"{device_name}: {status}")
        
        return device_statuses
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating account list: {e}")
        return {}
def test_account():
    """Test account status for each phone number in the config"""
    print(f"Testing accounts for IP: {ip}")
    
    # Get all device statuses at once
    device_statuses = update_accountlist(info_list, ip)
    
    print("-" * 50)

if __name__ == "__main__":

    test_account()

