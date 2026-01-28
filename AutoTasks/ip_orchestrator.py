"""
IP Orchestrator Module

This module coordinates the processing of multiple IPs either sequentially
or in parallel. It provides the top-level orchestration for the multi-IP
SMS relogin automation system.
"""

import sys
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setting import load_config, get_ip_config, get_all_ips
from AutoTasks.ip_processor import process_ip_batches


def process_sequential(ips: list, config: dict, global_config: dict) -> dict:
    """
    Process IPs one at a time in sequential order.
    
    This function iterates through the list of IPs and processes each one
    completely before moving to the next. If an IP fails, the error is logged
    and processing continues with the remaining IPs.
    
    Args:
        ips: List of IP addresses to process
        config: Complete configuration dict with "global" and "ips" sections
        global_config: Global configuration dict
    
    Returns:
        dict: Orchestrator results with keys:
            - total_ips: Total number of IPs to process
            - completed_ips: Number of IPs that completed successfully
            - failed_ips: Number of IPs that failed
            - results: Dict mapping IP addresses to their results
    
    Requirements: 5.1, 5.4, 5.5
    """
    results = {
        "total_ips": len(ips),
        "completed_ips": 0,
        "failed_ips": 0,
        "results": {}
    }
    
    for ip in ips:
        try:
            print(f"\n{'='*60}")
            print(f"Processing IP: {ip}")
            print(f"{'='*60}\n")
            
            ip_config = get_ip_config(ip)
            result = process_ip_batches(ip, ip_config, global_config)
            
            results["results"][ip] = result
            results["completed_ips"] += 1
            
            print(f"\nCompleted IP {ip}:")
            print(f"  Success: {result['success_count']}")
            print(f"  Failures: {result['failure_count']}")
            
        except Exception as e:
            print(f"Error processing IP {ip}: {e}")
            results["failed_ips"] += 1
            results["results"][ip] = {"error": str(e)}
    
    return results


def process_parallel(ips: list, config: dict, global_config: dict, max_parallel: int) -> dict:
    """
    Process multiple IPs concurrently with a concurrency limit.
    
    This function uses ProcessPoolExecutor to process multiple IPs in parallel,
    respecting the max_parallel limit. Results are collected as they complete.
    If an IP fails, the error is logged and processing continues with other IPs.
    
    Args:
        ips: List of IP addresses to process
        config: Complete configuration dict with "global" and "ips" sections
        global_config: Global configuration dict
        max_parallel: Maximum number of IPs to process concurrently
    
    Returns:
        dict: Orchestrator results with keys:
            - total_ips: Total number of IPs to process
            - completed_ips: Number of IPs that completed successfully
            - failed_ips: Number of IPs that failed
            - results: Dict mapping IP addresses to their results
    
    Requirements: 5.2, 5.3, 5.4, 5.5
    """
    results = {
        "total_ips": len(ips),
        "completed_ips": 0,
        "failed_ips": 0,
        "results": {}
    }
    
    with ProcessPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all IP processing tasks
        future_to_ip = {
            executor.submit(process_ip_batches, ip, get_ip_config(ip), global_config): ip
            for ip in ips
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                results["results"][ip] = result
                results["completed_ips"] += 1
                
                print(f"\nCompleted IP {ip}:")
                print(f"  Success: {result['success_count']}")
                print(f"  Failures: {result['failure_count']}")
                
            except Exception as e:
                print(f"Error processing IP {ip}: {e}")
                results["failed_ips"] += 1
                results["results"][ip] = {"error": str(e)}
    
    return results


def process_all_ips(mode: str = "sequential", max_parallel: int = 3, selected_ips: list = None) -> dict:
    """
    Process all configured IPs either sequentially or in parallel.
    
    This is the main entry point for the IP orchestrator. It loads the
    configuration, extracts the list of IPs, and routes to either
    sequential or parallel processing based on the mode parameter.
    
    Args:
        mode: Processing mode - "sequential" or "parallel"
        max_parallel: Maximum number of IPs to process concurrently (parallel mode only)
        selected_ips: Optional list of specific IPs to process. If None, all IPs are processed.
    
    Returns:
        dict: Orchestrator results with keys:
            - total_ips: Total number of IPs processed
            - completed_ips: Number of IPs that completed successfully
            - failed_ips: Number of IPs that failed
            - results: Dict mapping IP addresses to their results
    
    Raises:
        ValueError: If mode is not "sequential" or "parallel"
    
    Requirements: 5.1, 5.2
    """
    # Validate mode parameter
    if mode not in ["sequential", "parallel"]:
        raise ValueError(f"Invalid mode: {mode}. Must be 'sequential' or 'parallel'")
    
    # Load configuration
    config = load_config()
    global_config = config.get("global", {})
    
    # Get IPs to process
    if selected_ips:
        ips = selected_ips
        print(f"\n{'*'*60}")
        print(f"* Using selected IPs: {', '.join(ips)}")
    else:
        ips = get_all_ips()
    
    print(f"\n{'*'*60}")
    print(f"* IP Orchestrator Starting")
    print(f"* Mode: {mode}")
    print(f"* Total IPs: {len(ips)}")
    if mode == "parallel":
        print(f"* Max Parallel: {max_parallel}")
    print(f"{'*'*60}\n")
    
    # Route to appropriate processing function
    if mode == "sequential":
        return process_sequential(ips, config, global_config)
    else:  # mode == "parallel"
        return process_parallel(ips, config, global_config, max_parallel)
