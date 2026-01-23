<<<<<<< HEAD
import json
import requests


def accountGet_ip(api_url="http://192.168.223.144:9000/xhs/update_account_headers"):
    """
    Get all unique IPs that have accounts with logout state.
    
    Args:
        api_url: API endpoint URL
        
    Returns:
        list: List of unique IPs with logout state accounts
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        logout_ips = set()
        
        for account in data.get("data", []):
            if account.get("state") == "-100 账号退出登录,请删除或者重新登陆":
                logout_ips.add(account.get("ip"))
        
        return list(logout_ips)
    
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    ips = accountGet_ip()
    print(f"Found {len(ips)} IPs with logout accounts:")
    for ip in ips:
        print(f"  - {ip}")
=======
import json
import requests


def accountGet_ip(api_url="http://192.168.223.144:9000/xhs/update_account_headers"):
    """
    Get all unique IPs that have accounts with logout state.
    
    Args:
        api_url: API endpoint URL
        
    Returns:
        list: List of unique IPs with logout state accounts
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        logout_ips = set()
        
        for account in data.get("data", []):
            if account.get("state") == "-100 账号退出登录,请删除或者重新登陆":
                logout_ips.add(account.get("ip"))
        
        return list(logout_ips)
    
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    ips = accountGet_ip()
    print(f"Found {len(ips)} IPs with logout accounts:")
    for ip in ips:
        print(f"  - {ip}")
>>>>>>> 79f43efe8f97865b82f4301ee99fd82b75e4f048
