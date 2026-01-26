# -*- encoding=utf8 -*-

import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExceptionHandler:
    """Handle common UI exceptions and popups during automation"""
    
    def __init__(self, auto_phone):
        """
        Initialize ExceptionHandler
        
        Args:
            auto_phone: AutoPhone instance to use for image detection and clicking
        """
        self.auto_phone = auto_phone
        self.exception_images = {
            "tpl1766712390329.png": None,  # Gift close icon
            "tpl1766733358148.png": None,  # Later button
            "tpl1766718656239.png": None,  # Biometric authentication
            "tpl1768207957769.png": None,  # login in again exception
            "tpl1768442685927.png": None,  # click me 
            "MeAlpha.png": None,  # click me 
            "tryAgian.png": None,
            "tpl1768207957769.png": None, #login Agian
            "waitapp.png": None,
            "agreeCountinue.png": None,
            "SmsLogin.png": None,
            "tpl1766968639367.png": None,
            "tpl1766728475804.png": None, 
            #"tpl1766630010007.png": None,  # homepage Login
            # "tpl1766643959547.png": None,  # +86
            "tpl1766649447388.png": None,  # +1
            "myt_arrow.png": self.handle_captcha_arrow
            #Todo Add 
        }
    
    def click(self, match_result):
        x, y = match_result['result']
        self.auto_phone.pos_click(x, y)
        self.auto_phone.random_sleep()
        return True


    def handle_captcha_arrow(self, match_result):
        from Autolization.AutoXhs import XhsAutomation
        xhs = XhsAutomation(self.auto_phone)
        
        # Show notification window
        root = tk.Tk()
        root.geometry("600x200")
        root.title("Captcha Alert")
        
        label = tk.Label(root, text="⚠️ CAPTCHA DETECTED ⚠️\n\nPlease solve the captcha manually!", 
                        font=("Arial", 20, "bold"), fg="red", pady=30)
        label.pack()
        
        button = tk.Button(root, text="OK", command=root.destroy, font=("Arial", 14), width=10)
        button.pack(pady=10)
        
        root.mainloop()
        
        # Wait for captcha arrow to disappear
        #disappeared = self.auto_phone.wait_imageDisappear("myt_arrow.png", timeout=60, interval=1)
        for _ in range(120):
            if self.auto_phone.element_exists("myt_arrow.png"):
                time.sleep(3)
                continue
            else:
                break
   
        
      #  if not disappeared:
        print("\033[91mWarning: Captcha arrow did not disappear within timeout\033[0m")
        return disappeared 

    
    def switch_SmsLogin():
        
        return

    def handle_exceptions(self, threshold=0.7):
        try:
            for img, handler in self.exception_images.items():
                match_result = self.auto_phone.element_exists(img, threshold=threshold)
                if match_result:
                    print(f"\033[92mFound image match: {img}\033[0m")
                    if handler:
                        # Execute custom handler
                        return handler(match_result)
                    else:
                        # Default: just click
                        return self.click(match_result)
            return False
        except Exception as e:
            if "Verification image detected" in str(e) or "unexpected img" in str(e):
                print("\033[91m" + str(e) + "\033[0m")  # Red color output
                raise e