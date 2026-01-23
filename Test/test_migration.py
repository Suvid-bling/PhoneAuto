"""
Test the migrate_config function in setting.py.
"""
import json
import os
import sys
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setting import migrate_config, MigrationError


def test_migrate_single_ip_config():
    """Test migrating a single-IP config to multi-IP format."""
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a single-IP config
        single_ip_config = {
            "ip": "192.168.124.17",
            "host_local": "192.168.124.5:5000",
            "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
            "domain": "http://192.168.124.5:8002",
            "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base",
            "redis_url": "redis://zjl:password@192.168.223.202:6386/2",
            "update_account_url": "http://192.168.223.144:9000/android/updateAccountHeaders/",
            "ip_dict": {
                "192.168.124.17": "3-3001-192_168_124_17"
            },
            "info_pool": [
                ["2364180493", "2", "", ""],
                ["2364180320", "1", "", ""]
            ],
            "info_list": [],
            "success_list": [["6727221118", "1", "", ""]],
            "failure_list": []
        }
        
        # Write the single-IP config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(single_ip_config, f, indent=2)
        
        # Run migration
        result = migrate_config(config_path)
        
        # Verify migration succeeded
        assert result == True, "Migration should return True"
        
        # Load the migrated config
        with open(config_path, 'r', encoding='utf-8') as f:
            migrated_config = json.load(f)
        
        # Verify structure
        assert "global" in migrated_config, "Migrated config should have 'global' section"
        assert "ips" in migrated_config, "Migrated config should have 'ips' section"
        
        # Verify global fields preserved
        assert migrated_config["global"]["domain"] == single_ip_config["domain"]
        assert migrated_config["global"]["image"] == single_ip_config["image"]
        assert migrated_config["global"]["redis_url"] == single_ip_config["redis_url"]
        assert migrated_config["global"]["update_account_url"] == single_ip_config["update_account_url"]
        assert migrated_config["global"]["ip_dict"] == single_ip_config["ip_dict"]
        
        # Verify IP-specific fields moved
        ip = "192.168.124.17"
        assert ip in migrated_config["ips"], f"IP {ip} should be in 'ips' section"
        assert migrated_config["ips"][ip]["host_local"] == single_ip_config["host_local"]
        assert migrated_config["ips"][ip]["host_rpc"] == single_ip_config["host_rpc"]
        assert migrated_config["ips"][ip]["info_pool"] == single_ip_config["info_pool"]
        assert migrated_config["ips"][ip]["info_list"] == single_ip_config["info_list"]
        assert migrated_config["ips"][ip]["success_list"] == single_ip_config["success_list"]
        assert migrated_config["ips"][ip]["failure_list"] == single_ip_config["failure_list"]
        
        # Verify backup was created
        backup_files = [f for f in os.listdir(tmpdir) if f.startswith('config.json.backup')]
        assert len(backup_files) == 1, "Backup file should be created"
        
        print("✓ test_migrate_single_ip_config passed")


