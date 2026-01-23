# Implementation Plan: Multi-IP Automation Refactor

## Overview

This implementation plan refactors the SMS relogin automation system from single-IP to multi-IP architecture. The refactoring will be done incrementally, starting with configuration management, then machine management, followed by relogin processing, and finally the orchestration layer. Each step builds on the previous one and includes testing to validate correctness.

## Tasks

- [x] 1. Refactor configuration management for multi-IP support
  - [x] 1.1 Create new configuration structure and utilities
    - Implement `load_config()` to return multi-IP structure with "global" and "ips" sections
    - Implement `get_ip_config(ip: str)` to retrieve IP-specific configuration
    - Implement `get_all_ips()` to return list of configured IPs
    - _Requirements: 1.1, 1.2, 2.5_
  
  - [ ]* 1.2 Write property test for configuration structure integrity
    - **Property 1: Configuration Structure Integrity**
    - **Validates: Requirements 1.1, 1.5**
  
  - [ ]* 1.3 Write property test for configuration round-trip consistency
    - **Property 2: Configuration Round-Trip Consistency**
    - **Validates: Requirements 1.2**
  
  - [x] 1.4 Implement IP-specific write operations
    - Implement `write_ip_config(ip: str, key: str, value: any)` to write to specific IP
    - Implement `append_ip_config(ip: str, key: str, value: any)` to append to IP's list
    - Implement `clear_ip_config(ip: str, key: str)` to clear IP's list
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ]* 1.5 Write property test for configuration isolation
    - **Property 3: Configuration Isolation**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
  
  - [x] 1.6 Implement error handling for missing IPs
    - Add `IPNotFoundError` exception class
    - Update `get_ip_config()` to raise error for missing IPs
    - _Requirements: 1.4_
  
  - [ ]* 1.7 Write property test for missing IP error handling
    - **Property 4: Missing IP Error Handling**
    - **Validates: Requirements 1.4**

- [x] 2. Implement configuration migration utility
  - [x] 2.1 Create migration function
    - Implement `migrate_config()` to convert single-IP to multi-IP format
    - Extract current "ip" field and create IP entry under "ips"
    - Move info_pool, info_list, success_list, failure_list under IP's config
    - Preserve global fields (domain, image, redis_url, etc.)
    - Create backup of original config.json
    - _Requirements: 1.3, 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 2.2 Write property test for migration correctness
    - **Property 15: Configuration Migration Correctness**
    - **Validates: Requirements 1.3, 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [x] 2.3 Write unit tests for migration edge cases
    - Test migration with empty lists
    - Test migration with missing optional fields
    - Test backup file creation
    - _Requirements: 9.5_

- [x] 3. Checkpoint - Ensure configuration tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 4. Refactor machine management functions
  - [x] 4.1 Update stop_machine.py with explicit parameters
    - Refactor `stop_docker(ip, host_local, index, phone)` to use explicit params
    - Refactor `stop_batch(ip, host_local, device_info_list)` to use explicit params
    - Refactor `get_machine_namelist(ip, host_local)` to use explicit params
    - Refactor `stop_machines_all(ip, host_local, names)` to use explicit params
    - _Requirements: 3.1, 6.1_
  
  - [x] 4.2 Update start_machine.py with explicit parameters
    - Refactor `start_docker(ip, host_local, index, phone)` to use explicit params
    - Refactor `start_batch(ip, host_local, device_info_list)` to use explicit params
    - _Requirements: 3.1, 6.2_
  
  - [x] 4.3 Update delete_machine.py with explicit parameters
    - Refactor `delete_docker(ip, host_local, index, phone)` to use explicit params
    - _Requirements: 3.1, 6.5_
  
  - [x] 4.4 Write property test for machine name format
    - **Property 7: Machine Name Format Consistency**
    - **Validates: Requirements 6.4**
  
  - [ ] 4.5 Write property test for machine operation isolation
    - **Property 8: Machine Operation Isolation**
    - **Validates: Requirements 6.1, 6.2, 6.5**
  
  - [ ] 4.6 Write property test for machine name filtering
    - **Property 9: Machine Name Filtering**
    - **Validates: Requirements 6.3**

- [x] 5. Refactor relogin processor functions
  - [x] 5.1 Update SmsRelogin.py with explicit parameters
    - Refactor `relogin_process(ip, host_local, device_info)` to use explicit params
    - Update AutoPhone instantiation to use passed ip and host_local
    - Refactor `check_loginstate_batch(ip, host_local, device_info_list)` to use explicit params
    - _Requirements: 3.2, 10.1, 10.2_
  
  - [ ]* 5.2 Write property test for IP configuration usage
    - **Property 16: IP Configuration Usage in Operations**
    - **Validates: Requirements 10.1, 10.2, 10.3**

- [x] 6. Refactor account management functions
  - [x] 6.1 Update prologin_initial.py with explicit parameters
    - Refactor `batch_changeLogin_state(ip, host_local, device_info_list)` to use explicit params
    - _Requirements: 3.2_
  
  - [x] 6.2 Update test_account.py with explicit parameters
    - Refactor `update_accountlist(ip, host_rpc, device_info_list, update_account_url)` to use explicit params
    - _Requirements: 3.2, 10.3_
  
  - [ ]* 6.3 Write property test for device list updates
    - **Property 10: Device List Updates**
    - **Validates: Requirements 7.2, 7.3, 10.5**

