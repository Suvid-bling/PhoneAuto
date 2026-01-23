# Design Document: Multi-IP Automation Refactor

## Overview

This design refactors the SMS relogin automation system from a single-IP architecture to a multi-IP architecture. The refactoring introduces IP-specific configurations, explicit function parameters, and an orchestration layer for managing multiple IPs concurrently or sequentially.

The key architectural changes include:
1. Restructuring config.json to support multiple IP configurations
2. Refactoring functions to use explicit parameters instead of config dictionaries
3. Creating an IP orchestration layer for multi-IP processing
4. Isolating machine management and relogin operations per IP

## Architecture

### Current Architecture

```
config.json (single IP)
    ├── ip: "192.168.124.17"
    ├── host_local: "..."
    ├── info_pool: [...]
    ├── info_list: [...]
    ├── success_list: [...]
    └── failure_list: [...]

auto_SmsRelogin.py
    └── process_batch_relogin(batch)
        ├── Uses global config
        └── Processes single IP
```

### New Architecture

```
config.json (multi-IP)
    ├── global_config
    │   ├── domain
    │   ├── image
    │   ├── redis_url
    │   └── ip_dict
    └── ips
        ├── "192.168.124.17"
        │   ├── host_local
        │   ├── host_rpc
        │   ├── info_pool: [...]
        │   ├── info_list: [...]
        │   ├── success_list: [...]
        │   └── failure_list: [...]
        └── "192.168.124.18"
            └── ...

IP Orchestrator
    └── process_all_ips(mode: sequential|parallel)
        └── For each IP:
            └── IP Processor
                └── process_ip_batches(ip_config)
```


## Components and Interfaces

### 1. Configuration Manager (setting.py)

**Purpose:** Manage reading and writing of IP-specific configuration data.

**Refactored Functions:**

```python
def load_config() -> dict:
    """Load the complete multi-IP configuration"""
    # Returns: {
    #   "global": {...},
    #   "ips": {
    #     "192.168.124.17": {...},
    #     ...
    #   }
    # }

def get_ip_config(ip: str) -> dict:
    """Get configuration for a specific IP"""
    # Returns: {
    #   "ip": "192.168.124.17",
    #   "host_local": "...",
    #   "host_rpc": "...",
    #   "info_pool": [...],
    #   "info_list": [...],
    #   "success_list": [...],
    #   "failure_list": [...]
    # }

def write_ip_config(ip: str, key: str, value: any) -> bool:
    """Write value to a specific key for a specific IP"""

def append_ip_config(ip: str, key: str, value: any) -> bool:
    """Append value to a list key for a specific IP"""

def clear_ip_config(ip: str, key: str) -> bool:
    """Clear a key's value for a specific IP"""

def get_all_ips() -> list[str]:
    """Get list of all configured IP addresses"""

def migrate_config() -> bool:
    """Migrate single-IP config to multi-IP format"""
```

### 2. Machine Manager (MachineManage/)

**Purpose:** Manage Docker container lifecycle for devices.

**Refactored Functions:**

```python
def stop_docker(ip: str, host_local: str, index: int, phone: str) -> bool:
    """Stop a specific Docker container"""
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/stop/{ip}/{name}"

def start_docker(ip: str, host_local: str, index: int, phone: str) -> bool:
    """Start a specific Docker container"""
    name = f"T100{index}-{phone}"
    url = f"http://{host_local}/dc_api/v1/run/{ip}/{name}"

def delete_docker(ip: str, host_local: str, index: int, phone: str) -> bool:
    """Delete a specific Docker container"""

def get_machine_namelist(ip: str, host_local: str) -> list[str]:
    """Get list of machine names for a specific IP"""

def stop_machines_all(ip: str, host_local: str, names: list[str]) -> None:
    """Stop all machines in the name list for a specific IP"""

def stop_batch(ip: str, host_local: str, device_info_list: list) -> None:
    """Stop all machines in a batch"""
    for device_info in device_info_list:
        phone, index = device_info[0], device_info[1]
        stop_docker(ip, host_local, index, phone)

def start_batch(ip: str, host_local: str, device_info_list: list) -> None:
    """Start all machines in a batch"""
```


### 3. Relogin Processor (SMSLogin/SmsRelogin.py)

**Purpose:** Execute SMS relogin workflow for devices.

**Refactored Functions:**

