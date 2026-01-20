# -*- encoding=utf8 -*-
"""Image handling utilities for screenshot capture, template matching, and visualization"""

import os
import base64
import time
import requests
import aircv as ac
from PIL import Image, ImageDraw, ImageFont


class ImgHandle:
    """Handles image operations including screenshot capture, template matching, and visualization"""
    
    def __init__(self, host: str = "", ip: str = "", name: str = ""):
        """
        Initialize ImgHandle
        
        Args:
            host: Host for API calls (e.g., "192.168.124.5:5000")
            ip: Device IP address
            name: Device name for API calls
        """
        self.host = host
        self.ip = ip
        self.name = name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
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
            # Ensure output_path is properly encoded for Windows
            if isinstance(output_path, str):
                output_path = os.path.normpath(output_path)
            
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

    def rectangle_snap(self, x1, y1, x2, y2, output_path="capcha_template.png"):
        """
        截取屏幕指定矩形区域并保存为模板文件
        
        参数:
        x1, y1: 左上角坐标
        x2, y2: 右下角坐标
        output_path: 输出图像路径
        
        返回:
        bool: 成功返回True，失败返回False
        """
        import tempfile
        
        # 获取当前屏幕截图
        screenshot_base64 = self.get_screenshot_base64()
        if not screenshot_base64:
            print("获取截图失败")
            return False
        
        # 保存临时截图
        temp_screenshot = os.path.join(tempfile.gettempdir(), "temp_full_screenshot.png")
        if not self.save_base64_as_image(screenshot_base64, temp_screenshot):
            print("保存截图失败")
            return False
        
        # 打开图像并裁剪
        img = Image.open(temp_screenshot)
        
        # 确保坐标顺序正确
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)
        
        # 裁剪矩形区域
        cropped_img = img.crop((left, top, right, bottom))
        
        # 保存裁剪后的图像
        cropped_img.save(output_path)
        
        # 清理临时文件
        try:
            os.remove(temp_screenshot)
        except:
            pass
        
        print(f"已截取区域 ({left},{top})-({right},{bottom}) 并保存至 {output_path}")
        return True

    def wait_for_image(self, img_name, timeout=50, threshold=0.7, interval=1, img_dir=None):
        """
        Wait for an image to appear on screen (similar to airtest wait function)
        
        Args:
            img_name: Image filename in img/ directory
            timeout: Maximum time to wait in seconds
            threshold: Matching threshold (0.0-1.0)
            interval: Check interval in seconds
            img_dir: Custom image directory path (optional)
            
        Returns:
            dict: Match result if found, None if timeout
        """
        if img_dir:
            img_path = os.path.join(img_dir, img_name)
        else:
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

    def element_exists(self, img_name, threshold=0.7, img_dir=None):

        if img_dir:
            img_path = os.path.join(img_dir, img_name)
        else:
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
