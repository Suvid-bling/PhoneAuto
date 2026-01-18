import json
import time
from urllib.parse import urlparse
from APIService.InitService import *
import requests
from loguru import logger

#from service.file_service import push_file_to_android

def qiehuan_device(index):

    url = "http://127.0.0.1:8002/android/changeDevice/"
    data = {
        "host": "36.133.80.179:7152/3001-MYTSDK",
        "ip":  "192.168.124.17",
        "index": index,

    }
    response = requests.post(url, json=data)
    print(response.text)

def random_device():

    url = "http://127.0.0.1:8002/android/randomDeviceList/"
    data = {
        "host": "36.133.80.179:7152/3001-MYTSDK",
        "ip":  "192.168.124.17",

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

def change_login_state(data,domain):
    
    url = f"{domain}/android/change_login_state/"
    #url = "http://172.16.79.56:8002/android/change_Login_state/"
    response = requests.post(url, json=data)
    print(response.text)

#API service 
def delete_docker(ip,delete_list):
    for name in delete_list:
        url = f"http://127.0.0.1:5000/remove/{ip}/{name}"
        response=requests.get(url)
        print(f"delete_docker {name} >>>>{response.text}")
    return

def updateAccountHeaders():
    # check: 检查账号状态
    url="http://192.168.223.144:9000/android/updateAccountHeaders/"
    data={
        "host": "36.133.80.179:7152/3001-MYTSDK",
        "ip": "192.168.124.18"
    }
    response = requests.post(url, data=json.dumps(data))
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
    url = "http://172.16.162.64:8002/rpc/startLamda/"
    data = {
        "host": "36.133.80.179:7152/3001-MYTSDK",
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
    url = f"http://36.133.80.179:7152/3001-MYTSDK/shell/{dip}/{dname}"
    data = {
        # "cmd": "pm list packages"
        # "cmd": "pm install C:/Users/xieqi/Desktop/dongpeng_qq.apk"
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
    url="http://36.133.80.179:7152/3001-MYTSDK/dc_api/v1/list/{}".format(dip)
    response = requests.get(url)
    return response.json()["data"]


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


def update_lamda_and_yaml():
    one_ip = "192.168.124.17"
    devices = get_ip_devices(one_ip)
    for device in devices:
        try:
            if device['state'] !='running':
                logger.info(f"设备没开机:{one_ip} {device['name']}")
                continue
            one_device_name = device["name"]
            logger.info(f"设备开始切换:{one_ip} {one_device_name}")
            # kill_lamda(one_ip, one_device_name)
            # logger.success("杀掉lamda完成")
            # uninstall_lamda(one_ip, one_device_name)
            # logger.success("卸载lamda完成")
            # update_new_wenjian(one_ip, device["data"])
            # logger.success("更新文件完成")
            # run_install(one_ip, one_device_name)
            # logger.success("安装lamda完成")
            # time.sleep(5)
            start_lamda(one_ip, one_device_name)
            logger.success("启动lamda完成")
            # copy_yaml(one_ip, one_device_name)
            # logger.success("更新yaml完成")
            logger.info(f"设备切换完成:{one_ip} {one_device_name}")
        except Exception as e:
            logger.error(e)

    def reupload_cert(self, index, phone):
        """Re-upload certificate"""
        url = f"{self.domain}/android/reuploadCert/"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"reupload_cert T100{index}-{phone} >>>>{response.text}")