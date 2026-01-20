# -*- encoding=utf8 -*-

import os
import sys

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
        self.exception_images = [
            "tpl1766712390329.png",  # Gift close icon
            "tpl1766733358148.png",  # Later button
            "tpl1766718656239.png",  # Biometric authentication
            "tpl1768207957769.png",  # login in again exception
            "tpl1768442685927.png",  # click me 
            "tryAgian.png",
            "loginAgain.png",
            "waitapp.png",
            "agreeCountinue.png",
            "SmsLogin.png",
            "tpl1766968639367.png",
            "tpl1766728475804.png",
        ]
    
    def handle_exceptions(self, threshold=0.7):
        """
        Check for and handle common exception popups
        
        Args:
            threshold: Image matching threshold (0.0-1.0)
            
        Returns:
            bool: True if an exception was found and handled, False otherwise
            
        Raises:
            Exception: Re-raises verification or unexpected image exceptions
        """
        try:
            for img in self.exception_images:
                match_result = self.auto_phone.element_exists(img, threshold=threshold)
                if match_result:
                    x, y = match_result['result']
                    self.auto_phone.pos_click(x, y)
                    self.auto_phone.random_sleep()
                    return True
            
            # No image matched
            return False
            
        except Exception as e:
            if "Verification image detected" in str(e):
                raise e
            if "unexpected img" in str(e):
                print("unexpected img")
                raise e
            pass

    def switch_SmsLogin():
        
        return