# -*- encoding=utf8 -*-

import time
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Autolization.AutoOperate import AutoPhone
from Autolization.xhs_exceptEvents import ExceptionHandler

class XhsAutomation:
    """Xiaohongshu (XHS) app-specific automation methods"""
    
    # Image constants
    START_ICON_IMG = "tpl1766629844196.png"
    LOGIN_ELEMENT_IMG = "tpl1766630010007.png"
    SECOND_CIRCLE_IMG = "tpl1766627868831.png"
    COUNTRY_CODE_86_IMG = "tpl1766643959547.png"
    COUNTRY_CODE_1_IMG = "tpl1766649447388.png"
    
    def __init__(self, auto_phone):
        """
        Initialize XhsAutomation
        
        Args:
            auto_phone: AutoPhone instance to use for automation
        """
        self.auto_phone = auto_phone
        
        # Initialize exception handler
        self.exception_handler = ExceptionHandler(auto_phone)
    
    def _safe_touch(self, img_name, record_pos=None, threshold=0.6, 
                     timeout=10, clickpos=False,looptime=5):
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
        retry_count = 0
        for _ in range(looptime):
            retry_count += 1
            print(f"\033[91mRetry attempt: {retry_count} - Clicking: {img_name}\033[0m")
            
            if self.auto_phone.wait_and_click(img_name, timeout, threshold):
                return True
            
            exception_solution = self.exceptions_click()
            if not exception_solution:
                # If no exception was handled, don't break immediately
                # Continue trying if we haven't exhausted all attempts
                if retry_count >= looptime:
                    break
            time.sleep(3)

        # If image matching fails and clickpos is True, use fallback position
        if clickpos and record_pos is not None:
            x, y = record_pos
            # Convert normalized coordinates to actual coordinates if needed
            if -1 <= x <= 1 and -1 <= y <= 1:
                # Assuming 720x1280 resolution as in original code
                actual_x = int((x + 1) * 720 / 2)
                actual_y = int((y + 1) * 1280 / 2)
            else:
                actual_x, actual_y = x, y
                
            self.auto_phone.pos_click(actual_x, actual_y)
            print(f"Clicked at fallback position ({actual_x}, {actual_y}) for {img_name}")
            return True
        
        error_msg = f"Failed to click {img_name} and clickpos is False"
        print(f"\033[91m\033[1m{'=' * 80}\n{error_msg.center(80)}\n{'=' * 80}\033[0m")
        raise RuntimeError(error_msg)
    
    def switch_country(self):
        """Switch country code from +86 to +1"""
        self._safe_touch(self.SECOND_CIRCLE_IMG, (-0.324, -0.013), clickpos=True)  # click second little circle
        self.auto_phone.random_sleep()
        self._safe_touch("downarrow.png", (-0.29, -0.438), clickpos=True)  # click +86 to switch country
        self.auto_phone.random_sleep()
        self._safe_touch(self.COUNTRY_CODE_1_IMG, (0.357, -0.426), clickpos=True,looptime=5)  # click +1
        self.auto_phone.random_sleep()
    
    def into_loginface(self):
        """
        Navigate to login interface from app start
        
        Returns:
            bool: True if successful
        """
        time.sleep(1)
        self.auto_phone.random_sleep()
        self.auto_phone.wait_and_click(self.START_ICON_IMG, timeout=10, threshold=0.7)  # Wait and click start icon
        self.auto_phone.random_sleep()

        self._safe_touch("tpl1766629849292.png", record_pos=(0.018, 0.418))  # Agree Icon

        # Wait for homepage
        self.auto_phone.wait_for_image("tpl1766713067778.png", timeout=50)

        self.auto_phone.random_sleep()
        self._safe_touch(self.LOGIN_ELEMENT_IMG, (0.399, 0.844), clickpos=True)  # click me to login
        self.auto_phone.random_sleep()
        time.sleep(2)

        self.exceptions_click()
        self.exceptions_click()
        
        self.auto_phone.random_sleep()
        self._safe_touch("tpl1766630007249.png", (-0.374, 0.229), threshold=0.5)  # click little circle
        self.auto_phone.random_sleep()
        self._safe_touch(self.LOGIN_ELEMENT_IMG, (-0.062, 0.06))  # click homepage login
        self.auto_phone.random_sleep()
        return True
    
    def reinto_loginface(self):
        """
        Re-navigate to login interface (for re-login scenarios)
        """
        self.agree_go_home()

        self.auto_phone.random_sleep()
    
        self.auto_phone.wait_and_click(self.START_ICON_IMG, timeout=10, threshold=0.7)  # Wait and click start icon
    

        time.sleep(10)
        if self.auto_phone.element_exists("tpl1768207957769.png"):
            print("from exist ")
            self._safe_touch("tpl1768207957769.png", record_pos=(0, 0), clickpos=True, looptime=1)
        # else:
        #     self.auto_phone.wait_for_image(self.LOGIN_ELEMENT_IMG, timeout=30)  # wait for login element
        
        self.auto_phone.wait_for_image(self.LOGIN_ELEMENT_IMG, timeout=30)  # wait for login element

        #self._safe_touch("homepagecircle.png", (-0.374, 0.229), threshold=0.7,clickpos=True)  # click little circle
        self.auto_phone.random_sleep()
        self._safe_touch(self.LOGIN_ELEMENT_IMG, (-0.062, 0.06))  # click homepage login
        
        self.auto_phone.random_sleep()

        return True
 


    def agree_go_home(self):
        """
        Accept agreements and return to home screen
        """
        # self.auto_phone.random_sleep()
        # self.auto_phone.wait_and_click(self.START_ICON_IMG, timeout=5, threshold=0.7)  # Wait and click start icon
        # self.auto_phone.random_sleep()
        # time.sleep(3)
        
        self.auto_phone.stop_currentApp()
        #self._safe_touch("tpl1766629849292.png", record_pos=(0.018, 0.418))  # Agree Icon
        time.sleep(5)
        self.auto_phone.random_sleep()
        

    def send_sms(self, phone_number: str):
        
        # Input phone number
        self._safe_touch("PhoneInput.png", record_pos=(0.051, -0.375), clickpos=True)  # click "phone Number"
        self.auto_phone.random_sleep()
        self.auto_phone.human_type_text(phone_number)
        self.auto_phone.random_sleep()
        
        # Check for second little circle
        if self.auto_phone.element_exists("tpl1766627868831.png", threshold=0.7):
            pass  # Element exists but not clicked
            
        self.auto_phone.random_sleep()
        self._safe_touch("FirstLogin.png", record_pos=(-0.019, -0.122), clickpos=True,looptime=1)  # click "login"
        
        time.sleep(3)
        for _ in range(15):
            if self.auto_phone.element_exists("downarrow.png"):
                break        
            else:
                self.exceptions_click()  
                     
            time.sleep(2)
        
        print(f"SMS sent to {phone_number}")
        return True

    def resend_sms(self, phone_number: str):

        self.auto_phone.random_sleep()
        
        # Try to click "Get Code" first, if not found, click "resend"
        if self.auto_phone.element_exists("tpl1766968639367.png", threshold=0.6):
            self._safe_touch("tpl1766968639367.png", record_pos=(0.296, -0.232), clickpos=True,looptime=1)
        else:
            self._safe_touch("tpl1766728475804.png", record_pos=(0.301, -0.261), clickpos=True,looptime=1)  # click "resend"
        return True

    def input_sms(self, sms_code: str):
        """
        Input SMS verification code
        
        Args:
            sms_code: SMS verification code to input
            
        Returns:
            bool: True if successful
        """
        # Input SMS content
        self._safe_touch("EnterCode.png", record_pos=(-0.264, -0.231))  # click "Enter code"

        self.auto_phone.human_type_text(sms_code)
        time.sleep(3.0)  # Wait 3 seconds
        return True



    def exceptions_click(self):
        """
        Handle common exception popups - delegates to ExceptionHandler
        
        Returns:
            bool: True if an exception was found and handled, False otherwise
        """
        return self.exception_handler.handle_exceptions()

    def check_loginState(self):
        """Check if user is logged out"""
        
        #handle the exception after input smscode
        for _ in range(10):
            if not self.auto_phone.element_exists("X.png"):
                break
            self.exceptions_click()
            time.sleep(3)
        
        time.sleep(5)
        #self.wait_for_image("logined_flag.png",timeout=20)
        # if self.auto_phone.element_exists("YellowOpus.png"):
        #     self._safe_touch("YellowOpus.png")
        # for _ in range(30):            
        #     if self.auto_phone.element_exists("YellowOpus.png")\
        #         or self.auto_phone.element_exists("LoveIcon.png"):
        #         time.sleep(5)
        #         if not self.auto_phone.element_exists("loggedOut.png"):
        #             print("\033[92mbeen Logined Success\033[0m")
        #             return True
        #         else:
        #             print("\033[92mbeen Logined out\033[0m")
        #             return False
        #     elif self.auto_phone.element_exists("loggedOut.png"):
        #         print("\033[92mbeen Logined out\033[0m")
        #         return False
            
        #     time.sleep(2)  # Add delay between checks
        check_login()

        return True
    
    def check_login(self):
        """Check if user is logged in. Returns False if X.png or loggedOut.png found, True otherwise"""
        if self.auto_phone.element_exists("X.png"):
            return False
        elif self.auto_phone.element_exists(self.LOGIN_ELEMENT_IMG):
            return False
        elif self.auto_phone.element_exists("loginAgain.png"):
            return False
        return True

    def snap_capcha(self, output_path="captcha_template.png"):
        """Capture captcha area from screen"""
        return self.auto_phone.img_handler.rectangle_snap(82, 295, 637, 824, output_path)

    def swipe_fullcapcha(self, hold_time=3):
        """
        Swipe to solve full captcha puzzle
        
        Args:
            hold_time: Time to hold at the end position
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Wait for the arrow image
        match_result = self.auto_phone.wait_for_image("myt_arrow.png", timeout=50, threshold=0.7)
        if not match_result:
            return False
        start_x, start_y = match_result['result']
        
        self.multi_direction_swipe(start_x, start_y, duration=10, hold_time=2)
        
        print(f"Dragged and held arrow for {hold_time}s")
        return True

    def multi_direction_swipe(self, x, y, duration=None, hold_time=0.3):
        from Autolization.SovleCaptch import get_capcahSolution
        import time
        
        # Calculate delay based on duration or hold_time
        if duration is not None:
            # Distribute total duration across the two moves
            delay = duration / 2
        else:
            delay = hold_time
        
        # Touch down at first point
        self.auto_phone.api_adb_shell(f"input motionevent DOWN {x} {y}")
        time.sleep(delay)
        
        # Move to right position
        self.auto_phone.api_adb_shell(f"input motionevent MOVE {x+550} {y}")
        time.sleep(delay)
        self.snap_capcha()
        # Get captcha solution and adjust position
        capcha_distance = get_capcahSolution()
        
        if capcha_distance is None:
            print("Failed to get captcha solution, using default distance")
            capcha_distance = 0
        print("CapchaDistance is:",capcha_distance)

        # Swipe to correct captcha location
        self.auto_phone.api_adb_shell(f"input motionevent MOVE {int(capcha_distance)} {y}")
        time.sleep(delay)

        # Release at last point
        self.auto_phone.api_adb_shell(f"input motionevent UP {x} {y}")
        
        return True

