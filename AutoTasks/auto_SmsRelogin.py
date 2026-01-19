import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MachineManage.stop_machine import *
from MachineManage.start_machine import *
from setting import *
from AccountManage.prologin_initial import *

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    
    print(group_pools())
    batch_quene = batch_slice()
    
    for batch in batch_quene:
        write_configs("info_list", batch)
        config = load_config()
        """Initialize the Machine"""
        stop_batch(config)
        start_batch(config)
        time.sleep(50)

        """SmsRelogin with Multiple Threads"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(login_process, config["info_list"])

        """update the Account info if login Sucess"""
