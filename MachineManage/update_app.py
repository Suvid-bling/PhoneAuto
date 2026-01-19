import json
import requests
import time
import logging

logger = logging.getLogger(__name__)

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config["domain"]
host_rpc = config["host_rpc"]
ip = config["ip"]
info_list = config["info_list"]

def updateApp(dip, dname):
    url = f"{domain}/android/upload_xhs_app/?apk_name=xhs9.15.0.apk"
    data = {
        "host": host_rpc,
        "ip": dip,
        "name": dname
    }
    try:
        response = requests.post(url, json=data, timeout=60 * 3)
        print(response.text)
    except Exception as e:
        logger.error(f"{dip}-{dname}:{e}")
        time.sleep(60)

if __name__ == "__main__":
    # Loop through info_list
    for info in info_list:
        account_id = info[0]
        device_num = info[1]
        dname = f"T100{device_num}-{account_id}"
        
        print(f"Updating app for {ip}-{dname}")
        updateApp(ip,dname)