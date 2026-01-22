import sys
import os
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MachineManage.stop_machine import *
from MachineManage.start_machine import *
from setting import *
from AccountManage.prologin_initial import *
from SMSLogin.SmsRelogin import *
from AccountManage.test_account import *
import time

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "..", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_batch_relogin(batch):
    """Process a batch of devices for SMS relogin"""
    write_configs("info_list", batch)
    config = load_config()
    
    # Initialize the Machine
    stop_batch(config)
    start_batch(config)
    time.sleep(30)

 # SmsRelogin with Multiple Processes
    with ProcessPoolExecutor(max_workers=2) as executor:
        executor.map(relogin_process, config["info_list"])

    # Update the Account Login state if login Success
    batch_changeLogin_state(config)
    
    # Update Accountlist in server
    update_accountlist(batch, config["ip"])
    time.sleep(120)
    failure_account = update_accountlist(batch, config["ip"])
    #clear_configs("failure_list")
    append_configs("failure_list", failure_account)
    check_loginstate_batch(batch)
    stop_batch(config)  #stop Current Machine 

if __name__ == "__main__":
    config = load_config()
    groups = group_pools(config["info_pool"])
    batch_quene = batch_slice(groups)
    #clear_configs("info_pool")
    
    # Stop all machines first
    names = get_machine_namelist(config)
    stop_machines_all(names, config)
    time.sleep(20)

    for batch in batch_quene:
        process_batch_relogin(batch)
        #process_batch_relogin(config["failure_list"]) #Retry agian for failure account  
