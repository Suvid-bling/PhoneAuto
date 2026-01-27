import os
import redis
import json

# Load configuration from JSON file
CONFIG_FILE = "config.json"
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract configuration variables
redis_url = config["global"]["redis_url"]
ip = config.get("ip")


def lock_machine(target_ip=None):
    """Acquire Redis lock for a specific IP or current IP"""
    myredis = redis.Redis.from_url(
        redis_url, 
        encoding="utf-8", 
        decode_responses=True,
        max_connections=30
    )
    
    # Use provided IP or default to config IP
    lock_ip = target_ip if target_ip else ip
    lock_key = f"xhs_device_login:{lock_ip}"
    
    try:
        result = myredis.set(lock_key, "running", nx=True, ex=60 * 60 * 2)
        if not result:
            print(f"IP already locked: {lock_ip}")
            return False
        print(f"Successfully locked IP: {lock_ip}")
        return True
    except Exception as e:
        print(f"Error acquiring lock: {e}")
        return False
    finally:
        myredis.close()


def release_machine_lock(target_ip=None):
    """Release the Redis lock for a specific IP or current IP"""
    myredis = redis.Redis.from_url(
        redis_url, 
        encoding="utf-8", 
        decode_responses=True,
        max_connections=30
    )
    
    # Use provided IP or default to config IP
    release_ip = target_ip if target_ip else ip
    lock_key = f"xhs_device_login:{release_ip}"
    
    try:
        # Check if lock exists
        if myredis.exists(lock_key):
            result = myredis.delete(lock_key)
            if result:
                print(f"Successfully released lock for IP: {release_ip}")
                return True
            else:
                print(f"Failed to release lock for IP: {release_ip}")
                return False
        else:
            print(f"No lock found for IP: {release_ip}")
            return True
    except Exception as e:
        print(f"Error releasing lock: {e}")
        return False
    finally:
        myredis.close()


if __name__ == '__main__':
    release_machine_lock("192.168.124.17")
    release_machine_lock("192.168.124.18")
    release_machine_lock("192.168.124.19")
    release_machine_lock("192.168.124.60")
    release_machine_lock("192.168.124.23")
    release_machine_lock("192.168.124.26")
    release_machine_lock("192.168.124.68")
    release_machine_lock("192.168.124.50")
    release_machine_lock("172.16.227.32")
    release_machine_lock("172.16.212.171")
    release_machine_lock("172.16.209.72")
    release_machine_lock("172.16.42.55")
    release_machine_lock("172.16.204.10")
    #release_machine_lock("192.168.124.17")