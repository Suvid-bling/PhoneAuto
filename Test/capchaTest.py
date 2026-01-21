import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Autolization.AutoOperate import AutoPhone
from Autolization.AutoXhs import XhsAutomation

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

if __name__ == '__main__':
        phone = AutoPhone(
        ip=config["ip"], 
        port=f"5008",
        host=config["host_local"],
        name=f"T1008-4386643899",
        auto_connect=False
    )
        xhs = XhsAutomation(phone)
        xhs.swipe_fullcapcha()