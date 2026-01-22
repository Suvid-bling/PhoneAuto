"""
Integration test for multi-IP parallel processing.

This test verifies that multiple IPs can be processed concurrently in parallel mode,
and that concurrency limits are respected.

Feature: multi-ip-automation-refactor
Requirements: 5.2, 5.3
"""

import sys
import os
import json
import tempfile
import shutil
import threading
import time
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoTasks.ip_orchestrator import process_all_ips


def test_parallel_processing_concurrency():
    """
    Test parallel processing of 2-3 IPs.
    Verifies concurrency limits are respected.
    """
    # Create a temporary config file
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.json')
    
    try:
        # Setup test configuration with 4 IPs
        test_config = {
            "global": {
                "domain": "http://test.example.com",
                "image": "test-image:latest",
                "redis_url": "redis://localhost:6379/0",
                "update_account_url": "http://test.example.com/update",
                "ip_dict": {
                    "192.168.1.100": "test-mapping-1",
                    "192.168.1.101": "test-mapping-2",
                    "192.168.1.102": "test-mapping-3",
                    "192.168.1.103": "test-mapping-4"
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
                },
                "192.168.1.103": {
                    "host_local": "192.168.1.4:5000",
                    "host_rpc": "192.168.1.4:7152/test",
                    "info_pool": [["4444444444", "4", "", ""]],
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
        
        # Track concurrent processing
        active_ips = []
        max_concurrent = 0
        timeline_lock = threading.Lock()
        
        def mock_process_ip_batches(ip, ip_config, global_config):
            """Mock that tracks concurrent execution"""
            nonlocal max_concurrent
            
            with timeline_lock:
                active_ips.append(ip)
                current_concurrent = len(active_ips)
                if current_concurrent > max_concurrent:
                    max_concurrent = current_concurrent
            
            # Simulate processing time
            time.sleep(0.2)
            
            with timeline_lock:
                active_ips.remove(ip)
            
            return {
                "ip": ip,
                "success_count": 1,
                "failure_count": 0,
                "processed_batches": 1,
                "failures": []
            }
        
        # Mock the process_ip_batches function
        with patch('AutoTasks.ip_orchestrator.process_ip_batches', side_effect=mock_process_ip_batches):
            
            # Execute parallel processing with max_parallel=2
            result = process_all_ips(mode="parallel", max_parallel=2)
            
            # Verify result structure
            assert "total_ips" in result
            assert result["total_ips"] == 4
            assert "completed_ips" in result
            assert result["completed_ips"] == 4
            assert "failed_ips" in result
            assert result["failed_ips"] == 0
            assert "results" in result
            assert len(result["results"]) == 4
            
            # Verify all IPs were processed
            assert "192.168.1.100" in result["results"]
            assert "192.168.1.101" in result["results"]
            assert "192.168.1.102" in result["results"]
            assert "192.168.1.103" in result["results"]
            
            # Verify concurrency limit was respected
            # With 4 IPs and max_parallel=2, we should never have more than 2 concurrent
            assert max_concurrent <= 2, \
                f"Concurrency limit violated: {max_concurrent} IPs running concurrently (max: 2)"
            
            # Verify that parallel processing actually happened (max_concurrent > 1)
            assert max_concurrent > 1, \
                "Parallel processing did not occur (max_concurrent should be > 1)"
            
            print("✓ Parallel processing integration test passed")
            print(f"  - Processed {result['total_ips']} IPs in parallel")
            print(f"  - Completed: {result['completed_ips']}, Failed: {result['failed_ips']}")
            print(f"  - Max concurrent IPs: {max_concurrent} (limit: 2)")
            print(f"  - Concurrency limit respected: ✓")
            
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_parallel_processing_concurrency()
    print("\nAll integration tests passed!")