```python
def relogin_process(ip: str, host_local: str, device_info: list) -> bool:
    """Process login for a single device with explicit IP"""
    phone_number, index = device_info[0], device_info[1]
    phone = AutoPhone(
        ip=ip,
        port=f"500{index}",
        host=host_local,
        name=f"T100{index}-{phone_number}",
        auto_connect=False
    )
    # ... rest of relogin logic

def check_loginstate_batch(ip: str, host_local: str, device_info_list: list) -> dict:
    """Check login state for all devices in the list"""
    # Returns: {phone_number: is_logged_in, ...}
```

### 4. Account Manager (AccountManage/)

**Purpose:** Manage account state and server updates.

**Refactored Functions:**

```python
def batch_changeLogin_state(ip: str, host_local: str, device_info_list: list) -> None:
    """Update login state for all devices in the batch"""
    for phone, index, _, _ in device_info_list:
        device_name = f"T100{index}-{phone}"
        change_login_state([device_name])

def update_accountlist(ip: str, host_rpc: str, device_info_list: list, 
                       update_account_url: str) -> list:
    """Update account list on server and return failed devices"""
    data = {
        "host": host_rpc,
        "ip": ip
    }
    # ... rest of update logic
    # Returns: list of Device_Info that failed
```

### 5. IP Processor (AutoTasks/ip_processor.py - NEW)

**Purpose:** Process all batches for a single IP.

```python
def process_ip_batches(ip: str, ip_config: dict, global_config: dict) -> dict:
    """
    Process all batches for a single IP.
    
    Args:
        ip: IP address to process
        ip_config: Configuration specific to this IP
        global_config: Global configuration (domain, redis_url, etc.)
    
    Returns:
        {
            "ip": ip,
            "success_count": int,
            "failure_count": int,
            "processed_batches": int,
            "failures": [Device_Info, ...]
        }
    """
    # 1. Load IP-specific data
    info_pool = ip_config["info_pool"]
    host_local = ip_config["host_local"]
    host_rpc = ip_config["host_rpc"]
    
    # 2. Create batches from info_pool
    groups = group_pools(info_pool)
    batch_queue = batch_slice(groups)
    
    # 3. Stop all machines for this IP
    names = get_machine_namelist(ip, host_local)
    stop_machines_all(ip, host_local, names)
    time.sleep(20)
    
    # 4. Process each batch
    results = {
        "ip": ip,
        "success_count": 0,
        "failure_count": 0,
        "processed_batches": 0,
        "failures": []
    }
    
    for batch in batch_queue:
        batch_result = process_single_batch(ip, ip_config, global_config, batch)
        results["processed_batches"] += 1
        results["success_count"] += batch_result["success_count"]
        results["failure_count"] += batch_result["failure_count"]
        results["failures"].extend(batch_result["failures"])
    
    return results

def process_single_batch(ip: str, ip_config: dict, global_config: dict, 
                        batch: list) -> dict:
    """Process a single batch of devices for an IP"""
    # 1. Write batch to IP's info_list
    write_ip_config(ip, "info_list", batch)
    
    # 2. Stop and start machines
    stop_batch(ip, ip_config["host_local"], batch)
    start_batch(ip, ip_config["host_local"], batch)
    time.sleep(30)
    
    # 3. Execute relogin with multiprocessing
    with ProcessPoolExecutor(max_workers=2) as executor:
        relogin_func = partial(relogin_process, ip, ip_config["host_local"])
        executor.map(relogin_func, batch)
    
    # 4. Update login state
    batch_changeLogin_state(ip, ip_config["host_local"], batch)
    
    # 5. Update account list on server
    update_accountlist(ip, ip_config["host_rpc"], batch, 
                      global_config["update_account_url"])
    time.sleep(120)
    
    # 6. Get failures and update failure list
    failure_devices = update_accountlist(ip, ip_config["host_rpc"], batch,
                                        global_config["update_account_url"])
    for device in failure_devices:
        append_ip_config(ip, "failure_list", device)
    
    # 7. Check login state
    check_loginstate_batch(ip, ip_config["host_local"], batch)
    
    # 8. Stop batch machines
    stop_batch(ip, ip_config["host_local"], batch)
    
    return {
        "success_count": len(batch) - len(failure_devices),
        "failure_count": len(failure_devices),
        "failures": failure_devices
    }
```


### 6. IP Orchestrator (AutoTasks/ip_orchestrator.py - NEW)

**Purpose:** Coordinate processing across multiple IPs.

