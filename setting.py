import json
from typing import Any


# Custom exception for missing IP addresses
class IPNotFoundError(Exception):
    """Raised when an IP address is not found in the configuration."""
    def __init__(self, ip: str):
        self.ip = ip
        super().__init__(f"IP address {ip} not found in configuration")


# Custom exception for configuration validation errors
class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    def __init__(self, message: str):
        super().__init__(message)


def validate_config(config: dict) -> None:
    """
    Validate the structure and content of a multi-IP configuration.
    
    This function checks that:
    - The configuration has required "global" and "ips" sections
    - Each IP configuration has all required fields
    - Field types are correct (lists for device lists, strings for hosts)
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigValidationError: If validation fails with specific error message
        
    Requirements: 1.5, 8.5
    """
    # Check for required top-level sections
    if "global" not in config:
        raise ConfigValidationError("Configuration missing required 'global' section")
    
    if "ips" not in config:
        raise ConfigValidationError("Configuration missing required 'ips' section")
    
    # Validate global section has required fields
    required_global_fields = ["host_local", "host_rpc"]
    for field in required_global_fields:
        if field not in config["global"]:
            raise ConfigValidationError(f"Global configuration missing required field '{field}'")
        if not isinstance(config["global"][field], str):
            raise ConfigValidationError(
                f"Global field '{field}' must be a string, got {type(config['global'][field]).__name__}"
            )
    
    # Validate that ips is a dictionary
    if not isinstance(config["ips"], dict):
        raise ConfigValidationError("'ips' section must be a dictionary")
    
    # Check that there is at least one IP configured
    if len(config["ips"]) == 0:
        raise ConfigValidationError("'ips' section must contain at least one IP configuration")
    
    # Required fields for each IP configuration
    required_ip_fields = ["info_pool", "info_list", "success_list", "failure_list"]
    
    # Validate each IP configuration
    for ip, ip_config in config["ips"].items():
        if not isinstance(ip_config, dict):
            raise ConfigValidationError(f"Configuration for IP '{ip}' must be a dictionary")
        
        # Check for required fields
        for field in required_ip_fields:
            if field not in ip_config:
                raise ConfigValidationError(
                    f"IP '{ip}' configuration missing required field '{field}'"
                )
        
        # Validate field types
        list_fields = ["info_pool", "info_list", "success_list", "failure_list"]
        for field in list_fields:
            if not isinstance(ip_config[field], list):
                raise ConfigValidationError(
                    f"IP '{ip}' field '{field}' must be a list, got {type(ip_config[field]).__name__}"
                )


