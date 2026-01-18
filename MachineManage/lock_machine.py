import os
import redis
import json

# Load configuration from JSON file
CONFIG_FILE = "config.json"
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Extract configuration variables
redis_url = config["redis_url"]
ip = config["ip"]

if __name__ == '__main__':
    myredis = redis.Redis.from_url(
        redis_url, 
        encoding="utf-8", 
        decode_responses=True,
        max_connections=30
    )
    lock_key = f"xhs_device_login:{ip}"
    result = myredis.set(lock_key, "running", nx=True, ex=60 * 60 * 2)   
    if not result:
        myredis.close()
        print("ip已被占用")
        exit(1)

    # Your main logic here
    print("Redis lock acquired successfully")
    
