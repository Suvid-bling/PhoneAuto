#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import requests
from multiprocessing import Pool
from functools import partial
from PhoneInit import *
from InitTools import *

class PhoneInit:
    """Phone initialization and management class"""
    
    def __init__(self, ip):
        """
        Initialize PhoneInit with IP address only
        Auto-detects network configuration based on IP
        
        Args:
            ip (str): Current machine IP address
        """
        self.ip = ip
        
        # Auto-detect network configuration
        config = self._detect_config(ip)
        
        self.domain = config["domain"]
        self.host_local = config["host_local"]
        self.host_rpc = config["host_rpc"]
        self.image = config["image"]
        self.ip_dict = config["ip_dict"]
        self.gateway_route = f"http://36.133.80.179:7152/{self.ip_dict[ip]}-T100{{index}}"
    
    def _detect_config(self, ip):
        """Auto-detect configuration based on IP address"""
        if ip.startswith("192.168.124."):
            return CONFIGS["192_network"]
        elif ip.startswith("172.16."):
            return CONFIGS["172_network"]
        else:
            raise ValueError(f"Unknown network for IP: {ip}. Please add configuration.")
    
    def TransName(info_list):
        """
        Convert info_list format to push_device_names format
        Input: [['1753351192701747666172', 6, '', ''], ['1753351076364595143022', 7, '', '']]
        Output: ['T1006-1753351192701747666172', 'T1007-1753351076364595143022']
        """
        result = []
        for item in info_list:
            phone, index = item[0], item[1]
            device_name = f"T100{index}-{phone}"
            result.append(device_name)
        return result

    def create_docker(self, phone, index, send_code_url, verify_code_url):
        """Create docker container for phone"""
        url = f"{self.domain}/android/create/"
        data = {
            "phone": phone,
            "country_code": "+1",
            "verify_code_url": verify_code_url,
            "send_code_url": send_code_url,
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
                "name": f"T100{index}-{phone}",
                "image": self.image,
            }
        }
        
        response = requests.post(url, json=data)
        print(f"create_docker T100{index}-{phone} >>>>{response.text}")
        return response.text
    
    def start_lamda(self, index, phone):
        """Start Lambda service"""
        url = f"{self.domain}/rpc/startLamda/"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"start_lamda T100{index}-{phone} >>>>{response.text}")
    
    def random_device(self, index, phone):
        """Randomize device information"""
        url = f"{self.domain}/android/refreshDevice/"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"random_device T100{index}-{phone} >>>>{response.text}")
        result = response.json()
        
        if "false" in result.get("up", "upload_cert_success")\
        or "随机设备信息失败" in result.get("msg", ""):
            return False
        return True
    
    def delete_process(self, info_list):
        delete_list = self.TransName(info_list)
        delete_docker(self.ip, delete_list)
    
    def sid_login(self, index, phone):
        """Login using session ID"""
        url = f"{self.domain}/xhs/login_by_sid/?sessionNum={phone}"
        data = {
            "host": self.host_local,
            "ip": self.ip,
            "index": index,
            "name": f"T100{index}-{phone}",
        }
        response = requests.post(url, json=data)
        print(f"sid_login T100{index}-{phone} >>>>{response.text}")
    
    
    def create_process(self, info):
        """Create and initialize new device"""
        try:
            phone, index, send_code_url, verify_code_url = info
            print("=" * 63)
            print(f"CREATE - phone:{phone}, index:{index}")
            
            refresh = False
            while not refresh:
                self.create_docker(phone, index, send_code_url, verify_code_url)
                refresh = self.random_device(index, phone)
            
            self.start_lamda(index, phone)
            print("=" * 63)
        except Exception as e:
            print(f"Error creating device {phone}: {e}")
    
    def login_process(self, info):
        """Login with existing session"""
        try:
            phone, index, send_code_url, verify_code_url = info
            print("=" * 63)
            print(f"LOGIN - phone:{phone}, index:{index}")
            
            self.sid_login(index=index, phone=phone)
            change_login_state(TransName(info),self.domain)
            self.start_lamda(index, phone)
            
            print("=" * 63)
        except Exception as e:
            print(f"Error logging in device {phone}: {e}")
    
    def print_process(self, info):
        """Print device information"""
        try:    
            phone, index, send_code_url, verify_code_url = info
            print("=" * 63)
            print(f"PRINT - phone:{phone}, index:{index}")
            print(f"send_code_url:{send_code_url}")
            print(f"verify_code_url:{verify_code_url}")
            print("=" * 63)
        except Exception as e:
            print(f"Error printing device {phone}: {e}")
    
    def batch_process(self, info_list, func_name='create_process', processes=2):
        if not hasattr(self, func_name):
            raise ValueError(f"Function '{func_name}' not found in PhoneInit class")
        
        func = getattr(self, func_name)
        
        with Pool(processes=processes) as pool:
            pool.map(func, info_list)


# Configuration presets
CONFIGS = {
    "192_network": {
        "domain": "http://192.168.124.5:8002",
        "host_local": "192.168.124.5:5000",
        "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
        "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202510101731",
        "ip_dict": {
            "192.168.124.15": "3-3001-192_168_124_17",
            "192.168.124.17": "3-3001-192_168_124_17",
            "192.168.124.18": "2-3001-192_168_124_18",
            "192.168.124.19": "4-3001-192_168_124_19",
            "192.168.124.60": "8-3001-192_168_124_60",
            "192.168.124.23": "6-3001-192_168_124_23",
            "192.168.124.26": "5-3001-192_168_124_26",
            "192.168.124.68": "9-3001-192_168_124_68",
        }
    },
    "172_network": {
        "domain": "http://172.16.162.64:8002",
        "host_local": "172.16.162.64:5000",
        "host_rpc": "36.133.80.179:7152/zhxg-MYTSDK",
        "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202510101731",
        "ip_dict": {
            "172.16.227.32": "10-zhxg-172_16_227_32",
            "172.16.212.171": "11-zhxg-172_16_212_171",
            "172.16.209.72": "12-zhxg-172_16_209_72",
            "172.16.42.55": "1-zhxg-172_16_42_55",
        }
    }
}
