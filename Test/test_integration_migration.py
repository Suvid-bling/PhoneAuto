"""
Integration test for configuration migration workflow.

This test verifies the complete migration workflow from single-IP to multi-IP format,
including backup creation and processing the migrated configuration.

Feature: multi-ip-automation-refactor
Requirements: 1.3, 9.5
"""

import sys
import os
import json
import tempfile
import shutil
import glob
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setting import migrate_config, load_config, get_ip_config
from AutoTasks.ip_orchestrator import process_all_ips


def test_migration_and_processing_workflow():
    """
    Test migrating a single-IP config and processing the migrated config.
    Verifies backup file creation and successful processing.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.json')
    
    try:
        # Setup single-IP configuration (legacy format)
        single_ip_config = {
            "ip": "192.168.1.100",
            "host_local": "192.168.1.1:5000",
            "host_rpc": "192.168.1.1:7152/test",
            "domain": "http://test.example.com",
            "image": "test-image:latest",
            "redis_url": "redis://localhost:6379/0",
            "update_account_url": "http://test.example.com/update",
            "ip_dict": {
                "192.168.1.100": "test-mapping"
            },
            "info_pool": [
                ["1234567890", "1", "", ""],
                ["0987654321", "2", "", ""]
            ],
            "info_list": [],
            "success_list": [],
            "failure_list": []
        }
        
        # Write single-IP config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(single_ip_config, f, indent=2)
        
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Step 1: Migrate the configuration
        print("Step 1: Migrating single-IP configuration...")
        migration_result = migrate_config(config_path)
        
        # Verify migration succeeded
        assert migration_result == True, "Migration should return True"
        
        # Step 2: Verify backup file was created
        print("Step 2: Verifying backup file creation...")
        backup_files = glob.glob(f"{config_path}.backup.*")
        assert len(backup_files) == 1, f"Expected 1 backup file, found {len(backup_files)}"
        print(f"  - Backup created: {backup_files[0]}")
        
        # Verify backup contains original single-IP config
        with open(backup_files[0], 'r', encoding='utf-8') as f:
            backup_config = json.load(f)
        assert backup_config["ip"] == "192.168.1.100"
        assert "ips" not in backup_config  # Should be single-IP format
        
        # Step 3: Verify migrated configuration structure
        print("Step 3: Verifying migrated configuration...")
        migrated_config = load_config()
        
        # Check multi-IP structure
        assert "global" in migrated_config
        assert "ips" in migrated_config
        assert "192.168.1.100" in migrated_config["ips"]
        
        # Verify global fields were preserved
        assert migrated_config["global"]["domain"] == "http://test.example.com"
        assert migrated_config["global"]["image"] == "test-image:latest"
        assert migrated_config["global"]["redis_url"] == "redis://localhost:6379/0"
        assert migrated_config["global"]["update_account_url"] == "http://test.example.com/update"
        
        # Verify IP-specific fields were moved
        ip_config = migrated_config["ips"]["192.168.1.100"]
        assert ip_config["host_local"] == "192.168.1.1:5000"
        assert ip_config["host_rpc"] == "192.168.1.1:7152/test"
        assert len(ip_config["info_pool"]) == 2
        assert ip_config["info_pool"][0] == ["1234567890", "1", "", ""]
        assert ip_config["info_pool"][1] == ["0987654321", "2", "", ""]
        
        # Step 4: Verify get_ip_config works with migrated config
        print("Step 4: Testing get_ip_config with migrated configuration...")
        retrieved_config = get_ip_config("192.168.1.100")
        assert retrieved_config["ip"] == "192.168.1.100"
        assert retrieved_config["host_local"] == "192.168.1.1:5000"
        assert len(retrieved_config["info_pool"]) == 2
        
        # Step 5: Process the migrated configuration
        print("Step 5: Processing migrated configuration...")
        
        def mock_process_ip_batches(ip, ip_config, global_config):
            """Mock processing function"""
            return {
                "ip": ip,
                "success_count": 2,
                "failure_count": 0,
                "processed_batches": 1,
                "failures": []
            }
        
        with patch('AutoTasks.ip_orchestrator.process_ip_batches', side_effect=mock_process_ip_batches):
            result = process_all_ips(mode="sequential")
            
            # Verify processing succeeded
            assert result["total_ips"] == 1
            assert result["completed_ips"] == 1
            assert result["failed_ips"] == 0
            assert "192.168.1.100" in result["results"]
            assert result["results"]["192.168.1.100"]["success_count"] == 2
        
        # Step 6: Verify second migration attempt returns False (already migrated)
        print("Step 6: Verifying idempotency (second migration should be skipped)...")
        second_migration = migrate_config(config_path)
        assert second_migration == False, "Second migration should return False (already migrated)"
        
        # Verify only one backup file exists (no new backup created)
        backup_files_after = glob.glob(f"{config_path}.backup.*")
        assert len(backup_files_after) == 1, "Should still have only 1 backup file"
        
        print("✓ Migration workflow integration test passed")
        print("  - Single-IP config migrated to multi-IP format")
        print("  - Backup file created successfully")
        print("  - Global fields preserved")
        print("  - IP-specific fields moved correctly")
        print("  - Migrated config processed successfully")
        print("  - Idempotency verified (second migration skipped)")
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_migration_and_processing_workflow()
    print("\nAll integration tests passed!")