def load_config() -> dict:
    """
    Load the complete multi-IP configuration from config.json.
    
    Returns:
        dict: Configuration with "global" and "ips" sections
        {
            "global": {...},
            "ips": {
                "192.168.124.17": {...},
                ...
            }
        }
        
    Raises:
        ConfigValidationError: If the configuration structure is invalid
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate configuration structure
        validate_config(config)
        
        return config
    except json.JSONDecodeError as e:
        raise ConfigValidationError(f"Invalid JSON in config.json: {e}")
    except FileNotFoundError:
        raise ConfigValidationError("Configuration file 'config.json' not found")
    except ConfigValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        raise ConfigValidationError(f"Error loading configuration: {e}")


def get_ip_config(ip: str) -> dict:
    """
    Get configuration for a specific IP address.
    
    Args:
        ip: IP address to retrieve configuration for
        
    Returns:
        dict: IP-specific configuration containing:
            - ip: The IP address
            - host_local: Local host address
            - host_rpc: RPC host address
            - info_pool: List of devices available for processing
            - info_list: List of devices currently being processed
            - success_list: List of devices that succeeded
            - failure_list: List of devices that failed
            
    Raises:
        IPNotFoundError: If the IP address is not found in configuration
    """
    config = load_config()
    
    if "ips" not in config or ip not in config["ips"]:
        raise IPNotFoundError(ip)
    
    ip_config = config["ips"][ip].copy()
    ip_config["ip"] = ip
    return ip_config


def get_all_ips() -> list:
    """
    Get list of all configured IP addresses.
    
    Returns:
        list: List of IP address strings
    """
    config = load_config()
    
    if "ips" not in config:
        return []
    
    return list(config["ips"].keys())


def write_ip_config(ip: str, key: str, value: Any) -> bool:
    """
    Write value to a specific key for a specific IP.
    
    Args:
        ip: IP address to modify
        key: Configuration key to write to
        value: Value to write
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        IPNotFoundError: If the IP address is not found in configuration
    """
    try:
        config = load_config()
        
        if "ips" not in config or ip not in config["ips"]:
            raise IPNotFoundError(ip)
        
        config["ips"][ip][key] = value
        
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json_multi_ip(config, f)
        
        return True
    except IPNotFoundError:
        raise
    except Exception as e:
        print(f"Error writing IP config: {e}")
        return False


def append_ip_config(ip: str, key: str, value: Any) -> bool:
    """
    Append value to a list key for a specific IP.
    Only appends if the value doesn't already exist in the list.
    
    Args:
        ip: IP address to modify
        key: Configuration key (must be a list) to append to
        value: Value to append
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        IPNotFoundError: If the IP address is not found in configuration
    """
    try:
        config = load_config()
        
        if "ips" not in config or ip not in config["ips"]:
            raise IPNotFoundError(ip)
        
        if key not in config["ips"][ip]:
            config["ips"][ip][key] = []
        
        # Only append if value doesn't already exist
        if value not in config["ips"][ip][key]:
            config["ips"][ip][key].append(value)
        
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json_multi_ip(config, f)
        
        return True
    except IPNotFoundError:
        raise
    except Exception as e:
        print(f"Error appending IP config: {e}")
        return False


def clear_ip_config(ip: str, key: str) -> bool:
    """
    Clear a key's value for a specific IP.
    
    Args:
        ip: IP address to modify
        key: Configuration key to clear
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        IPNotFoundError: If the IP address is not found in configuration
    """
    try:
        config = load_config()
        
        if "ips" not in config or ip not in config["ips"]:
            raise IPNotFoundError(ip)
        
        if key in config["ips"][ip]:
            if isinstance(config["ips"][ip][key], list):
                config["ips"][ip][key] = []
            elif isinstance(config["ips"][ip][key], dict):
                config["ips"][ip][key] = {}
            else:
                config["ips"][ip][key] = ""
        
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json_multi_ip(config, f)
        
        return True
    except IPNotFoundError:
        raise
    except Exception as e:
        print(f"Error clearing IP config: {e}")
        return False


class MigrationError(Exception):
    """Raised when configuration migration fails."""
    def __init__(self, message: str):
        super().__init__(message)


def migrate_config(config_path: str = 'config.json') -> bool:
    """
    Migrate single-IP configuration to multi-IP format.
    
    This function converts a legacy single-IP config.json to the new multi-IP format:
    - Extracts the current "ip" field and creates an IP entry under "ips"
    - Moves info_pool, info_list, success_list, failure_list under the IP's config
    - Preserves global fields (domain, image, redis_url, update_account_url, ip_dict)
    - Creates a backup of the original config.json
    
    Args:
        config_path: Path to the config.json file (default: 'config.json')
        
    Returns:
        bool: True if migration successful, False if already migrated or no migration needed
        
    Raises:
        MigrationError: If migration fails (e.g., backup creation fails, invalid config)
        
    Requirements: 1.3, 9.1, 9.2, 9.3, 9.4, 9.5
    """
    import os
    import shutil
    from datetime import datetime
    
    try:
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check if already in multi-IP format
        if "ips" in config and "global" in config:
            print("Configuration is already in multi-IP format. No migration needed.")
            return False
        
        # Check if this is a single-IP config (has "ip" field at root level)
        if "ip" not in config:
            raise MigrationError("Invalid configuration: missing 'ip' field for single-IP config")
        
        # Create backup before migration
        backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(config_path, backup_path)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            raise MigrationError(f"Failed to create backup: {e}")
        
        # Extract the IP address
        ip_address = config["ip"]
        
        # Define global fields to preserve at root level
        global_fields = ["domain", "image", "redis_url", "update_account_url", "ip_dict", "host_local", "host_rpc"]
        
        # Define IP-specific fields to move under the IP's config
        ip_specific_fields = ["info_pool", "info_list", "success_list", "failure_list"]
        
        # Build the new multi-IP configuration
        new_config = {
            "global": {},
            "ips": {}
        }
        
        # Move global fields
        for field in global_fields:
            if field in config:
                new_config["global"][field] = config[field]
        
        # Create IP-specific configuration
        ip_config = {}
        for field in ip_specific_fields:
            if field in config:
                ip_config[field] = config[field]
            else:
                # Initialize with empty list for list fields
                if field in ["info_pool", "info_list", "success_list", "failure_list"]:
                    ip_config[field] = []
                else:
                    ip_config[field] = ""
        
        # Add the IP configuration under "ips"
        new_config["ips"][ip_address] = ip_config
        
        # Write the new multi-IP configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            _write_formatted_json_multi_ip(new_config, f)
        
        print(f"Migration successful. IP '{ip_address}' migrated to multi-IP format.")
        return True
        
    except MigrationError:
        raise
    except json.JSONDecodeError as e:
        raise MigrationError(f"Invalid JSON in config file: {e}")
    except FileNotFoundError:
        raise MigrationError(f"Config file not found: {config_path}")
    except Exception as e:
        raise MigrationError(f"Migration failed: {e}")


def _write_formatted_json_multi_ip(config: dict, file) -> None:
    """
    Write multi-IP JSON with custom formatting.
    Inner arrays on single lines, outer structure indented.
    """
    def write_value(value, indent_level=1):
        indent = "  " * indent_level
        
        if isinstance(value, dict):
            file.write('{\n')
            keys = list(value.keys())
            for i, k in enumerate(keys):
                file.write(f'{indent}  "{k}": ')
                write_value(value[k], indent_level + 1)
                if i < len(keys) - 1:
                    file.write(',\n')
                else:
                    file.write('\n')
            file.write(f'{indent}}}')
        elif isinstance(value, list) and value and isinstance(value[0], list):
            # List of lists - each inner list on one line
            file.write('[\n')
            for j, item in enumerate(value):
                file.write(f'{indent}  {json.dumps(item, ensure_ascii=False)}')
                if j < len(value) - 1:
                    file.write(',\n')
                else:
                    file.write('\n')
            file.write(f'{indent}]')
        else:
            file.write(json.dumps(value, ensure_ascii=False))
    
    file.write('{\n')
    keys = list(config.keys())
    for i, key in enumerate(keys):
        file.write(f'  "{key}": ')
        write_value(config[key], 1)
        if i < len(keys) - 1:
            file.write(',\n')
        else:
            file.write('\n')
    file.write('}\n')


def group_pools(info_pools:dict):
    #Group items by their index (second element)
    from collections import defaultdict
    
    grouped = defaultdict(list)
    for item in info_pools:
        index = item[1]
        grouped[index].append(item)
    
    # Convert to list of lists, sorted by index
    group_list = [grouped[i] for i in sorted(grouped.keys())]
    return group_list

#The Goal is slice pool but avoid select same index list in one slice
def batch_slice(groups:list, batch_size=4):
    """
    Select items from different groups to avoid same index in one batch.
    Each batch contains batch_size items from different groups.
    """ 
    import random
    
    # Create a copy to modify
    groups_copy = [group[:] for group in groups]
    
    slice_quene = []
    
    while any(len(group) > 0 for group in groups_copy):
        batch = []
        
        # Get available groups (non-empty)
        available_groups = [i for i, group in enumerate(groups_copy) if len(group) > 0]
        
        # If we have enough groups, select batch_size items
        if len(available_groups) >= batch_size:
            selected_groups = random.sample(available_groups, batch_size)
        else:
            # Use all remaining groups
            selected_groups = available_groups
        
        # Pick one item from each selected group
        for group_idx in selected_groups:
            item = groups_copy[group_idx].pop(0)
            batch.append(item)
        
        slice_quene.append(batch)
    
    return slice_quene

def write_configs(key:str,value:str):
    """
    Open config.json, write value to the specified key, and save.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update the key
        config[key] = value
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False