```python
def process_all_ips(mode: str = "sequential", max_parallel: int = 3) -> dict:
    """
    Process all configured IPs either sequentially or in parallel.
    
    Args:
        mode: "sequential" or "parallel"
        max_parallel: Maximum number of IPs to process concurrently (parallel mode only)
    
    Returns:
        {
            "total_ips": int,
            "completed_ips": int,
            "failed_ips": int,
            "results": {
                "192.168.124.17": {...},
                "192.168.124.18": {...},
                ...
            }
        }
    """
    config = load_config()
    global_config = config["global"]
    ips = get_all_ips()
    
    if mode == "sequential":
        return process_sequential(ips, config, global_config)
    elif mode == "parallel":
        return process_parallel(ips, config, global_config, max_parallel)
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'sequential' or 'parallel'")

def process_sequential(ips: list[str], config: dict, global_config: dict) -> dict:
    """Process IPs one at a time"""
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

def process_parallel(ips: list[str], config: dict, global_config: dict, 
                    max_parallel: int) -> dict:
    """Process multiple IPs concurrently"""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    
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
```

## Data Models

### Configuration Structure

**Multi-IP Configuration (config.json):**

```json
{
  "global": {
    "domain": "http://192.168.124.5:8002",
    "image": "registry.cn-guangzhou.aliyuncs.com/mytos/dobox:Q12_base_202510101731",
    "redis_url": "redis://zjl:hZohdCUneLEo@192.168.223.202:6386/2",
    "update_account_url": "http://192.168.223.144:9000/android/updateAccountHeaders/",
    "ip_dict": {
      "192.168.124.15": "3-3001-192_168_124_18",
      "192.168.124.17": "3-3001-192_168_124_17",
      "192.168.124.18": "2-3001-192_168_124_18"
    }
  },
  "ips": {
    "192.168.124.17": {
      "host_local": "192.168.124.5:5000",
      "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
      "info_pool": [
        ["2364180493", "2", "", ""],
        ["2364180320", "1", "", ""]
      ],
      "info_list": [],
      "success_list": [],
      "failure_list": []
    },
    "192.168.124.18": {
      "host_local": "192.168.124.5:5000",
      "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
      "info_pool": [
        ["4376662009", "7", "", ""],
        ["4508371395", "1", "", ""]
      ],
      "info_list": [],
      "success_list": [],
      "failure_list": []
    }
  }
}
```

**Device Info Structure:**

```python
Device_Info = [phone_number: str, index: str, "", ""]
# Example: ["6727221187", "6", "", ""]
```

**IP Configuration Object:**

