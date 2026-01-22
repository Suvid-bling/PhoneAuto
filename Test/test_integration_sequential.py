"""
Integration test for multi-IP sequential processing.

This test verifies that IPs are processed one at a time in sequential mode,
with each IP completing before the next begins.

Feature: multi-ip-automation-refactor
Requirements: 5.1
"""

import sys
import os
import json
import tempfile
import shutil
import threading
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoTasks.ip_orchestrator import process_all_ips


def test_sequential_processing_order():
    """
    Test sequential processing of 2-3 IPs.
    Verifies IPs are processed one at a time without overlap.
    """
    # Create a temporary config file
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.json')
    
    try:
        # Setup test configuration with 3 IPs
        test_config = {
            "global": {
                "domain": "http://test.example.com",
                "image": "test-image:latest",
                "redis_url": "redis://localhost:6379/0",
                "update_account_url": "http://test.example.com/update",
                "ip_dict": {
                    "192.168.1.100": "test-mapping-1",
                    "192.168.1.101": "test-mapping-2",
                    "192.168.1.102": "test-mapping-3"
                }
            },
            "ips": {
                "192.168.1.100": {
                    "host_local": "192.168.1.1:5000",
                    "host_rpc": "192.168.1.1:7152/test",
                    "info_pool": [["1111111111", "1", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.1.101": {
                    "host_local": "192.168.1.2:5000",
                    "host_rpc": "192.168.1.2:7152/test",
                    "info_pool": [["2222222222", "2", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.1.102": {
                    "host_local": "192.168.1.3:5000",
                    "host_rpc": "192.168.1.3:7152/test",
                    "info_pool": [["3333333333", "3", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        # Write test config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Track processing timeline
        processing_timeline = []
        timeline_lock = threading.Lock()
        
        def mock_process_ip_batches(ip, ip_config, global_config):
            """Mock that tracks when each IP starts and ends processing"""
            import time
            
            with timeline_lock:
                processing_timeline.append(('start', ip))
            
            # Simulate some processing time
            time.sleep(0.1)
            
            with timeline_lock:
                processing_timeline.append(('end', ip))
            
            return {
                "ip": ip,
                "success_count": 1,
                "failure_count": 0,
                "processed_batches": 1,
                "failures": []
            }
        
        # Mock the process_ip_batches function
        with patch('AutoTasks.ip_orchestrator.process_ip_batches', side_effect=mock_process_ip_batches):
            
            # Execute sequential processing
            result = process_all_ips(mode="sequential")
            
            # Verify result structure
            assert "total_ips" in result
            assert result["total_ips"] == 3
            assert "completed_ips" in result
            assert result["completed_ips"] == 3
            assert "failed_ips" in result
            assert result["failed_ips"] == 0
            assert "results" in result
            assert len(result["results"]) == 3
            
            # Verify all IPs were processed
            assert "192.168.1.100" in result["results"]
            assert "192.168.1.101" in result["results"]
            assert "192.168.1.102" in result["results"]
            
            # Verify sequential processing order
            # Each IP should complete before the next starts
            # Timeline should be: start(IP1), end(IP1), start(IP2), end(IP2), start(IP3), end(IP3)
            
            assert len(processing_timeline) == 6  # 3 IPs * 2 events (start, end)
            
            # Extract IPs in order they were processed
            processed_ips = []
            for event, ip in processing_timeline:
                if event == 'start':
                    processed_ips.append(ip)
            
            # Verify no overlap: each IP should end before next starts
            for i in range(len(processed_ips)):
                ip = processed_ips[i]
                
                # Find start and end indices for this IP
                start_idx = None
                end_idx = None
                for j, (event, event_ip) in enumerate(processing_timeline):
                    if event_ip == ip:
                        if event == 'start' and start_idx is None:
                            start_idx = j
                        elif event == 'end':
                            end_idx = j
                
                # If there's a next IP, verify current IP ends before next starts
                if i < len(processed_ips) - 1:
                    next_ip = processed_ips[i + 1]
                    next_start_idx = None
                    for j, (event, event_ip) in enumerate(processing_timeline):
                        if event_ip == next_ip and event == 'start':
                            next_start_idx = j
                            break
                    
                    # Current IP must end before next IP starts
                    assert end_idx < next_start_idx, \
                        f"IP {ip} did not complete before IP {next_ip} started"
            
            print("✓ Sequential processing integration test passed")
            print(f"  - Processed {result['total_ips']} IPs sequentially")
            print(f"  - Completed: {result['completed_ips']}, Failed: {result['failed_ips']}")
            print(f"  - Processing order verified: no overlap detected")
            print(f"  - Timeline: {processing_timeline}")
            
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_sequential_processing_order()
    print("\nAll integration tests passed!")
