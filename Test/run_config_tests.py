#!/usr/bin/env python3
"""
Run all configuration-related tests.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
import test_migration
import test_config_functions
import test_config_validation

def run_all_tests():
    """Run all configuration tests."""
    print("=" * 60)
    print("Running Configuration Tests")
    print("=" * 60)
    print()
    
    print("--- Migration Tests ---")
    test_migration.test_migrate_single_ip_config()
    test_migration.test_already_migrated_config()
    test_migration.test_missing_ip_field()
    test_migration.test_missing_config_file()
    test_migration.test_migration_with_empty_lists()
    test_migration.test_migration_with_missing_optional_fields()
    test_migration.test_backup_file_creation()
    print()
    
    print("--- Configuration Function Tests ---")
    test_config_functions.test_load_config_multi_ip()
    test_config_functions.test_get_ip_config()
    test_config_functions.test_get_ip_config_missing_ip()
    test_config_functions.test_get_all_ips()
    test_config_functions.test_write_ip_config()
    test_config_functions.test_append_ip_config()
    test_config_functions.test_clear_ip_config()
    test_config_functions.test_configuration_isolation()
    print()
    
    print("--- Configuration Validation Tests ---")
    test_config_validation.test_valid_config()
    test_config_validation.test_missing_global_section()
    test_config_validation.test_missing_ips_section()
    test_config_validation.test_empty_ips_section()
    test_config_validation.test_missing_required_ip_field()
    test_config_validation.test_invalid_field_type_list()
    test_config_validation.test_invalid_field_type_string()
    test_config_validation.test_ips_not_dict()
    test_config_validation.test_ip_config_not_dict()
    test_config_validation.test_multiple_ips_valid()
    test_config_validation.test_invalid_json()
    test_config_validation.test_missing_config_file()
    print()
    
    print("=" * 60)
    print("✓ ALL CONFIGURATION TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_tests()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
