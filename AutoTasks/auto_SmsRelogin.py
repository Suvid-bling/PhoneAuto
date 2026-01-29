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
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AutoTasks.ip_orchestrator import process_all_ips


def print_summary(results: dict) -> None:
    """
    Print a summary of processing results for all IPs.
    
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
  %(prog)s --ips 192.168.124.19 192.168.124.17
  %(prog)s --mode parallel --ips 192.168.124.19 192.168.124.17
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
    
    parser.add_argument(
        '--ips',
        type=str,
        nargs='+',
        help='Specific IP addresses to process (space-separated). If not provided, all IPs will be processed.'
    )
    
    args = parser.parse_args()
    
    # Hardcoded IPs list - modify this to select specific IPs
    Ips = [



    ]
    
    # Use hardcoded IPs if args.ips is not provided
    selected_ips = args.ips if args.ips else Ips
    
    # Validate max_parallel
    if args.max_parallel < 1:
        print("Error: --max-parallel must be at least 1")
        sys.exit(1)
    
    try:
        # Process all IPs using the orchestrator
        results = process_all_ips(mode=args.mode, max_parallel=args.max_parallel, selected_ips=selected_ips)
        
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