- [ ] 7. Checkpoint - Ensure refactored functions work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create IP processor module
  - [x] 8.1 Create AutoTasks/ip_processor.py
    - Implement `process_single_batch(ip, ip_config, global_config, batch)` function
    - Write batch to IP's info_list using `write_ip_config()`
    - Call refactored stop_batch() and start_batch() with explicit params
    - Execute relogin with ProcessPoolExecutor using refactored relogin_process()
    - Call refactored batch_changeLogin_state() with explicit params
    - Call refactored update_accountlist() with explicit params
    - Append failures to IP's failure_list using `append_ip_config()`
    - Call refactored check_loginstate_batch() with explicit params
    - Return batch results dict with success/failure counts
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 10.4_
  
  - [x] 8.2 Implement process_ip_batches function
    - Load IP-specific data from ip_config
    - Create batches using group_pools() and batch_slice()
    - Stop all machines for the IP using refactored functions
    - Process each batch using process_single_batch()
    - Aggregate results across all batches
    - Return IP processing results dict
    - _Requirements: 4.1, 4.5, 10.5_
  
  - [ ]* 8.3 Write property test for batch creation from IP pool
    - **Property 5: Batch Creation from IP Pool**
    - **Validates: Requirements 4.1, 4.4**
  
  - [ ]* 8.4 Write property test for batch processing isolation
    - **Property 6: Batch Processing Isolation**
    - **Validates: Requirements 4.2, 4.3, 4.5**
  
  - [ ]* 8.5 Write property test for relogin workflow sequence
    - **Property 17: Relogin Workflow Sequence**
    - **Validates: Requirements 10.4**

- [-] 9. Create IP orchestrator module
  - [x] 9.1 Create AutoTasks/ip_orchestrator.py
    - Implement `process_sequential(ips, config, global_config)` function
    - Iterate through IPs one at a time
    - Call process_ip_batches() for each IP
    - Collect and aggregate results
    - Handle errors gracefully and continue with other IPs
    - Return orchestrator results dict
    - _Requirements: 5.1, 5.4, 5.5_
  
  - [x] 9.2 Implement parallel processing function
    - Implement `process_parallel(ips, config, global_config, max_parallel)` function
    - Use ProcessPoolExecutor with max_workers=max_parallel
    - Submit all IP processing tasks
    - Collect results as they complete using as_completed()
    - Handle errors gracefully for each IP
    - Return orchestrator results dict
    - _Requirements: 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 9.3 Implement main orchestrator function
    - Implement `process_all_ips(mode, max_parallel)` function
    - Load config and extract global config and IPs
    - Route to process_sequential() or process_parallel() based on mode
    - Validate mode parameter and raise ValueError for invalid modes
    - _Requirements: 5.1, 5.2_
  
  - [ ]* 9.4 Write property test for sequential processing order
    - **Property 12: Sequential Processing Order**
    - **Validates: Requirements 5.1**
  
  - [ ]* 9.5 Write property test for parallel concurrency limit
    - **Property 13: Parallel Processing Concurrency Limit**
    - **Validates: Requirements 5.3**
  
  - [ ]* 9.6 Write property test for error isolation
    - **Property 14: Error Isolation in Orchestrator**
    - **Validates: Requirements 5.4**
  
  - [ ]* 9.7 Write property test for result completeness
    - **Property 11: Orchestrator Result Completeness**
    - **Validates: Requirements 5.5, 7.5**

- [x] 10. Update main entry point
  - [x] 10.1 Refactor AutoTasks/auto_SmsRelogin.py
    - Remove old process_batch_relogin() function
    - Update main block to use new ip_orchestrator
    - Add command-line arguments for mode selection (sequential/parallel)
    - Add command-line argument for max_parallel setting
    - Call process_all_ips() with selected mode
    - Print summary of results for all IPs
    - _Requirements: 5.1, 5.2, 7.4, 7.5_
  
  - [ ]* 10.2 Write unit tests for main entry point
    - Test command-line argument parsing
    - Test sequential mode invocation
    - Test parallel mode invocation
    - _Requirements: 5.1, 5.2_

- [x] 11. Add configuration validation
  - [x] 11.1 Implement configuration validation function
    - Create `validate_config(config)` function
    - Check for required "global" and "ips" sections
    - Validate each IP configuration has required fields
    - Raise ConfigValidationError with specific error messages
    - _Requirements: 1.5, 8.5_
  
  - [x] 11.2 Integrate validation into load_config
    - Call validate_config() after loading JSON
    - Handle validation errors and provide clear messages
    - _Requirements: 8.5_
  
  - [ ]* 11.3 Write property test for configuration validation
    - **Property 18: Configuration Validation**
    - **Validates: Requirements 8.5**
  
  - [ ]* 11.4 Write property test for global configuration preservation
    - **Property 19: Global Configuration Preservation**
    - **Validates: Requirements 8.3**
  
  - [ ]* 11.5 Write property test for multi-IP structure
    - **Property 20: Multi-IP Configuration Structure**
    - **Validates: Requirements 8.1**

- [-] 12. Final checkpoint - Integration testing
  - [-]* 12.1 Write integration test for single IP processing
    - Test complete processing of one IP from start to finish
    - Verify all steps execute in correct order
    - _Requirements: 10.4_
  
  - [-]* 12.2 Write integration test for multi-IP sequential processing
    - Test sequential processing of 2-3 IPs
    - Verify IPs are processed one at a time
    - _Requirements: 5.1_
  
  - [-]* 12.3 Write integration test for multi-IP parallel processing
    - Test parallel processing of 2-3 IPs
    - Verify concurrency limits are respected
    - _Requirements: 5.2, 5.3_
  
  - [ ]* 12.4 Write integration test for migration workflow
    - Test migrating a single-IP config
    - Test processing the migrated config
    - Verify backup file creation
    - _Requirements: 1.3, 9.5_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end workflows
- Use `hypothesis` library for property-based testing in Python
- Tag each property test with: `# Feature: multi-ip-automation-refactor, Property {N}: {property_text}`
