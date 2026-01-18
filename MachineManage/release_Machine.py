import os
import redis
import json
import sys

# Load configuration from JSON file
CONFIG_FILE = "config.json"
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract configuration variables
redis_url = config["redis_url"]
ip = config["ip"]

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
    # Check if IP is provided as command line argument
    target_ip = sys.argv[1] if len(sys.argv) > 1 else None
    
    success = release_machine_lock(target_ip)
    exit(0 if success else 1)