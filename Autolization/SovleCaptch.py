import base64
import requests
import os
#from Autolization.ImgHandle import ImgHandle
# www.jfbym.com  注册后登录去用户中心

img_path = os.path.join(os.path.dirname(__file__), 'img', 'capcha_5.png')
with open(img_path, 'rb') as f:
    b = base64.b64encode(f.read()).decode()  ## 图片二进制流base64字符串


def verify():
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


if __name__ == '__main__':
    verify()

