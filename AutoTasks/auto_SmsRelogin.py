"""
Multi-IP SMS Relogin Automation - Main Entry Point

This script orchestrates SMS relogin processing across multiple IPs.
It supports both sequential and parallel processing modes.

Usage:
    python auto_SmsRelogin.py [--mode MODE] [--max-parallel N]

Arguments:
    --mode MODE          Processing mode: 'sequential' or 'parallel' (default: sequential)
    --max-parallel N     Maximum number of IPs to process in parallel (default: 3)

Examples:
    # Process IPs sequentially (one at a time)
    python auto_SmsRelogin.py --mode sequential

    # Process IPs in parallel with max 5 concurrent IPs
    python auto_SmsRelogin.py --mode parallel --max-parallel 5
"""

import sys
import os
<<<<<<< HEAD
from concurrent.futures import ProcessPoolExecutor
=======
import argparse
>>>>>>> 79f43efe8f97865b82f4301ee99fd82b75e4f048

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AutoTasks.ip_orchestrator import process_all_ips


def print_summary(results: dict) -> None:
    """
    Print a summary of processing results for all IPs.
    
<<<<<<< HEAD
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
=======
    Args:
        results: Orchestrator results dict containing IP processing results
    """
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total IPs: {results['total_ips']}")
    print(f"Completed: {results['completed_ips']}")
    print(f"Failed: {results['failed_ips']}")
    print(f"{'='*60}\n")
    
    # Print details for each IP
    for ip, result in results['results'].items():
        print(f"IP: {ip}")
        if 'error' in result:
            print(f"  Status: FAILED")
            print(f"  Error: {result['error']}")
        else:
            print(f"  Status: COMPLETED")
            print(f"  Batches Processed: {result.get('processed_batches', 0)}")
            print(f"  Successful Devices: {result.get('success_count', 0)}")
            print(f"  Failed Devices: {result.get('failure_count', 0)}")
        print()
    
    print(f"{'='*60}\n")


def main():
    """
    Main entry point for the multi-IP SMS relogin automation system.
    
    Parses command-line arguments and invokes the IP orchestrator with
    the specified processing mode and concurrency settings.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Multi-IP SMS Relogin Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode sequential
  %(prog)s --mode parallel --max-parallel 5
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['sequential', 'parallel'],
        default='sequential',
        help='Processing mode: sequential (one IP at a time) or parallel (multiple IPs concurrently)'
    )
    
    parser.add_argument(
        '--max-parallel',
        type=int,
        default=3,
        help='Maximum number of IPs to process concurrently in parallel mode (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Validate max_parallel
    if args.max_parallel < 1:
        print("Error: --max-parallel must be at least 1")
        sys.exit(1)
    
    try:
        # Process all IPs using the orchestrator
        results = process_all_ips(mode=args.mode, max_parallel=args.max_parallel)
        
        # Print summary of results
        print_summary(results)
        
        # Exit with appropriate status code
        if results['failed_ips'] > 0:
            sys.exit(1)  # Exit with error if any IPs failed
        else:
            sys.exit(0)  # Exit successfully
            
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()  
>>>>>>> 79f43efe8f97865b82f4301ee99fd82b75e4f048
