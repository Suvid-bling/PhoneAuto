import json
import time
from urllib.parse import urlparse
import os

import requests
from loguru import logger

# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Extract global config
global_config = config.get("global", {})
host_local = global_config.get("host_local")
domain = global_config.get("domain")
host_rpc = global_config.get("host_rpc")
update_account_url = global_config.get("update_account_url")

# For backward compatibility with single-IP config
if not host_local and "host_local" in config:
    host_local = config["host_local"]
    domain = config["domain"]
    host_rpc = config["host_rpc"]
    update_account_url = config["update_account_url"]

def qiehuan_device(ip, index):
    url = f"{domain}/android/changeDevice/"
    data = {
        "host": host_rpc,
        "ip": ip,
        "index": index,
    }
    response = requests.post(url, json=data)
    print(response.text)

def random_device(ip):
    url = f"{domain}/android/randomDeviceList/"
    data = {
        "host": host_rpc,
        "ip": ip,
    }
    response = requests.post(url, json=data)
    print(response.text)

def test_proxy():
    proxy="http://newtwitter2:zhxg123456@146.103.55.145:6197"
    url = 'https://www.baidu.com'
    proxies = {
        'http': proxy,
        'https': proxy
    }

    response = requests.get(url, proxies=proxies)
    print(response.text)

def change_login_state(data):
    url = f"{domain}/android/change_login_state/"
    response = requests.post(url, json=data)
    print(response.text)

def delete_docker(ip, index: int, phone: str):
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/remove/{ip}/{name}"
    response=requests.get(url)
    print(f"delete_docker T100{index}-{phone} >>>>{response.text}")

def updateAccountHeaders(ip):
    # check: 检查账号状态
    data={
        "host": host_rpc,
        "ip": ip
    }
    response = requests.post(update_account_url, data=json.dumps(data))
    print(response.text)

def script_mua( url, method="GET", body=""):
    """

    :param lamda_port:
    :param device_ip:
    :param url:
    :param code: 8.81.0:-1726371244,8.83.0:-1721529429
    :return:
    """
    try:
        parsed_url = urlparse(url)
        # mua_url = f"http://36.133.80.179:7152/1-zhxg-172_16_42_55-T1005/script/com.xingin.xhs/calla?user=0"
        # mua_url = f"http://36.133.80.179:7152/2-3001-192_168_124_18-T1007/script/com.xingin.xhs/calla?user=0"
        mua_url = f"http://192.168.124.19:65005/script/com.xingin.xhs/calla?user=0"
        res = requests.post(mua_url, data={
            "args": json.dumps([[method, parsed_url.netloc, parsed_url.path, parsed_url.query, body]])
        }, timeout=10)
        mua_resp = res.json().get("result")
        # mua_json = parse_to_json_advanced(mua_resp)
        print( mua_resp)
        return mua_resp
    except Exception as e:
        print(e)
        # traceback.print_exc()
    return None


def start_lamda(dip,dname):
    url = f"{domain}/rpc/startLamda/"
    data = {
        "host": host_rpc,
        "ip":  dip,
        "name": dname
    }
    try:
        response = requests.post(url, json=data, timeout=60 * 3)
        print(response.text)
    except Exception as e:
        logger.error(f"{dip}-{dname}:{e}")
        time.sleep(60)


def api_adb_shell(dip, dname, cmd_str: str, timeout=0):
    """执行adb的命令"""
    url = f"http://{host_rpc}/shell/{dip}/{dname}"
    data = {
        "cmd": cmd_str
    }
    try:
        if timeout == 0:
            response = requests.post(url, data=json.dumps(data))
        else:
            response = requests.post(url, data=json.dumps(data), timeout=timeout)
        logger.info(response.json())
        return response.json()
    except Exception as e:
        logger.error(e)
        return {"code": -1, "msg": str(e)}

def get_ip_devices(dip):
    url=f"http://{host_rpc}/dc_api/v1/list/{dip}"
    response = requests.get(url)
    return response.json()["data"]

def TransName(info_list):
    """
    Convert info_list format to push_device_names format
    Input: [['1753351192701747666172', 6, '', ''], 
            ['1753351076364595143022', 7, '', '']]
    Output: ['T1006-1753351192701747666172''T1007-1753351076364595143022']
    """
    result = []
    for item in info_list:
        phone, index = item[0], item[1]
        device_name = f"T100{index}-{phone}"
        result.append(device_name)
    return result
def kill_lamda(dip,dname):
    api_adb_shell(dip, dname, "kill -SIGUSR2 $(cat /data/usr/lamda.pid)", timeout=10)
    time.sleep(30)
    api_adb_shell(dip, dname, "ps -ef |grep lamda|grep -v grep| awk '{print $2}' | xargs kill -9", timeout=10)

def uninstall_lamda(dip, dname,):
    api_adb_shell(dip, dname, "rm -rf /data/server /data/usr", timeout=10)
    api_adb_shell(dip, dname, "rm -rf /data/local/tmp/lamda-server-arm64-v8a.tar.gz", timeout=10)
def update_new_wenjian(dip,android_data):
    file_name_list = ["xhs.9.7.0.spawn.yaml", "lamda-server-arm64-v8a.tar.gz"]
    #push_file_to_android(dip, android_data=android_data, file_name_list=file_name_list)

def run_install(dip,dname):
    shell_command = 'chmod 755 /data/local/tmp/busybox-arm64-v8a&&cd /data&&/data/local/tmp/busybox-arm64-v8a tar -xzf /data/local/tmp/lamda-server-arm64-v8a.tar.gz'
    api_adb_shell(dip,dname, shell_command, 60)
def copy_yaml(dip,dname):
    api_adb_shell(dip,dname,"cp /data/local/tmp/xhs.9.7.0.spawn.yaml /data/usr/modules/script/xhs.9.7.0.spawn.yaml", timeout=10)


def update_lamda_and_yaml(ip):
    devices = get_ip_devices(ip)
    for device in devices:
        try:
            if device['state'] !='running':
                logger.info(f"设备没开机:{ip} {device['name']}")
                continue
            one_device_name = device["name"]
            logger.info(f"设备开始切换:{ip} {one_device_name}")
            start_lamda(ip, one_device_name)
            logger.success("启动lamda完成")
            logger.info(f"设备切换完成:{ip} {one_device_name}")
        except Exception as e:
            logger.error(e)



if __name__ == '__main__':
    # For backward compatibility, try to get info_list from old config format
    info_list = config.get("info_list", [])
    if not info_list and "ips" in config:
        # Get first IP's info_pool as example
        first_ip = list(config["ips"].keys())[0]
        info_list = config["ips"][first_ip].get("info_pool", [])
    
    # Generate device names from config info_list
    device_names = [f"T100{item[1]}-{item[0]}" for item in info_list]
    
    # Use TransName function to convert info_list to device names
    push_device_names = TransName(info_list)
    
    change_login_state(push_device_names)