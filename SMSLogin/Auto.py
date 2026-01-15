# -*- encoding=utf8 -*-
#__author__ = "34857"

import subprocess
import os
import random
import requests
import time
import aircv as ac
import base64
from PIL import Image, ImageDraw, ImageFont


class AutoPhone:
    def __init__(self, ip: str, port: str, host: str = "", name: str = "", auto_connect: bool = True):
        """
        Initialize AutoPhone with device IP and port
        
        Args:
            ip: Device IP address (e.g., "192.168.124.15")
            port: Device port (e.g., "5002")
            host: Host for API calls (e.g., "192.168.124.5:5000")
            name: Device name for API calls
            auto_connect: Whether to automatically connect on initialization
        """
        self.ip = ip
        self.port = port
        self.host = host
        self.name = name
        self.device_addr = f"{ip}:{port}"
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Connect to device if auto_connect is True
        if auto_connect:
            self._connect_device()
    
    def _connect_device(self):
        """Connect to Android device via ADB and Airtest"""
        import time
        
        # First, disconnect any existing connection to clear offline state
        subprocess.run(
            f"adb disconnect {self.device_addr}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"Disconnected from {self.device_addr}")
        time.sleep(1)
        
        # ADB connect with timeout
        result = subprocess.run(
            f"adb connect {self.device_addr}", 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=10  # 10 second timeout
        )
        print(f"ADB Connect: {result.stdout}")
        time.sleep(2)
        
        # Verify device is online before connecting Airtest
        check_result = subprocess.run(
            f"adb -s {self.device_addr} get-state",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "device" not in check_result.stdout:
            raise Exception(f"Device {self.device_addr} is offline. Try: adb disconnect {self.device_addr} && adb connect {self.device_addr}")
        
        print(f"Device connected: {self.device_addr}")
    
    def _disconnect_device(self):
        """Disconnect from Android device"""
        import time
        
        try:
            # Disconnect ADB
            result = subprocess.run(
                f"adb disconnect {self.device_addr}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"Disconnected from {self.device_addr}: {result.stdout.strip()}")
            time.sleep(1)
        except Exception as e:
            print(f"Error disconnecting: {e}")
        
    def get_screenshot_base64(self):
        """Get screenshot from device via API"""
        url = f"http://{self.host}/screenshots/{self.ip}/{self.name}/3"
        try:
            resp = requests.get(url)
            data = resp.json()
            return data.get("msg")
        except Exception as e:
            print(f"Error getting screenshot: {e}")
            return None

    def save_base64_as_image(self, base64_data, output_path):
        """Save base64 image data to file"""
        if base64_data.startswith('data:image'):
            comma_index = base64_data.find(',')
            if comma_index != -1:
                base64_data = base64_data[comma_index + 1:]
        
        try:
            image_data = base64.b64decode(base64_data)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def match_image(self, src_img_path, obj_img_path, threshold=0.7):
        """Match template image in source image using aircv"""
        try:
            src_img = ac.imread(src_img_path)
            obj_img = ac.imread(obj_img_path)
            match_result = ac.find_template(src_img, obj_img, threshold=threshold, rgb=True, bgremove=False)
            return match_result
        except Exception as e:
            print(f"Image matching failed: {e}")
            return None

    def draw_match_result(self, src_img_path, match_result, output_path="result.png"):
        """
        在源图像上标记匹配区域并保存结果
        
        参数:
        src_img_path: 源图像路径
        match_result: 匹配结果字典
        output_path: 输出图像路径
        """
        if match_result is None:
            print("未找到匹配区域")
            return
            
        # 打开源图像
        img = Image.open(src_img_path)
        draw = ImageDraw.Draw(img)
        
        # 获取匹配区域的位置和大小
        pos = match_result['rectangle']
        confidence = match_result['confidence']
        
        # 修复：将四个点的坐标转换为左上角和右下角的坐标
        x_coords = [point[0] for point in pos]
        y_coords = [point[1] for point in pos]
        left = min(x_coords)
        top = min(y_coords)
        right = max(x_coords)
        bottom = max(y_coords)
        
        # 绘制矩形标记匹配区域
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        
        # 添加置信度文本
        try:
            font = ImageFont.truetype("simhei.ttf", 16)
        except IOError:
            # 如果找不到中文字体，使用默认字体
            font = None
            
        text = f"匹配度: {confidence:.2f}"
        text_pos = (pos[0][0], pos[0][1] - 20)
        draw.text(text_pos, text, fill="red", font=font)
        
        # 保存结果图像
        img.save(output_path)
        print(f"匹配结果已保存至 {output_path}")

    def human_type_text(self, text, min_delay=0.1, max_delay=0.3):
        """
        Type text character by character with human-like delays
        
        Args:
            text: Text to type
            min_delay: Minimum delay between characters (seconds)
            max_delay: Maximum delay between characters (seconds)
        """
        for char in text:
            # Type single character
            self.api_adb_shell(f"input text '{char}'")
            # Random delay between characters to simulate human typing
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
        
        print(f"Typed '{text}' with human-like timing")

    def wait_for_image(self, img_name, timeout=50, threshold=0.7, interval=1):
        """
        Wait for an image to appear on screen (similar to airtest wait function)
        
        Args:
            img_name: Image filename in img/ directory
            timeout: Maximum time to wait in seconds
            threshold: Matching threshold (0.0-1.0)
            interval: Check interval in seconds
            
        Returns:
            dict: Match result if found, None if timeout
        """
        img_path = os.path.join(self.script_dir, f"img/{img_name}")
        
        if not os.path.exists(img_path):
            print(f"Template image not found: {img_path}")
            return None
        
        start_time = time.time()
        temp_screenshot = os.path.join(self.script_dir, "temp_wait_screenshot.png")
        
        print(f"Waiting for {img_name} (timeout: {timeout}s, threshold: {threshold})")
        
        while time.time() - start_time < timeout:
            # Get current screenshot
            screenshot_base64 = self.get_screenshot_base64()
            if not screenshot_base64:
                time.sleep(interval)
                continue
                
            # Save screenshot temporarily
            if not self.save_base64_as_image(screenshot_base64, temp_screenshot):
                time.sleep(interval)
                continue
            
            # Match template
            match_result = self.match_image(temp_screenshot, img_path, threshold)
            
            if match_result and match_result['confidence'] >= threshold:
                # Clean up temp file
                try:
                    os.remove(temp_screenshot)
                except:
                    pass
                    
                elapsed_time = time.time() - start_time
                print(f"Found {img_name} after {elapsed_time:.1f}s with confidence {match_result['confidence']:.2f}")
                return match_result
            
            time.sleep(interval)
        
        # Clean up temp file
        try:
            os.remove(temp_screenshot)
        except:
            pass
            
        print(f"Timeout waiting for {img_name} after {timeout} seconds")
        return None

    def wait_and_click(self, img_name, timeout=50, threshold=0.7, interval=1):
        """
        Wait for an image to appear and then click on it
        
        Args:
            img_name: Image filename in img/ directory
            timeout: Maximum time to wait in seconds
            threshold: Matching threshold (0.0-1.0)
            interval: Check interval in seconds
            
        Returns:
            bool: True if found and clicked, False if timeout
        """
        match_result = self.wait_for_image(img_name, timeout, threshold, interval)
        if match_result:
            x, y = match_result['result']
            self.pos_click(x, y)
            print(f"Clicked on {img_name}")
            return True
        return False

    def pos_click(self, x, y):
        """Click at specific coordinates using ADB"""
        return self.api_adb_shell(f"input tap {x} {y}")

    def element_exists(self, img_name, threshold=0.7):
        """
        Check if an element exists on screen immediately without waiting or clicking
        
        Args:
            img_name: Image filename in img/ directory
            threshold: Matching threshold (0.0-1.0)
            
        Returns:
            dict: Match result if found, None if not found
        """
        img_path = os.path.join(self.script_dir, f"img/{img_name}")
        
        if not os.path.exists(img_path):
            print(f"Template image not found: {img_path}")
            return None
        
        temp_screenshot = os.path.join(self.script_dir, "temp_exists_check.png")
        
        # Get current screenshot
        screenshot_base64 = self.get_screenshot_base64()
        if not screenshot_base64:
            print("Failed to get screenshot")
            return None
            
        # Save screenshot temporarily
        if not self.save_base64_as_image(screenshot_base64, temp_screenshot):
            print("Failed to save screenshot")
            return None
        
        # Match template
        match_result = self.match_image(temp_screenshot, img_path, threshold)
        
        # Clean up temp file
        try:
            os.remove(temp_screenshot)
        except:
            pass
        
        if match_result and match_result['confidence'] >= threshold:
            print(f"Element {img_name} exists with confidence {match_result['confidence']:.2f}")
            return match_result
        else:
            print(f"Element {img_name} not found")
            return None

    def random_sleep(self):
        time.sleep(random.randint(1, 3))
        
    def _safe_touch(self, img_name, record_pos, threshold=0.7, timeout=10, clickpos=False):
        """
        Safe touch method using aircv for image matching
        
        Args:
            img_name: Image filename in img/ directory
            record_pos: Fallback position coordinates (x, y)
            threshold: Matching threshold (0.0-1.0)
            timeout: Timeout in seconds
            clickpos: If True, click record_pos when image not found
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Try to wait and click using image matching first
        if self.wait_and_click(img_name, timeout, threshold):
            return True
        
        # If image matching fails and clickpos is True, use fallback position
        if clickpos:
            x, y = record_pos
            # Convert normalized coordinates to actual coordinates if needed
            if -1 <= x <= 1 and -1 <= y <= 1:
                # Assuming 720x1280 resolution as in original code
                actual_x = int((x + 1) * 720 / 2)
                actual_y = int((y + 1) * 1280 / 2)
            else:
                actual_x, actual_y = x, y
                
            self.pos_click(actual_x, actual_y)
            print(f"Clicked at fallback position ({actual_x}, {actual_y}) for {img_name}")
            return True
        
        print(f"Failed to click {img_name} and clickpos is False")
        return False
    
    def into_loginface(self):
        """
        Send SMS by automating the app flow
        
        Args:
            phone_number: Phone number to send SMS to
        """
        time.sleep(1)
        self.random_sleep()
        self._safe_touch("tpl1766629844196.png",record_pos=(-0.386, 0.317)) #start Icon 
        self.random_sleep()

        # Check if Agree Icon exists before clicking
        # if exists(Template(os.path.join(self.script_dir, r"img/tpl1766629849292.png"), 
        #                  record_pos=(0.018, 0.418), resolution=(720, 1280))):
        self._safe_touch("tpl1766629849292.png",record_pos=(0.018, 0.418)) #Agree Icon

        # Wait for homepage - using aircv approach
        self.wait_for_image("tpl1766713067778.png", timeout=50)  # Wait for homepage

        # if not exists(Template(os.path.join(self.script_dir, r"img/tpl1766630010007.png"), 
        #                   record_pos=(0.399, 0.844), resolution=(720, 1280))):
        self.random_sleep()
        self._safe_touch("tpl1766630010007.png", (0.399, 0.844),clickpos=True)  #clcik me to login
        self.random_sleep()
        time.sleep(2)

        self.exceptions_click()
        self.exceptions_click()
        
        self.random_sleep()
        self._safe_touch("tpl1766630007249.png", (-0.374, 0.229), threshold=0.5)    #clcik little circle
        self.random_sleep()
        self._safe_touch("tpl1766630010007.png", (-0.062, 0.06))  #clcik homepage login
        self.random_sleep()
        self._safe_touch("tpl1766627868831.png", (-0.324, -0.013))  #click second little circle
        self.random_sleep()
        self._safe_touch("tpl1766643959547.png", (-0.29, -0.438))  #clcick +86 to switch country
        self.random_sleep()
        self._safe_touch("tpl1766649447388.png", (0.357, -0.426))  #click +1
        self.random_sleep()
        return True
    
    def reinto_loginface(self):
        """
        Send SMS by automating the app flow
        
        Args:
            phone_number: Phone number to send SMS to
        """
        
        """
        self.random_sleep()
        
        if self.element_exists("tpl1766629844196.png"):
            self._safe_touch("tpl1766629844196.png",record_pos=(-0.386, 0.317)) #start Icon 
        self.random_sleep()

        # Wait for homepage - using aircv approach
        self.wait_for_image("tpl1768207957769.png", timeout=50) #wait for relogin 

        self._safe_touch("tpl1768207957769.png",record_pos=(0.003, 0.171)) #click login in agian 
        # if not exists(Template(os.path.join(self.script_dir, r"img/tpl1766630010007.png"), 
        #                   record_pos=(0.399, 0.844), resolution=(720, 1280))):
        # self.random_sleep()
        # self._safe_touch("tpl1766630010007.png", (0.399, 0.844),clickpos=True)  #clcik me to login
        # self.random_sleep()
        self.random_sleep()
        """
        self.Agree_GoHome()

        self.random_sleep()
        self._safe_touch("tpl1766629844196.png",record_pos=(-0.386, 0.317)) #start Icon 
        
        self.wait_for_image("tpl1766630010007.png", timeout=50) #wait for login element
        if self.element_exists("tpl1768207957769.png"):
            self._safe_touch("tpl1768207957769.png",record_pos=(0.003, 0.171)) #click login in agian 
            self.random_sleep()

            self._safe_touch("tpl1768442685927.png", record_pos=(0.4, 0.81),clickpos=True)  #clcik me to login
            self.random_sleep()

        self._safe_touch("tpl1766630007249.png", (-0.374, 0.229), threshold=0.7)    #clcik little circle
        self.random_sleep()
        self._safe_touch("tpl1766630010007.png", (-0.062, 0.06))  #clcik homepage login
  
        
        self.random_sleep()
        self._safe_touch("tpl1766627868831.png", (-0.324, -0.013))  #click second little circle
        self.random_sleep()
        self._safe_touch("tpl1766643959547.png", (-0.29, -0.438))  #clcick +86 to switch country
        self.random_sleep()
        self._safe_touch("tpl1766649447388.png", (0.357, -0.426))  #click +1
        self.random_sleep()
        return True
 
    def Agree_GoHome(self):
        self.random_sleep()
        self._safe_touch("tpl1766629844196.png",record_pos=(-0.386, 0.317)) #start Icon 
        self.random_sleep()
        time.sleep(1)
        self._safe_touch("tpl1766629849292.png",record_pos=(0.018, 0.418)) #Agree Icon
        time.sleep(5)
        # Wait for homepage - using aircv approach
        # self.wait_for_image("tpl1766713067778.png", timeout=50)  # Wait for homepage (sid_login use)
        self.random_sleep()
        
        # Go to homepage using ADB home key command
        # Press back button 7 times to close app
        self.api_adb_shell("am force-stop com.xingin.xhs")

    def exceptions_click(self):
        try:
            # Check for gift close icon using aircv
            if self.element_exists("tpl1766712390329.png", threshold=0.7):
                self._safe_touch("tpl1766712390329.png", record_pos=(0, 0), threshold=0.7, timeout=2)
            self.random_sleep()
            
            # Check for "Later" button
            if self.element_exists("tpl1766733358148.png", threshold=0.7):
                self._safe_touch("tpl1766733358148.png", record_pos=(0, 0), threshold=0.7, timeout=2)
            self.random_sleep()
            
            # Check for biometric authentication
            if self.element_exists("tpl1766718656239.png", threshold=0.7):
                self._safe_touch("tpl1766718656239.png", record_pos=(0, 0), threshold=0.7, timeout=2)
                
        except Exception as e:
            if "Verification image detected" in str(e):
                raise e
            pass

    def send_sms(self, phone_number: str):
        # Input phone number
        self._safe_touch("tpl1766727477620.png", record_pos=(0.051, -0.375),clickpos=True) #点击 “phone Number”
        self.random_sleep()
        # Use ADB to input text instead of airtest text()
        self.human_type_text(phone_number)
        self.random_sleep()
        # Check for second little circle using aircv
        if self.element_exists("tpl1766627868831.png", threshold=0.7):
            pass  # Element exists but not clicked
            
        self.random_sleep()
        self._safe_touch("tpl1766627887424.png", record_pos=(-0.019, -0.122),clickpos=True) #点击 “login”
        time.sleep(5)
        # try:
        #     self.exceptions_click()
        # except:
        #     pass
        time.sleep(3)
        print(f"SMS sent to {phone_number}")
        return True

    def resend_sms(self, phone_number: str):
        self._safe_touch("tpl1766728324773.png", record_pos=(0.333, -0.379),clickpos=True)#点击删除
        self.random_sleep()
        self.send_sms(phone_number)
        self.random_sleep()
        # Try to click "Get Code" first, if not found, click "resend"
        if self.element_exists("tpl1766968639367.png", threshold=0.6):
            self._safe_touch("tpl1766968639367.png", record_pos=(0.296, -0.232),clickpos=True)
        else:
            self._safe_touch("tpl1766728475804.png", record_pos=(0.296, -0.232),clickpos=True)#点击“resend”
        return True

    def input_sms(self, sms_code: str):

        # Input SMS content
        self._safe_touch("tpl1766727625112.png", record_pos=(-0.264, -0.231)) #点击 "Enter code"

        # Use ADB to input text instead of airtest text()
        self.human_type_text(sms_code)
        time.sleep(3.0)  # Wait 3 seconds
        self._safe_touch("tpl1766652655771.png", record_pos=(-0.019, -0.122),clickpos=True)
     #   self.exceptions_click()
        return True

    def api_adb_shell(self, cmd_str: str, timeout=5):
        """执行adb的命令"""
        url = f"http://{self.host}/and_api/v1/shell/{self.ip}/{self.name}"
        print(url)
        data = {
            "cmd": cmd_str
        }
        try:
            response = requests.post(url, json=data, timeout=timeout)
            return response.json()
        except Exception as e:
            print(e)
            return {"code": -1, "msg": str(e)}

    def set_screenlock(self, paswd: str):
        result = self.api_adb_shell(f"locksettings set-password {paswd}")
        time.sleep(1)
        return

    def set_fingerprint(self):
        """打开安全设置页面"""
        # Open Security settings
        self.api_adb_shell("am start -a android.settings.SECURITY_SETTINGS")
        time.sleep(1.5)
        self.api_adb_shell("input tap 370 830")
        time.sleep(1)
        self.api_adb_shell("input text 1234")
        time.sleep(1)
        self.api_adb_shell("input keyevent KEYCODE_ENTER")
        time.sleep(1)
        # Scroll down multiple times
        self.api_adb_shell("input swipe 285 800 285 300 300")
        time.sleep(0.3)
        self.api_adb_shell("input swipe 285 800 285 300 300")
        time.sleep(0.3)
        self.api_adb_shell("input swipe 285 800 285 300 300")
        self.api_adb_shell("input tap 595 1200")
        time.sleep(1)
        self.api_adb_shell("input tap 124 1211")
        time.sleep(1)
        
        return self.api_adb_shell("input keyevent KEYCODE_HOME")
        time.sleep(2)

    def clear_app_cache(self, package_name: str = None):
        """Clear all cache for all apps or specific package"""
        try:
            if package_name:
                # Clear cache for specific package
                self.api_adb_shell(f"pm clear {package_name}")
                print(f"Cleared cache for {package_name}")
            else:
                # Clear cache for all apps
                result = self.api_adb_shell("pm list packages -3")  # Get all user-installed packages
                if result:
                    packages = [line.split(':')[1] for line in result.split('\n') if line.startswith('package:')]
                    for pkg in packages:
                        self.api_adb_shell(f"pm clear {pkg}")
                    print(f"Cleared cache for {len(packages)} apps")
                
                # Also clear system cache
                self.api_adb_shell("pm trim-caches 999999999")  # Trim all caches
            
            # Kill all background apps
            self.api_adb_shell("am kill-all")
            
            # Go back to home
            self.api_adb_shell("input keyevent KEYCODE_HOME")
            
            self.random_sleep()
            return True
        except Exception as e:
            print(f"Error clearing apps and cache: {e}")
            return False

    