# Requirements Document

## Introduction

This document specifies the requirements for refactoring a multi-IP automation system for SMS relogin processes. The current system uses a single IP configuration with shared data structures (info_pool, info_list, success_list, failure_list). The refactoring will enable the system to manage multiple IPs independently, each with its own data structures, and support parallel or sequential processing across all IPs.

## Glossary

- **System**: The SMS relogin automation system
- **IP_Configuration**: A configuration object containing ip, host_local, host_rpc, and associated data structures for a single IP address
- **Device_Info**: A list containing [phone_number, index, "", ""] representing a device to be processed
- **Info_Pool**: A collection of Device_Info items available for processing
- **Info_List**: A collection of Device_Info items currently being processed in a batch
- **Success_List**: A collection of Device_Info items that successfully completed relogin
- **Failure_List**: A collection of Device_Info items that failed relogin
- **Batch**: A subset of Device_Info items processed together
- **Config_Manager**: Component responsible for reading and writing configuration data
- **Machine_Manager**: Component responsible for starting, stopping, and managing Docker containers
- **Relogin_Processor**: Component responsible for executing the SMS relogin workflow
- **IP_Orchestrator**: Component responsible for coordinating relogin processes across multiple IPs

## Requirements

### Requirement 1: Multi-IP Configuration Structure

**User Story:** As a system administrator, I want the configuration file to support multiple IP addresses with independent data structures, so that I can manage separate device pools for each IP.

#### Acceptance Criteria

1. THE System SHALL store configuration data in a structure where each IP address has its own Info_Pool, Info_List, Success_List, and Failure_List
2. WHEN the configuration file is read, THE System SHALL parse the multi-IP structure into IP_Configuration objects
3. THE System SHALL maintain backward compatibility by providing a migration utility for converting single-IP configurations to multi-IP format
4. WHEN an IP address is not found in the configuration, THE System SHALL return an error indicating the missing IP
5. THE System SHALL validate that each IP_Configuration contains all required fields (ip, host_local, info_pool, info_list, success_list, failure_list)

### Requirement 2: Configuration Management Functions

**User Story:** As a developer, I want configuration management functions to work with IP-specific data, so that operations on one IP do not affect other IPs.

#### Acceptance Criteria

1. WHEN writing configuration data, THE Config_Manager SHALL accept an IP address parameter to identify which IP_Configuration to modify
2. WHEN appending to a list (info_list, success_list, failure_list), THE Config_Manager SHALL append only to the specified IP's list
3. WHEN clearing a list, THE Config_Manager SHALL clear only the specified IP's list
4. THE Config_Manager SHALL preserve data for all other IPs when modifying one IP's configuration
5. WHEN reading configuration data, THE Config_Manager SHALL return the complete multi-IP structure

### Requirement 3: Function Parameter Refactoring

**User Story:** As a developer, I want functions to accept explicit parameters instead of config dictionaries, so that function signatures are clear and type-safe.

#### Acceptance Criteria

1. THE Machine_Manager SHALL accept explicit parameters (ip, name, host_local) instead of a config dictionary
2. THE Relogin_Processor SHALL accept explicit parameters (ip, host_local, device_info_list) instead of a config dictionary
3. WHEN a function requires IP-specific configuration, THE System SHALL pass only the relevant IP_Configuration object
4. THE System SHALL eliminate all functions that accept the entire config dictionary as a parameter
5. WHEN calling refactored functions, THE System SHALL extract required parameters from IP_Configuration objects

### Requirement 4: Batch Processing Per IP

**User Story:** As a system operator, I want each IP to process its own batches independently, so that device management is isolated per IP.

#### Acceptance Criteria

1. WHEN creating batches, THE System SHALL create batches only from the specified IP's Info_Pool
2. WHEN processing a batch, THE System SHALL use only the specified IP's configuration and device list
3. WHEN updating success or failure lists, THE System SHALL update only the specified IP's lists
4. THE System SHALL ensure that Device_Info items from one IP are never mixed with another IP's devices
5. WHEN a batch completes, THE System SHALL update the specified IP's Info_List to reflect processed devices

### Requirement 5: Multi-IP Orchestration

**User Story:** As a system operator, I want to process multiple IPs either sequentially or in parallel, so that I can optimize throughput based on system resources.

