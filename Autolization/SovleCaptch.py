import base64
import requests
import os

def verify():
    # Load image at runtime, not at import time
   # img_path = os.path.join(os.path.dirname(__file__), 'img', 'captcha_template.png')
    with open("captcha_template.png", 'rb') as f:
        b = base64.b64encode(f.read()).decode()
    
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "token": "RKTzGcq96Y3d69wzyOwWW+mkbLpRsRltKWTXAhd658k",
        "type": "20226",
        "image": b,
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data).json()
    print(response)
    return response

def get_capcahSolution():
    response = verify()
    if response.get("code") == 10000:
        return response.get("data", {}).get("data")
    else:
     print("failed to recognize the capcha!")
     return None


if __name__ == '__main__':
    verify()

