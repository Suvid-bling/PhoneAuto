import json
import requests
import time
import logging
import sys
import os

# Add parent directory to path to import setting module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from setting import load_config

logger = logging.getLogger(__name__)

# Load config
config = load_config()
domain = config["global"]["domain"]
host_rpc = config["global"]["host_rpc"]


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

        updateApp("192.168.124.68","T1002-4385542539")