#### Acceptance Criteria

1. THE IP_Orchestrator SHALL provide a sequential processing mode that processes one IP at a time
2. THE IP_Orchestrator SHALL provide a parallel processing mode that processes multiple IPs concurrently
3. WHEN processing in parallel mode, THE IP_Orchestrator SHALL limit concurrency to a configurable maximum number of IPs
4. WHEN an IP's processing fails, THE IP_Orchestrator SHALL continue processing other IPs without interruption
5. WHEN all IPs complete processing, THE IP_Orchestrator SHALL return a summary of results for each IP

### Requirement 6: Machine Management Isolation

**User Story:** As a system operator, I want machine start/stop operations to be isolated per IP, so that operations on one IP do not affect machines on other IPs.

#### Acceptance Criteria

1. WHEN stopping machines, THE Machine_Manager SHALL stop only machines associated with the specified IP
2. WHEN starting machines, THE Machine_Manager SHALL start only machines associated with the specified IP
3. WHEN retrieving machine names, THE Machine_Manager SHALL filter results to only include machines for the specified IP
4. THE Machine_Manager SHALL construct machine names using the format "T100{index}-{phone_number}"
5. WHEN deleting machines, THE Machine_Manager SHALL delete only machines associated with the specified IP

### Requirement 7: Error Handling and Logging

**User Story:** As a system operator, I want clear error messages and logs that identify which IP encountered issues, so that I can troubleshoot problems efficiently.

#### Acceptance Criteria

1. WHEN an error occurs during processing, THE System SHALL log the error with the associated IP address
2. WHEN a device fails relogin, THE System SHALL append the Device_Info to the correct IP's Failure_List
3. WHEN a device succeeds relogin, THE System SHALL append the Device_Info to the correct IP's Success_List
4. THE System SHALL log the start and completion of processing for each IP
5. WHEN processing completes, THE System SHALL output a summary showing success and failure counts per IP

### Requirement 8: Configuration File Format

**User Story:** As a system administrator, I want a clear and maintainable configuration file format, so that I can easily add or modify IP configurations.

#### Acceptance Criteria

1. THE System SHALL use a JSON configuration file with a top-level "ips" object containing IP addresses as keys
2. WHEN formatting the configuration file, THE System SHALL maintain readable indentation and structure
3. THE System SHALL preserve global configuration fields (domain, image, redis_url, update_account_url, ip_dict) at the root level
4. WHEN writing the configuration file, THE System SHALL format nested arrays (Device_Info lists) on single lines for readability
5. THE System SHALL validate the configuration file structure on load and report specific validation errors

### Requirement 9: Migration Utility

**User Story:** As a system administrator, I want a migration utility to convert my existing single-IP configuration to the new multi-IP format, so that I can upgrade without manual data entry.

#### Acceptance Criteria

1. THE System SHALL provide a migration function that converts single-IP config.json to multi-IP format
2. WHEN migrating, THE System SHALL extract the current "ip" field and create an IP_Configuration entry for it
3. WHEN migrating, THE System SHALL move info_pool, info_list, success_list, and failure_list under the IP's configuration
4. THE System SHALL preserve all global configuration fields during migration
5. WHEN migration completes, THE System SHALL create a backup of the original configuration file

### Requirement 10: Relogin Process Integration

**User Story:** As a developer, I want the relogin process to work seamlessly with IP-specific configurations, so that SMS relogin continues to function correctly after refactoring.

#### Acceptance Criteria

1. WHEN processing relogin for a device, THE Relogin_Processor SHALL use the correct IP address for API calls
2. WHEN checking login state, THE System SHALL use the device's associated IP configuration
3. WHEN updating account lists on the server, THE System SHALL send the correct IP address in the request
4. THE System SHALL maintain the existing relogin workflow (stop batch, start batch, relogin, update state, check state)
5. WHEN relogin completes for an IP, THE System SHALL update only that IP's success and failure lists


### Requirement 11: Auto infoPool fillin

***User Story:** As a autolization developer, I need fill in infoPool auto based on the ip spec 

#### Acceptance Criteria
1.when a IP's task begin ,the program should first request its info ,then the config would be complete 

2. the function have write in account_requests.py , just call it 