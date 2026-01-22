"""
Test configuration validation functionality.
"""
import json
import os
import sys
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setting import load_config, validate_config, ConfigValidationError


def test_valid_config():
    """Test that a valid configuration passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        valid_config = {
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
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(valid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            # Should not raise any exception
            config = load_config()
            assert config is not None
            print("✓ test_valid_config passed")
        finally:
            os.chdir(original_dir)


def test_missing_global_section():
    """Test that missing 'global' section raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        invalid_config = {
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
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "global" in str(e).lower()
                assert "missing" in str(e).lower()
            
            print("✓ test_missing_global_section passed")
        finally:
            os.chdir(original_dir)


def test_missing_ips_section():
    """Test that missing 'ips' section raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        invalid_config = {
            "global": {
                "domain": "http://192.168.124.5:8002"
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "ips" in str(e).lower()
                assert "missing" in str(e).lower()
            
            print("✓ test_missing_ips_section passed")
        finally:
            os.chdir(original_dir)


def test_empty_ips_section():
    """Test that empty 'ips' section raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        invalid_config = {
            "global": {},
            "ips": {}
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "at least one" in str(e).lower()
            
            print("✓ test_empty_ips_section passed")
        finally:
            os.chdir(original_dir)


def test_missing_required_ip_field():
    """Test that missing required IP field raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Missing 'info_list' field
        invalid_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "192.168.124.17" in str(e)
                assert "info_list" in str(e)
                assert "missing" in str(e).lower()
            
            print("✓ test_missing_required_ip_field passed")
        finally:
            os.chdir(original_dir)


def test_invalid_field_type_list():
    """Test that invalid field type (list field as non-list) raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # info_pool should be a list, not a string
        invalid_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": "not a list",
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "192.168.124.17" in str(e)
                assert "info_pool" in str(e)
                assert "must be a list" in str(e).lower()
            
            print("✓ test_invalid_field_type_list passed")
        finally:
            os.chdir(original_dir)


def test_invalid_field_type_string():
    """Test that invalid field type (string field as non-string) raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # host_local should be a string, not a list
        invalid_config = {
            "global": {},
            "ips": {
                "192.168.124.17": {
                    "host_local": ["not", "a", "string"],
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "192.168.124.17" in str(e)
                assert "host_local" in str(e)
                assert "must be a string" in str(e).lower()
            
            print("✓ test_invalid_field_type_string passed")
        finally:
            os.chdir(original_dir)


def test_ips_not_dict():
    """Test that 'ips' section as non-dict raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        invalid_config = {
            "global": {},
            "ips": ["not", "a", "dict"]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "ips" in str(e).lower()
                assert "must be a dictionary" in str(e).lower()
            
            print("✓ test_ips_not_dict passed")
        finally:
            os.chdir(original_dir)


def test_ip_config_not_dict():
    """Test that IP configuration as non-dict raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        invalid_config = {
            "global": {},
            "ips": {
                "192.168.124.17": "not a dict"
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "192.168.124.17" in str(e)
                assert "must be a dictionary" in str(e).lower()
            
            print("✓ test_ip_config_not_dict passed")
        finally:
            os.chdir(original_dir)


def test_multiple_ips_valid():
    """Test that configuration with multiple valid IPs passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        valid_config = {
            "global": {
                "domain": "http://192.168.124.5:8002"
            },
            "ips": {
                "192.168.124.17": {
                    "host_local": "192.168.124.5:5000",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.18": {
                    "host_local": "192.168.124.5:5001",
                    "info_pool": [["1234567890", "1", "", ""]],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                },
                "192.168.124.19": {
                    "host_local": "192.168.124.5:5002",
                    "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
                    "info_pool": [],
                    "info_list": [],
                    "success_list": [],
                    "failure_list": []
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(valid_config, f, indent=2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            config = load_config()
            assert len(config["ips"]) == 3
            print("✓ test_multiple_ips_valid passed")
        finally:
            os.chdir(original_dir)


def test_invalid_json():
    """Test that invalid JSON raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, 'config.json')
        
        # Write invalid JSON
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('{"global": {}, "ips": {')  # Incomplete JSON
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "json" in str(e).lower()
            
            print("✓ test_invalid_json passed")
        finally:
            os.chdir(original_dir)


def test_missing_config_file():
    """Test that missing config file raises ConfigValidationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            try:
                load_config()
                assert False, "Should have raised ConfigValidationError"
            except ConfigValidationError as e:
                assert "not found" in str(e).lower()
            
            print("✓ test_missing_config_file passed")
        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    test_valid_config()
    test_missing_global_section()
    test_missing_ips_section()
    test_empty_ips_section()
    test_missing_required_ip_field()
    test_invalid_field_type_list()
    test_invalid_field_type_string()
    test_ips_not_dict()
    test_ip_config_not_dict()
    test_multiple_ips_valid()
    test_invalid_json()
    test_missing_config_file()
    print("\n✓ All validation tests passed!")