def test_already_migrated_config():
    """Test that migration returns False for already migrated config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a multi-IP config (already migrated)
        multi_ip_config = {
            "global": {
                "domain": "http://192.168.124.5:8002"
            },
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        # Run migration
        result = migrate_config(config_path)
        
        # Should return False (no migration needed)
        assert result == False, "Migration should return False for already migrated config"
        
        print("✓ test_already_migrated_config passed")


def test_missing_ip_field():
    """Test that migration raises error for config without 'ip' field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create an invalid config (no 'ip' field, not multi-IP format)
        invalid_config = {
            "domain": "http://192.168.124.5:8002",
            "info_pool": []
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        # Run migration - should raise MigrationError
        try:
            migrate_config(config_path)
            assert False, "Should have raised MigrationError"
        except MigrationError as e:
            assert "missing 'ip' field" in str(e)
        
        print("✓ test_missing_ip_field passed")


def test_missing_config_file():
    """Test that migration raises error for missing config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'nonexistent.json')
        
        try:
            migrate_config(config_path)
            assert False, "Should have raised MigrationError"
        except MigrationError as e:
            assert "not found" in str(e)
        
        print("✓ test_missing_config_file passed")


def test_migration_with_empty_lists():
    """Test migration with empty info_pool, info_list, etc."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a single-IP config with empty lists
        single_ip_config = {
            "ip": "192.168.124.18",
            "host_local": "192.168.124.5:5000",
            "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
            "domain": "http://192.168.124.5:8002",
            "info_pool": [],
            "info_list": [],
            "success_list": [],
            "failure_list": []
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(single_ip_config, f, indent=2)
        
        result = migrate_config(config_path)
        assert result == True
        
        with open(config_path, 'r', encoding='utf-8') as f:
            migrated = json.load(f)
        
        ip = "192.168.124.18"
        assert migrated["ips"][ip]["info_pool"] == []
        assert migrated["ips"][ip]["info_list"] == []
        assert migrated["ips"][ip]["success_list"] == []
        assert migrated["ips"][ip]["failure_list"] == []
        
        print("✓ test_migration_with_empty_lists passed")


def test_migration_with_missing_optional_fields():
    """Test migration when some optional fields are missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a minimal single-IP config (missing some optional fields)
        single_ip_config = {
            "ip": "192.168.124.19",
            "host_local": "192.168.124.5:5000",
            "domain": "http://192.168.124.5:8002",
            "info_pool": [["1234567890", "1", "", ""]]
            # Missing: host_rpc, image, redis_url, update_account_url, ip_dict
            # Missing: info_list, success_list, failure_list
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(single_ip_config, f, indent=2)
        
        result = migrate_config(config_path)
        assert result == True
        
        with open(config_path, 'r', encoding='utf-8') as f:
            migrated = json.load(f)
        
        ip = "192.168.124.19"
        # IP-specific fields should have defaults
        assert migrated["ips"][ip]["info_pool"] == [["1234567890", "1", "", ""]]
        assert migrated["ips"][ip]["info_list"] == []
        assert migrated["ips"][ip]["success_list"] == []
        assert migrated["ips"][ip]["failure_list"] == []
        assert migrated["ips"][ip]["host_rpc"] == ""  # Default empty string
        
        # Global fields should only include what was present
        assert migrated["global"]["domain"] == "http://192.168.124.5:8002"
        
        print("✓ test_migration_with_missing_optional_fields passed")


def test_backup_file_creation():
    """Test that backup file is created with correct content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a single-IP config
        original_config = {
            "ip": "192.168.124.20",
            "host_local": "192.168.124.5:5000",
            "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
            "domain": "http://192.168.124.5:8002",
            "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base",
            "info_pool": [["9876543210", "3", "", ""]],
            "info_list": [["1111111111", "1", "", ""]],
            "success_list": [],
            "failure_list": [["2222222222", "2", "", ""]]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(original_config, f, indent=2)
        
        # Run migration
        result = migrate_config(config_path)
        assert result == True
        
        # Find the backup file
        backup_files = [f for f in os.listdir(tmpdir) if f.startswith('config.json.backup')]
        assert len(backup_files) == 1, "Exactly one backup file should be created"
        
        # Verify backup content matches original
        backup_path = os.path.join(tmpdir, backup_files[0])
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = json.load(f)
        
        assert backup_content == original_config, "Backup content should match original config"
        
        # Verify backup file name format (config.json.backup.YYYYMMDD_HHMMSS)
        backup_name = backup_files[0]
        assert backup_name.startswith('config.json.backup.'), "Backup should have correct prefix"
        timestamp_part = backup_name.replace('config.json.backup.', '')
        assert len(timestamp_part) == 15, "Timestamp should be in YYYYMMDD_HHMMSS format"
        assert timestamp_part[8] == '_', "Timestamp should have underscore separator"
        
        print("✓ test_backup_file_creation passed")


if __name__ == "__main__":
    test_migrate_single_ip_config()
    test_already_migrated_config()
    test_missing_ip_field()
    test_missing_config_file()
    test_migration_with_empty_lists()
    test_migration_with_missing_optional_fields()
    test_backup_file_creation()
    print("\n✓ All migration tests passed!")