```python
{
    "ip": "192.168.124.17",
    "host_local": "192.168.124.5:5000",
    "host_rpc": "36.133.80.179:7152/3001-MYTSDK",
    "info_pool": [Device_Info, ...],
    "info_list": [Device_Info, ...],
    "success_list": [Device_Info, ...],
    "failure_list": [Device_Info, ...]
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Configuration Structure Integrity

*For any* valid multi-IP configuration, each IP address SHALL have its own independent Info_Pool, Info_List, Success_List, and Failure_List, and all required fields (ip, host_local, info_pool, info_list, success_list, failure_list) SHALL be present.

**Validates: Requirements 1.1, 1.5**

### Property 2: Configuration Round-Trip Consistency

*For any* valid multi-IP configuration, serializing it to JSON and then parsing it back SHALL produce an equivalent configuration with the same structure and data.

**Validates: Requirements 1.2**

### Property 3: Configuration Isolation

*For any* IP address and any configuration operation (write, append, clear), modifying one IP's configuration SHALL NOT affect any other IP's configuration data.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 4: Missing IP Error Handling

*For any* IP address that does not exist in the configuration, attempting to retrieve its configuration SHALL return an error indicating the missing IP.

**Validates: Requirements 1.4**

### Property 5: Batch Creation from IP Pool

*For any* IP address, all Device_Info items in batches created from that IP's Info_Pool SHALL originate from that IP's Info_Pool and SHALL NOT contain devices from other IPs.

**Validates: Requirements 4.1, 4.4**

### Property 6: Batch Processing Isolation

*For any* IP address and batch, processing the batch SHALL only access and modify that IP's configuration data, and SHALL NOT affect other IPs' Info_Lists, Success_Lists, or Failure_Lists.

**Validates: Requirements 4.2, 4.3, 4.5**

### Property 7: Machine Name Format Consistency

*For any* Device_Info with phone_number and index, the constructed machine name SHALL match the format "T100{index}-{phone_number}".

**Validates: Requirements 6.4**

### Property 8: Machine Operation Isolation

*For any* IP address, machine operations (start, stop, delete) SHALL only affect machines associated with that IP and SHALL NOT affect machines associated with other IPs.

**Validates: Requirements 6.1, 6.2, 6.5**

### Property 9: Machine Name Filtering

*For any* IP address, retrieving machine names SHALL return only machines whose names correspond to devices in that IP's configuration.

**Validates: Requirements 6.3**

### Property 10: Device List Updates

*For any* IP address and Device_Info, when a device succeeds or fails relogin, it SHALL be appended to the correct IP's Success_List or Failure_List respectively, and SHALL NOT appear in other IPs' lists.

**Validates: Requirements 7.2, 7.3, 10.5**

### Property 11: Orchestrator Result Completeness

*For any* set of IP addresses, when the IP_Orchestrator completes processing (sequential or parallel), the results SHALL contain an entry for each IP that was processed, including success counts, failure counts, and processed batch counts.

**Validates: Requirements 5.5, 7.5**

### Property 12: Sequential Processing Order

*For any* set of IP addresses in sequential mode, IPs SHALL be processed one at a time without overlap, and each IP SHALL complete before the next begins.

**Validates: Requirements 5.1**

### Property 13: Parallel Processing Concurrency Limit

*For any* set of IP addresses in parallel mode with max_parallel limit, no more than max_parallel IPs SHALL be processed concurrently at any given time.

**Validates: Requirements 5.3**

### Property 14: Error Isolation in Orchestrator

*For any* set of IP addresses, if one IP's processing fails, all other IPs SHALL continue processing and complete successfully (assuming no errors in those IPs).

**Validates: Requirements 5.4**

### Property 15: Configuration Migration Correctness

*For any* valid single-IP configuration, migrating it to multi-IP format SHALL produce a valid multi-IP configuration where: (1) the original IP field becomes a key in the ips object, (2) info_pool, info_list, success_list, and failure_list are moved under that IP's configuration, (3) all global fields are preserved, and (4) a backup file is created.

**Validates: Requirements 1.3, 9.1, 9.2, 9.3, 9.4, 9.5**

### Property 16: IP Configuration Usage in Operations

*For any* device relogin operation, the IP address used in API calls, login state checks, and account list updates SHALL match the device's associated IP configuration.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 17: Relogin Workflow Sequence

*For any* batch of devices, the relogin workflow SHALL execute steps in the correct order: stop batch, start batch, execute relogin, update login state, update account list, check login state, stop batch.

**Validates: Requirements 10.4**

### Property 18: Configuration Validation

*For any* configuration file, loading it SHALL succeed if it has valid structure (global section and ips section with valid IP configurations), and SHALL fail with a specific error message if the structure is invalid.

**Validates: Requirements 8.5**

### Property 19: Global Configuration Preservation

*For any* configuration operation, the global configuration fields (domain, image, redis_url, update_account_url, ip_dict) SHALL remain unchanged and accessible at the root level.

**Validates: Requirements 8.3**

### Property 20: Multi-IP Configuration Structure

*For any* valid configuration, it SHALL have a top-level "ips" object where keys are IP addresses and values are IP_Configuration objects.

**Validates: Requirements 8.1**


## Error Handling

### Configuration Errors

1. **Missing IP Error**: When an IP address is not found in the configuration, raise `IPNotFoundError` with message: "IP address {ip} not found in configuration"

2. **Invalid Configuration Structure**: When loading a configuration file with invalid structure, raise `ConfigValidationError` with specific details about what's missing or malformed

3. **Migration Errors**: When migrating a configuration fails (e.g., backup creation fails), raise `MigrationError` with details about the failure

### Processing Errors

1. **Batch Processing Failure**: When a batch fails to process, log the error with IP and batch details, append failed devices to the IP's failure_list, and continue with next batch

2. **Device Relogin Failure**: When a device fails relogin, catch the exception, log it with device and IP details, append to failure_list, and continue with other devices

3. **Machine Operation Failure**: When machine start/stop/delete fails, log the error with machine name and IP, but continue processing other machines

### Orchestrator Errors

1. **IP Processing Failure**: When an IP's processing fails in the orchestrator, log the error, record it in results with error details, and continue processing other IPs

2. **Invalid Mode Error**: When an invalid processing mode is specified, raise `ValueError` with message: "Invalid mode: {mode}. Must be 'sequential' or 'parallel'"

### Error Recovery

1. **Retry Logic**: Device relogin includes retry logic for SMS code retrieval (up to 2 retries)

2. **Failure Tracking**: All failures are tracked in IP-specific failure_lists for later retry or investigation

3. **Graceful Degradation**: System continues processing even when individual devices or IPs fail

## Testing Strategy

### Unit Testing

Unit tests will focus on specific examples, edge cases, and error conditions:

1. **Configuration Management**:
   - Test loading valid and invalid configuration files
   - Test migration from single-IP to multi-IP format
   - Test write/append/clear operations on specific IPs
   - Test error handling for missing IPs

2. **Machine Management**:
   - Test machine name construction with various phone numbers and indices
   - Test API call construction for start/stop/delete operations
   - Test error handling for failed API calls

3. **Batch Processing**:
   - Test batch creation from info_pool
   - Test batch slicing algorithm
   - Test empty batch handling

4. **Orchestrator**:
   - Test sequential processing with 2-3 IPs
   - Test parallel processing with concurrency limits
   - Test error handling when one IP fails

### Property-Based Testing

Property tests will verify universal properties across all inputs. Each test will run a minimum of 100 iterations.

**Testing Library**: Use `hypothesis` for Python property-based testing.

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `# Feature: multi-ip-automation-refactor, Property {N}: {property_text}`

