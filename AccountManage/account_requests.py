import json
import requests


def accountGet_ip(target_ip, api_url="http://192.168.223.144:9000/xhs/update_account_headers"):
    """
    Get account list for a specific IP that have logout state.
    
    Args:
        target_ip: Target IP address to filter accounts
        api_url: API endpoint URL
        
    Returns:
        list: List of accounts in format [name, index, "", ""] matching config.json structure
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        logout_accounts = []
        
        for account in data.get("data", []):
            if (account.get("ip") == target_ip and 
                account.get("state") == "-100 账号退出登录,请删除或者重新登陆"):
                name_field = account.get("name", "")
                if "-" in name_field:
                    parts = name_field.split("-")
                    index_str = parts[0].replace("T", "")
                    account_number = parts[1]
                    index = index_str[-1] if index_str.isdigit() else "0"
                    logout_accounts.append([account_number, index, "", ""])
        
        return logout_accounts
    
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    accounts = accountGet_ip("192.168.124.17")
    print(f"Found {len(accounts)} logout accounts:")
    for account in accounts:
        print(f"  {account}")
