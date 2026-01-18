#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/11/27 18:47
# @Author : 赵金林
# @Desc :
import requests
from multiprocessing import Pool


class InitDevice:
    def __init__(self, ip):
        self.domain = "http://192.168.124.5:8002"  # 和魔云藤机器同一个网络的服务,为了上传证书
        # self.domain = "http://127.0.0.1:8002"  # 和魔云藤机器同一个网络的服务,为了上传证书
        init_dict = {
            "192.168.124.26": {
                "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                "host_local": "192.168.124.5:5000",
                "gateway_route": "http://36.133.80.179:7152/5-3001-192_168_124_26-T100{index}",  # 远程RPC地址
                "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202510101731"  # MYT-CQ12-BASE-v24.12.0

                # "image":  "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202508141406" #镜像 MYT-CQ12-BASE-v24.11.2
            },
            "192.168.124.23":{
                "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                "host_local": "192.168.124.5:5000",
                "gateway_route": "http://36.133.80.179:7152/6-3001-192_168_124_23-T100{index}",  # 远程RPC地址
                "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202510101731"  # MYT-CQ12-BASE-v24.12.0
            },
            "192.168.124.19": {
                "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                "host_local": "192.168.124.5:5000",
                "gateway_route": "http://36.133.80.179:7152/4-3001-192_168_124_19-T100{index}",  # 远程RPC地址
                "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202508141406" #镜像 MYT-CQ12-BASE-v24.11.2
                # MYT-CQ12-BASE-v24.12.0
            },
            "192.168.124.15": {
                "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                "host_local": "192.168.124.5:5000",
                "gateway_route": "http://36.133.80.179:7152/4-3001-192_168_124_15-T100{index}",  # 远程RPC地址
                "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202508141406" #镜像 MYT-CQ12-BASE-v24.11.2
                # MYT-CQ12-BASE-v24.12.0
            }
        }
        self.ip = ip #192.168.124.15 
        self.host_rpc = init_dict[ip]["host_rpc"]
        self.host_local = init_dict[ip]["host_local"]
        self.gateway_route = init_dict[ip]["gateway_route"]
        self.image = init_dict[ip]["image"]

    def create_docker(self, phone: str, index: int, sendCodeUrl, verifyCodeUrl):
        url = f"{self.domain}/android/create/"
        data = {
            "phone": phone,
            "country_code": "+1",
            "verify_code_url": verifyCodeUrl,
            "send_code_url": sendCodeUrl,
            "expire_time": "2026-01-27",
            "proxy": "",
            "gateway_route": self.gateway_route.format(index=index),
            "sid": "",
            "device_id": "",
            "is_login": 0,
            "login_count": 0,
            "operation": {
                "host": self.host_rpc,
                "ip": self.ip,
                "index": index,
                "name": f"T100{index}",
                "image": self.image,
            }
        }

        response = requests.post(url, json=data)
        print(f"create_docker T100{index}-{phone} >>>>{response.text}")

    def start_lamda(self, index: int, phone: str):
        url = f"{self.domain}/rpc/startLamda/"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"start_lamda T100{index}-{phone} >>>>{response.text}")

    def random_device(self, index: int, phone: str):
        url = f"{self.domain}/android/refreshDevice/"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"random_device T100{index}-{phone} >>>>{response.text}")
        return response.json()

    def sid_login(self, index: int, phone: str):
        url = f"{self.domain}/xhs/login_by_sid/?sessionNum={phone}"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"sid_login T100{index}-{phone} >>>>{response.text}")


def process_device(info):
    """处理单个设备的函数"""
    try:
        _phone, _index, _sendCodeUrl, _verifyCodeUrl = info
        print("===============================================================")
        print(f"phone:{_phone},index:{_index}")
        init = InitDevice(ip = "192.168.124.15") #origin:192.168.124.19
        #init.create_docker(_phone, _index, _sendCodeUrl, _verifyCodeUrl)
        init.random_device(_index, _phone)

        print("===============================================================")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    info_list = [
        ['4508371979', 1, 'http://api.sms28.top/uuid-page/255cd4c5b8f84d929e288b4962734036', 
                     'https://sms2api.com/sms/by_key?key=23f9920f7fad48eaaeef791e7fc3887d'],
      #  ['175335107545128', 2, '', ''],
    
    ]

    with Pool(processes=2) as pool:
        # Map the process_device function to each item in info_list
        # Each item will be processed in parallel by the worker processes
        pool.map(process_device, info_list)
