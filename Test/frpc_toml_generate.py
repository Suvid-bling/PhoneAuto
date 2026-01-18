#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/11/20 16:45
# @Author : 赵金林
# @Desc :
import requests


def add(name, port):
    url = "http://36.133.80.179:7152/gateway/add/"
    # 更新可用
    # url = "http://36.133.80.179:7152/gateway/update/"

    payload = {
        "id": name,
        "predicates": [
            {
                "name": "Path",
                "args": {
                    "_genkey_0": f"/{name}/**"
                }
            }
        ],
        "filters": [
            {
                "name": "StripPrefix",
                "args": {
                    "_genkey_0": "1"
                }
            }
        ],
        "uri": f"http://127.0.0.1:{port}",
        "order": 0
    }

    response = requests.post(url, json=payload)

    print(response.text)

def create_frpc_config(device_count,device_ip):
    # device_count = 9
    # network_name = "3001"
    network_name="zhxg"
    # device_ip = "192_168_124_68"

    toml = """
    serverAddr = "36.133.80.179"
    serverPort = 8888
    auth.token = "88888888"
        """
    for index in range(1, 9):
        name = f"{device_count}-{network_name}-{device_ip}-T100{index}"
        port = 65000 + (device_count - 1) * 20 + index
        toml_file = f"""
    [[proxies]]
    name = "{name}"
    type = "tcp"
    localIP = "127.0.0.1"
    localPort = 6500{index}
    remotePort = {port}
            """
        toml += toml_file
        add(name, port)
    print("=================================")
    return toml
if __name__ == '__main__':
    toml_text=create_frpc_config(9,"192_168_124_68")
    print(toml_text)


