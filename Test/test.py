# -*- encoding=utf8 -*-
__author__ = "34857"

from airtest.core.api import *
import subprocess
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

auto_setup(__file__)

result = subprocess.run("adb connect 192.168.124.15:5002", shell=True, capture_output=True, text=True)
print(result.stdout)
touch(Template(r"tpl1766727625112.png", record_pos=(-0.264, -0.231), resolution=(720, 1280)))

# Connect device in Airtest
connect_device("Android://127.0.0.1:5037/192.168.124.15:5002")
exists(Template(r"tpl1766718533150.png", record_pos=(-0.014, -0.136), resolution=(720, 1280)))
touch(Template(r"tpl1766727477620.png", record_pos=(0.051, -0.375), resolution=(720, 1280)))

touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629844196.png"), record_pos=(-0.386, 0.317), resolution=(720, 1280)))

if exists(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629849292.png"), record_pos=(0.018, 0.418), resolution=(720, 1280))):
    touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629849292.png"), record_pos=(0.018, 0.418), resolution=(720, 1280)))

sleep(25.0)  # Wait 20 seconds

keyevent("BACK")
keyevent("BACK")
keyevent("BACK")
keyevent("BACK")
keyevent("BACK")
keyevent("BACK")
keyevent("BACK")
# touch(Template(r"tpl1766642400576.png", record_pos=(-0.335, 0.45), resolution=(720, 1280)))

touch(Template(r"tpl1766712390329.png", record_pos=(0.389, -0.549), resolution=(720, 1280)))

touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629844196.png"), record_pos=(-0.386, 0.317), resolution=(720, 1280)))
touch(Template(r"tpl1766649447388.png", record_pos=(0.357, -0.426), resolution=(720, 1280)))

sleep(15)
if exists(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629957359.png"), record_pos=(0.399, 0.844), resolution=(720, 1280))):
    touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766629957359.png"), record_pos=(0.399, 0.844), resolution=(720, 1280)))

touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766630007249.png"), record_pos=(-0.374, 0.229), resolution=(720, 1280)))
touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766630010007.png"), record_pos=(-0.062, 0.06), resolution=(720, 1280)))
touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766627868831.png"), record_pos=(-0.324, -0.013), resolution=(720, 1280)))
text("15327330452")
touch(Template(os.path.join(SCRIPT_DIR, r"img/tpl1766627887424.png"), record_pos=(-0.019, -0.122), resolution=(720, 1280)))
exists(Template(r"tpl1766733358148.png", record_pos=(-0.237, 0.804), resolution=(720, 1280)))

        #handle exception 
#         if exists((Template(os.path.join(self.script_dir, r"img/tpl1766712390329.png"), 
#              record_pos=(0.389, -0.549), resolution=(720, 1280)))
# ):
#             self._safe_touch("tpl1766712390329.png",record_pos=(0.018, 0.418)) #closeGift Icon
#             #Todo: click the translate butiion
#         else:
#             #Todo: clcik the translate button
#             self._safe_touch("tpl1766712390329.png",record_pos=(0.018, 0.418)) #closeGift Icon

        #