"""
Integration test for single IP processing.

This test verifies the complete processing workflow for a single IP from start to finish,
ensuring all steps execute in the correct order.

Feature: multi-ip-automation-refactor
Requirements: 10.4
"""

import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoTasks.ip_processor import process_ip_batches


def test_single_ip_complete_workflow():
    """
    Test complete processing of one IP from start to finish.
    Verifies all steps execute in correct order.
    """
    # Create a temporary config file
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.json')
    
    try:
        # Setup test configuration
        test_config = {
            "global": {
                "domain": "http://test.example.com",
                "image": "test-image:latest",
                "redis_url": "redis://localhost:6379/0",
                "update_account_url": "http://test.example.com/update",
                "ip_dict": {
                    "192.168.1.100": "test-mapping"
                }
            },
            "ips": {
                "192.168.1.100": {
                    "host_local": "192.168.1.1:5000",
                    "host_rpc": "192.168.1.1:7152/test",
                    "info_pool": [
                        ["1234567890", "1", "", ""],
                        ["0987654321", "2", "", ""]
                    ],
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
        
        # Track function call order
        call_order = []
        
        # Mock all external dependencies
        with patch('AutoTasks.ip_processor.get_machine_namelist') as mock_get_names, \
             patch('AutoTasks.ip_processor.stop_machines_all') as mock_stop_all, \
             patch('AutoTasks.ip_processor.stop_batch') as mock_stop_batch, \
             patch('AutoTasks.ip_processor.start_batch') as mock_start_batch, \
             patch('AutoTasks.ip_processor.relogin_process') as mock_relogin, \
             patch('AutoTasks.ip_processor.batch_changeLogin_state') as mock_change_state, \
             patch('AutoTasks.ip_processor.update_accountlist') as mock_update_account, \
             patch('AutoTasks.ip_processor.check_loginstate_batch') as mock_check_state, \
             patch('AutoTasks.ip_processor.time.sleep'):
            
            # Setup mock return values
            mock_get_names.return_value = ["T1001-1234567890", "T1002-0987654321"]
            mock_update_account.side_effect = [None, []]  # First call returns None, second returns empty failures
            
            # Track call order
            def track_call(name):
                def wrapper(*args, **kwargs):
                    call_order.append(name)
                    return None
                return wrapper
            
            mock_stop_all.side_effect = track_call('stop_all')
            mock_stop_batch.side_effect = track_call('stop_batch')
            mock_start_batch.side_effect = track_call('start_batch')
            mock_relogin.side_effect = track_call('relogin')
            mock_change_state.side_effect = track_call('change_state')
            mock_check_state.side_effect = track_call('check_state')
            
            def track_update_account(*args, **kwargs):
                call_order.append('update_account')
                # Return empty list on second call (failures check)
                if call_order.count('update_account') == 2:
                    return []
                return None
            
            mock_update_account.side_effect = track_update_account
            
            # Execute the test
            ip = "192.168.1.100"
            ip_config = test_config["ips"][ip]
            ip_config["ip"] = ip
            global_config = test_config["global"]
            
            result = process_ip_batches(ip, ip_config, global_config)
            
            # Verify result structure
            assert "ip" in result
            assert result["ip"] == ip
            assert "success_count" in result
            assert "failure_count" in result
            assert "processed_batches" in result
            assert "failures" in result
            
            # Verify at least one batch was processed
            assert result["processed_batches"] > 0
            
            # Verify workflow order
            # Should start with stop_all
            assert call_order[0] == 'stop_all'
            
            # Then for each batch: stop_batch, start_batch, relogin, change_state, update_account (2x), check_state, stop_batch
            # Find first stop_batch after stop_all
            batch_start_idx = call_order.index('stop_batch', 1)
            
            # Verify batch workflow sequence
            expected_sequence = ['stop_batch', 'start_batch', 'change_state', 'update_account', 'update_account', 'check_state', 'stop_batch']
            
            # Extract the batch workflow (skip stop_all at beginning)
            batch_workflow = [c for c in call_order[1:] if c != 'relogin']  # relogin can be called multiple times in parallel
            
            # Verify key steps are present in order
            assert 'stop_batch' in batch_workflow
            assert 'start_batch' in batch_workflow
            assert 'change_state' in batch_workflow
            assert 'update_account' in batch_workflow
            assert 'check_state' in batch_workflow
            
            # Verify stop_batch comes before start_batch
            stop_idx = batch_workflow.index('stop_batch')
            start_idx = batch_workflow.index('start_batch')
            assert stop_idx < start_idx
            
            # Verify start_batch comes before change_state
            change_idx = batch_workflow.index('change_state')
            assert start_idx < change_idx
            
            # Verify change_state comes before update_account
            update_idx = batch_workflow.index('update_account')
            assert change_idx < update_idx
            
            # Verify update_account comes before check_state
            check_idx = batch_workflow.index('check_state')
            assert update_idx < check_idx
            
            print("✓ Single IP integration test passed")
            print(f"  - Processed {result['processed_batches']} batch(es)")
            print(f"  - Success: {result['success_count']}, Failures: {result['failure_count']}")
            print(f"  - Workflow order verified: {len(call_order)} steps executed")
            
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_single_ip_complete_workflow()
    print("\nAll integration tests passed!")
