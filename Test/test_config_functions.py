"""
Test the configuration management functions in setting.py.
"""
import json
import os
import sys
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setting import (
    load_config, get_ip_config, get_all_ips,
    write_ip_config, append_ip_config, clear_ip_config,
    IPNotFoundError
)


def test_load_config_multi_ip():
    """Test loading a multi-IP configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Create a multi-IP config
        multi_ip_config = {
            "global": {
                "domain": "http://192.168.124.5:8002",
                "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base"
            },
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                    "info_pool": [["2364180493", "2", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.18": {
                    "host_local": "192.168.124.5:5000",
                    "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                    "info_pool": [["4376662009", "7", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        # Change to temp directory to test load_config
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            config = load_config()
            
            assert "global" in config
            assert "ips" in config
            assert "192.168.124.17" in config["ips"]
            assert "192.168.124.18" in config["ips"]
            
            print("✓ test_load_config_multi_ip passed")
        finally:
            os.chdir(original_dir)


def test_get_ip_config():
    """Test retrieving IP-specific configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {
                "domain": "http://192.168.124.5:8002"
            },
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                    "info_pool": [["2364180493", "2", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            ip_config = get_ip_config("192.168.124.17")
            
            assert ip_config["ip"] == "192.168.124.17"
            assert ip_config["host_local"] == "192.168.124.5:5000"
            assert ip_config["host_rpc"] == "36.133.80.179:7152/3001-MYTSDK"
            assert len(ip_config["info_pool"]) == 1
            
            print("✓ test_get_ip_config passed")
        finally:
            os.chdir(original_dir)


def test_get_ip_config_missing_ip():
    """Test that get_ip_config raises IPNotFoundError for missing IP."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                get_ip_config("192.168.124.99")
                assert False, "Should have raised IPNotFoundError"
            except IPNotFoundError as e:
                assert "192.168.124.99" in str(e)
                assert "not found" in str(e)
            
            print("✓ test_get_ip_config_missing_ip passed")
        finally:
            os.chdir(original_dir)


def test_get_all_ips():
    """Test retrieving all configured IP addresses."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.18": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.19": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            ips = get_all_ips()
            
            assert len(ips) == 3
            assert "192.168.124.17" in ips
            assert "192.168.124.18" in ips
            assert "192.168.124.19" in ips
            
            print("✓ test_get_all_ips passed")
        finally:
            os.chdir(original_dir)


def test_write_ip_config():
    """Test writing to IP-specific configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Write a new value
            result = write_ip_config("192.168.124.17", "info_list", [["1234567890", "1", "", ""]])
            assert result == True
            
            # Verify the write
            config = load_config()
            assert config["ips"]["192.168.124.17"]["info_list"] == [["1234567890", "1", "", ""]]
            
            # Verify other IPs not affected (isolation)
            assert config["ips"]["192.168.124.17"]["info_pool"] == []
            
            print("✓ test_write_ip_config passed")
        finally:
            os.chdir(original_dir)


def test_append_ip_config():
    """Test appending to IP-specific list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [["1111111111", "1", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Append a new value
            result = append_ip_config("192.168.124.17", "failure_list", ["2222222222", "2", "", ""])
            assert result == True
            
            # Verify the append
            config = load_config()
            assert len(config["ips"]["192.168.124.17"]["failure_list"]) == 1
            assert config["ips"]["192.168.124.17"]["failure_list"][0] == ["2222222222", "2", "", ""]
            
            # Append another value
            append_ip_config("192.168.124.17", "failure_list", ["3333333333", "3", "", ""])
            config = load_config()
            assert len(config["ips"]["192.168.124.17"]["failure_list"]) == 2
            
            # Try to append duplicate (should not add)
            append_ip_config("192.168.124.17", "failure_list", ["2222222222", "2", "", ""])
            config = load_config()
            assert len(config["ips"]["192.168.124.17"]["failure_list"]) == 2
            
            print("✓ test_append_ip_config passed")
        finally:
            os.chdir(original_dir)


def test_clear_ip_config():
    """Test clearing IP-specific configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [["1111111111", "1", "", ""], ["2222222222", "2", "", ""]],
                    "info_list": [["3333333333", "3", "", ""]],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Clear info_list
            result = clear_ip_config("192.168.124.17", "info_list")
            assert result == True
            
            # Verify the clear
            config = load_config()
            assert config["ips"]["192.168.124.17"]["info_list"] == []
            
            # Verify other fields not affected
            assert len(config["ips"]["192.168.124.17"]["info_pool"]) == 2
            
            print("✓ test_clear_ip_config passed")
        finally:
            os.chdir(original_dir)


def test_configuration_isolation():
    """Test that operations on one IP don't affect other IPs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        multi_ip_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [["1111111111", "1", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.18": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [["2222222222", "2", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(multi_ip_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Modify IP 17
            write_ip_config("192.168.124.17", "info_list", [["3333333333", "3", "", ""]])
            append_ip_config("192.168.124.17", "failure_list", ["4444444444", "4", "", ""])
            
            # Verify IP 18 is unchanged
            config = load_config()
            assert config["ips"]["192.168.124.18"]["info_pool"] == [["2222222222", "2", "", ""]]
            assert config["ips"]["192.168.124.18"]["info_list"] == []
            assert config["ips"]["192.168.124.18"]["failure_list"] == []
            
            # Verify IP 17 was modified
            assert config["ips"]["192.168.124.17"]["info_list"] == [["3333333333", "3", "", ""]]
            assert config["ips"]["192.168.124.17"]["failure_list"] == [["4444444444", "4", "", ""]]
            
            print("✓ test_configuration_isolation passed")
        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    test_load_config_multi_ip()
    test_get_ip_config()
    test_get_ip_config_missing_ip()
    test_get_all_ips()
    test_write_ip_config()
    test_append_ip_config()
    test_clear_ip_config()
    test_configuration_isolation()
    print("\n✓ All configuration function tests passed!")
