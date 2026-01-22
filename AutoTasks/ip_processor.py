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
from setting import write_ip_config, append_ip_config, group_pools, batch_slice
from AccountManage.prologin_initial import batch_changeLogin_state
from SMSLogin.SmsRelogin import relogin_process, check_loginstate_batch
from AccountManage.test_account import update_accountlist


def process_single_batch(ip: str, ip_config: dict, global_config: dict, batch: list) -> dict:
    """
    Process a single batch of devices for an IP.
    
    This function executes the complete relogin workflow for a batch:
    1. Write batch to IP's info_list
    2. Stop and start machines
    3. Execute relogin with multiprocessing
    4. Update login state
    5. Update account list on server
    6. Track failures
    7. Check login state
    8. Stop batch machines
    
    Args:
        ip: IP address to process
        ip_config: Configuration specific to this IP
        global_config: Global configuration (domain, redis_url, etc.)
        batch: List of Device_Info items to process
    
    Returns:
        dict: Batch results with keys:
            - success_count: Number of successful devices
            - failure_count: Number of failed devices
            - failures: List of Device_Info that failed
    
    Requirements: 4.1, 4.2, 4.3, 4.5, 10.4
    """
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
    time.sleep(30)
    
    # 3. Execute relogin with multiprocessing
    print(f"Executing SMS relogin for {len(batch)} devices...")
    with ProcessPoolExecutor(max_workers=2) as executor:
        relogin_func = partial(relogin_process, ip, host_local)
        executor.map(relogin_func, batch)
    
    # 4. Update login state
    print(f"Updating login state for batch...")
    batch_changeLogin_state(ip, host_local, batch)
    
    # 5. Update account list on server
    print(f"Updating account list on server...")
    update_accountlist(ip, host_rpc, batch, update_account_url)
    time.sleep(120)
    
    # 6. Get failures and update failure list
    print(f"Checking for failed devices...")
    failure_devices = update_accountlist(ip, host_rpc, batch, update_account_url)
    
    for device in failure_devices:
        append_ip_config(ip, "failure_list", device)
    
    # 7. Check login state
    print(f"Checking login state for batch...")
    check_loginstate_batch(ip, host_local, batch)
    
    # 8. Stop batch machines
    print(f"Stopping batch machines...")
    stop_batch(ip, host_local, batch)
    
    # Calculate results
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
    
    # 1. Load IP-specific data
    info_pool = ip_config["info_pool"]
    host_local = global_config["host_local"]
    
    print(f"IP {ip} has {len(info_pool)} devices in info_pool")
    
    # 2. Create batches from info_pool
    print(f"Creating batches from info_pool...")
    groups = group_pools(info_pool)
    batch_queue = batch_slice(groups)
    
    print(f"Created {len(batch_queue)} batches for IP {ip}")
    
    # 3. Stop all machines for this IP
    print(f"Stopping all machines for IP {ip}...")
    names = get_machine_namelist(ip, host_local)
    stop_machines_all(ip, host_local, names)
    time.sleep(20)
    
    # 4. Process each batch
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
