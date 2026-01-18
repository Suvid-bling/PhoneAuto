# -*- encoding=utf8 -*-
__author__ = "34857"

from airtest.core.api import *
import subprocess

auto_setup(__file__)

# Connect to device via ADB
print("Connecting to device...")
result = subprocess.run("adb connect 192.168.124.15:5001", shell=True, capture_output=True, text=True)
print(result.stdout)

# Connect device in Airtest
connect_device("Android://127.0.0.1:5037/192.168.124.15:5001")
print("Device connected!")

# Perform touch actions
touch(Template(r"tpl1766624614799.png", record_pos=(-0.365, 0.333), resolution=(720, 1280)))
touch(Template(r"tpl1766624618972.png", record_pos=(0.36, 0.667), resolution=(720, 1280)))
touch(Template(r"tpl1766624622198.png", record_pos=(-0.374, 0.128), resolution=(720, 1280)))
touch(Template(r"tpl1766624624114.png", record_pos=(-0.028, -0.021), resolution=(720, 1280)))

print("Script completed!")