**Property Test Coverage**:

1. **Property 1-4**: Configuration structure and isolation
   - Generate random multi-IP configurations
   - Test structure integrity, round-trip consistency, isolation, and error handling

2. **Property 5-6**: Batch processing
   - Generate random IP configurations with device pools
   - Test batch creation and processing isolation

3. **Property 7-9**: Machine management
   - Generate random device info
   - Test name formatting, operation isolation, and filtering

4. **Property 10**: Device list updates
   - Generate random devices and success/failure outcomes
   - Test correct list updates per IP

5. **Property 11-14**: Orchestrator behavior
   - Generate random sets of IPs
   - Test result completeness, sequential order, concurrency limits, error isolation

6. **Property 15**: Migration
   - Generate random single-IP configurations
   - Test migration correctness

7. **Property 16-17**: Relogin operations
   - Generate random device batches
   - Test IP usage and workflow sequence

8. **Property 18-20**: Configuration validation
   - Generate valid and invalid configurations
   - Test validation, preservation, and structure

**Generator Strategies**:

```python
from hypothesis import strategies as st

# Device Info: [phone_number, index, "", ""]
device_info = st.tuples(
    st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))),  # phone
    st.integers(min_value=1, max_value=9).map(str),  # index
    st.just(""),
    st.just("")
).map(list)

# IP Configuration
ip_config = st.fixed_dictionaries({
    'host_local': st.text(min_size=5),
    'host_rpc': st.text(min_size=5),
    'info_pool': st.lists(device_info, min_size=0, max_size=20),
    'info_list': st.lists(device_info, min_size=0, max_size=10),
    'success_list': st.lists(device_info, min_size=0, max_size=10),
    'failure_list': st.lists(device_info, min_size=0, max_size=10)
})

# Multi-IP Configuration
multi_ip_config = st.fixed_dictionaries({
    'global': st.fixed_dictionaries({
        'domain': st.text(min_size=5),
        'image': st.text(min_size=5),
        'redis_url': st.text(min_size=5),
        'update_account_url': st.text(min_size=5),
        'ip_dict': st.dictionaries(st.ip_addresses(v=4).map(str), st.text(min_size=5))
    }),
    'ips': st.dictionaries(
        st.ip_addresses(v=4).map(str),
        ip_config,
        min_size=1,
        max_size=5
    )
})
```

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Full IP Processing**: Test complete processing of one IP from start to finish
2. **Multi-IP Sequential**: Test sequential processing of 2-3 IPs
3. **Multi-IP Parallel**: Test parallel processing of 2-3 IPs
4. **Migration Integration**: Test migrating a real single-IP config and processing it

### Test Execution

- Unit tests: Run with `pytest tests/unit/`
- Property tests: Run with `pytest tests/property/ --hypothesis-seed=random`
- Integration tests: Run with `pytest tests/integration/`
- All tests: Run with `pytest tests/`