def append_configs(key:str,value):
    """
    Open config.json, append value to the specified key (assumes key is a list), and save.
    Only appends if the value doesn't already exist in the list.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Append to the key (assumes it's a list)
        if key not in config:
            config[key] = []
        
        # Only append if value doesn't already exist
        if value not in config[key]:
            config[key].append(value)
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error appending config: {e}")
        return False

def clear_configs(key:str):
    """
    Open config.json, clear the value of the specified key (set to empty list or empty string), and save.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Clear the key value
        if key in config:
            if isinstance(config[key], list):
                config[key] = []
            elif isinstance(config[key], dict):
                config[key] = {}
            else:
                config[key] = ""
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error clearing config: {e}")
        return False

def _write_formatted_json(config, file):
    """
    Write JSON with custom formatting: inner arrays on single lines, outer structure indented.
    """
    import json
    
    file.write('{\n')
    keys = list(config.keys())
    for i, key in enumerate(keys):
        file.write(f'  "{key}": ')
        value = config[key]
        
        if isinstance(value, list) and value and isinstance(value[0], list):
            # List of lists - each inner list on one line
            file.write('[\n')
            for j, item in enumerate(value):
                file.write(f'    {json.dumps(item, ensure_ascii=False)}')
                if j < len(value) - 1:
                    file.write(',\n')
                else:
                    file.write('\n')
            file.write('  ]')
        else:
            # Regular value
            file.write(json.dumps(value, indent=2, ensure_ascii=False).replace('\n', '\n  '))
        
        if i < len(keys) - 1:
            file.write(',\n')
        else:
            file.write('\n')
    file.write('}\n')