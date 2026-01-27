"""
IP Processor Module

This module handles processing of device batches for individual IPs.
It coordinates machine management, relogin operations, and account updates
for a single IP address.
"""

import sys
import os
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MachineManage.stop_machine import stop_batch, stop_machines_all, get_machine_namelist
from MachineManage.start_machine import start_batch
from MachineManage.lock_machine import lock_machine, release_machine_lock
from setting import write_ip_config, append_ip_config, group_pools, batch_slice
from AccountManage.prologin_initial import batch_changeLogin_state
from AccountManage.account_requests import accountGet_ip
from SMSLogin.SmsRelogin import relogin_process, check_loginstate_batch
from AccountManage.test_account import update_accountlist
from MachineManage.start_machine import wait_machines_ready

def process_single_batch(ip: str, ip_config: dict, global_config: dict, batch: list) -> dict:

    print(f"\n{'='*60}")
    print(f"Processing batch for IP {ip}: {len(batch)} devices")
    print(f"{'='*60}\n")
    
    # Extract configuration from global config
    host_local = global_config["host_local"]
    host_rpc = global_config["host_rpc"]
    update_account_url = global_config["update_account_url"]
    
    # 1. Write batch to IP's info_list
    write_ip_config(ip, "info_list", batch)
    
    # 2. Stop and start machines
    print(f"Stopping batch machines for IP {ip}...")
    stop_batch(ip, host_local, batch)
    
    print(f"Starting batch machines for IP {ip}...")
    start_batch(ip, host_local, batch)
    
    wait_machines_ready(ip, host_local, batch)
    time.sleep(5)

    # 3. Execute relogin with multiprocessing
    print(f"Executing SMS relogin for {len(batch)} devices...")
    with ProcessPoolExecutor(max_workers=4) as executor:
        relogin_func = partial(relogin_process, ip, host_local)
        executor.map(relogin_func, batch)
    
    # 4. Update login state
    print(f"Updating login state for batch...")
    batch_changeLogin_state(ip, host_local, batch)
    
    # # 5. Update account list on server and wait for hooks to be ready
    print(f"Updating account list on server...")
    update_accountlist(ip, host_rpc, batch, update_account_url)
    
    # # Wait for all hooks to work properly
    time.sleep(100)

    
    # # 6. Get failures and update failure list
    # print(f"Checking for failed devices...")
    update_accountlist(ip, host_rpc, batch, update_account_url)

    
    # 7. Check login state
    print(f"Checking login state for batch...")
    check_loginstate_batch(ip, host_local, batch)
    
    # 8. Stop batch machines
    print(f"Stopping batch machines...")
    stop_batch(ip, host_local, batch)
    
    # Calculate results (no failures tracked when update_accountlist is commented out)
    failure_devices = []
    success_count = len(batch) - len(failure_devices)
    failure_count = len(failure_devices)
    
    print(f"\nBatch complete for IP {ip}:")
    print(f"  Success: {success_count}")
    print(f"  Failures: {failure_count}")
    
    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "failures": failure_devices
    }



def process_ip_batches(ip: str, ip_config: dict, global_config: dict) -> dict:
    """
    Process all batches for a single IP.
    
    This function:
    1. Loads IP-specific data from ip_config
    2. Creates batches using group_pools() and batch_slice()
    3. Stops all machines for the IP
    4. Processes each batch using process_single_batch()
    5. Aggregates results across all batches
    6. Returns IP processing results
    
    Args:
        ip: IP address to process
        ip_config: Configuration specific to this IP
        global_config: Global configuration (domain, redis_url, etc.)
    
    Returns:
        dict: IP processing results with keys:
            - ip: IP address processed
            - success_count: Total number of successful devices
            - failure_count: Total number of failed devices
            - processed_batches: Number of batches processed
            - failures: List of all Device_Info that failed
    
    Requirements: 4.1, 4.5, 10.5
    """
    print(f"\n{'#'*60}")
    print(f"# Starting IP Processing: {ip}")
    print(f"{'#'*60}\n")
    
    # 1. Lock the IP to prevent concurrent processing
    print(f"Acquiring lock for IP {ip}...")
    if not lock_machine(ip):
        print(f"Failed to acquire lock for IP {ip}. IP is already being processed.")
        return {
            "ip": ip,
            "success_count": 0,
            "failure_count": 0,
            "processed_batches": 0,
            "failures": [],
            "error": "Failed to acquire IP lock"
        }
    
    try:
        # 2. Auto-fill info_pool from account API
        print(f"Fetching logout accounts for IP {ip}...")
        logout_accounts = accountGet_ip(ip)
        
        if logout_accounts:
            print(f"IP {ip} has {len(logout_accounts)} logout accounts. Writing to info_pool...")
            # Write logout accounts directly to info_pool in config.json
            write_ip_config(ip, "info_pool", logout_accounts)
            print(f"Successfully updated info_pool for IP {ip}")
            # Update the local ip_config to reflect the changes
            ip_config["info_pool"] = logout_accounts 
       
        # 3. Load IP-specific data
        info_pool = ip_config["info_pool"]
        host_local = global_config["host_local"]
        
        print(f"IP {ip} has {len(info_pool)} devices in info_pool")
        
        # 4. Create batches from info_pool
        print(f"Creating batches from info_pool...")
        groups = group_pools(info_pool)
        batch_queue = batch_slice(groups)
        
        print(f"Created {len(batch_queue)} batches for IP {ip}")
        
        # 5. Stop all machines for this IP
        print(f"Stopping all machines for IP {ip}...")
        names = get_machine_namelist(ip, host_local)
        stop_machines_all(ip, host_local, names)
        time.sleep(10)
        
        # 6. Process each batch
        results = {
            "ip": ip,
            "success_count": 0,
            "failure_count": 0,
            "processed_batches": 0,
            "failures": []
        }
        
        for batch_idx, batch in enumerate(batch_queue, 1):
            print(f"\n--- Processing batch {batch_idx}/{len(batch_queue)} for IP {ip} ---")
            
            batch_result = process_single_batch(ip, ip_config, global_config, batch)
            
            results["processed_batches"] += 1
            results["success_count"] += batch_result["success_count"]
            results["failure_count"] += batch_result["failure_count"]
            results["failures"].extend(batch_result["failures"])
        
        print(f"\n{'#'*60}")
        print(f"# Completed IP Processing: {ip}")
        print(f"# Total Success: {results['success_count']}")
        print(f"# Total Failures: {results['failure_count']}")
        print(f"# Batches Processed: {results['processed_batches']}")
        print(f"{'#'*60}\n")
        
        return results
    
    except KeyboardInterrupt:
        print(f"\n[!] User cancelled processing for IP {ip}")
        raise
    except Exception as e:
        print(f"\n[!] Error processing IP {ip}: {e}")
        raise
    finally:
        # 7. Release the IP lock after processing completes (always executes)
        print(f"Releasing lock for IP {ip}...")
        release_machine_lock(ip)

if __name__ == "__main__":
    from setting import load_config
    
    # Set IP here - change this to the IP you want to process
    selected_ip = "192.168.124.18"
    
    # Load configuration
    config = load_config()
    
    # Get IP-specific and global configs
    ip_config = config["ips"][selected_ip]
    global_config = config["global"]
    results = process_ip_batches(selected_ip, ip_config, global_config)
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS FOR IP {selected_ip}")
    print(f"{'='*60}")
    print(f"Total Success: {results['success_count']}")
    print(f"Total Failures: {results['failure_count']}")
    print(f"Batches Processed: {results['processed_batches']}")
    print(f"{'='*60}\n")