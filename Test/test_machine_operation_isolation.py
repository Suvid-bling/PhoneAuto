"""
Property-based test for machine operation isolation.

Feature: multi-ip-automation-refactor, Property 8: Machine Operation Isolation

This test validates that for any IP address, machine operations (start, stop, delete)
only affect machines associated with that IP and do not affect machines associated
with other IPs.

Validates: Requirements 6.1, 6.2, 6.5
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, call
from MachineManage.stop_machine import stop_docker, stop_batch, stop_machines_all
from MachineManage.start_machine import start_docker, start_batch
from MachineManage.delete_machine import delete_docker


# Generator for valid IP addresses (simplified for testing)
ip_strategy = st.sampled_from([
    "192.168.124.17",
    "192.168.124.18",
    "192.168.124.19",
    "192.168.124.20"
])

# Generator for valid phone numbers (10 digits)
phone_number_strategy = st.text(
    min_size=10,
    max_size=10,
    alphabet=st.characters(whitelist_categories=('Nd',))
)

# Generator for valid indices (1-9 as strings)
index_strategy = st.integers(min_value=1, max_value=9).map(str)

# Generator for host_local addresses
host_local_strategy = st.text(min_size=10, max_size=30).filter(lambda x: ':' in x or '.' in x)

# Generator for device info: [phone, index, "", ""]
device_info_strategy = st.tuples(
    phone_number_strategy,
    index_strategy,
    st.just(""),
    st.just("")
).map(list)


@given(
    ip1=ip_strategy,
    ip2=ip_strategy,
    host_local=host_local_strategy,
    device1=device_info_strategy,
    device2=device_info_strategy
)
@settings(max_examples=100)
def test_property_stop_docker_isolation(ip1, ip2, host_local, device1, device2):
    """
    Property 8: Machine Operation Isolation - stop_docker
    
    For any two different IP addresses, stopping a machine on IP1 should only
    affect machines on IP1 and not affect machines on IP2.
    
    This test verifies that the stop_docker function constructs URLs with the
    correct IP address and that operations are isolated per IP.
    """
    # Ensure we're testing with different IPs
    assume(ip1 != ip2)
    
    phone1, index1 = device1[0], device1[1]
    phone2, index2 = device2[0], device2[1]
    
    # Mock requests.get to capture API calls
    with patch('MachineManage.stop_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Stop machine on IP1
        stop_docker(ip1, host_local, index1, phone1)
        
        # Verify the API call was made with IP1
        expected_name1 = f"T100{index1}-{phone1}"
        expected_url1 = f"http://{host_local}/dc_api/v1/stop/{ip1}/{expected_name1}"
        mock_get.assert_called_once_with(expected_url1)
        
        # Verify the URL contains IP1 and not IP2
        actual_url = mock_get.call_args[0][0]
        assert ip1 in actual_url, f"URL should contain IP1 ({ip1})"
        assert ip2 not in actual_url, f"URL should not contain IP2 ({ip2})"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Stop machine on IP2
        stop_docker(ip2, host_local, index2, phone2)
        
        # Verify the API call was made with IP2
        expected_name2 = f"T100{index2}-{phone2}"
        expected_url2 = f"http://{host_local}/dc_api/v1/stop/{ip2}/{expected_name2}"
        mock_get.assert_called_once_with(expected_url2)
        
        # Verify the URL contains IP2 and not IP1
        actual_url = mock_get.call_args[0][0]
        assert ip2 in actual_url, f"URL should contain IP2 ({ip2})"
        assert ip1 not in actual_url, f"URL should not contain IP1 ({ip1})"


@given(
    ip1=ip_strategy,
    ip2=ip_strategy,
    host_local=host_local_strategy,
    device1=device_info_strategy,
    device2=device_info_strategy
)
@settings(max_examples=100)
def test_property_start_docker_isolation(ip1, ip2, host_local, device1, device2):
    """
    Property 8: Machine Operation Isolation - start_docker
    
    For any two different IP addresses, starting a machine on IP1 should only
    affect machines on IP1 and not affect machines on IP2.
    """
    # Ensure we're testing with different IPs
    assume(ip1 != ip2)
    
    phone1, index1 = device1[0], device1[1]
    phone2, index2 = device2[0], device2[1]
    
    # Mock requests.get to capture API calls
    with patch('MachineManage.start_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Start machine on IP1
        start_docker(ip1, host_local, index1, phone1)
        
        # Verify the API call was made with IP1
        expected_name1 = f"T100{index1}-{phone1}"
        expected_url1 = f"http://{host_local}/dc_api/v1/run/{ip1}/{expected_name1}"
        mock_get.assert_called_once_with(expected_url1)
        
        # Verify the URL contains IP1 and not IP2
        actual_url = mock_get.call_args[0][0]
        assert ip1 in actual_url, f"URL should contain IP1 ({ip1})"
        assert ip2 not in actual_url, f"URL should not contain IP2 ({ip2})"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Start machine on IP2
        start_docker(ip2, host_local, index2, phone2)
        
        # Verify the API call was made with IP2
        expected_name2 = f"T100{index2}-{phone2}"
        expected_url2 = f"http://{host_local}/dc_api/v1/run/{ip2}/{expected_name2}"
        mock_get.assert_called_once_with(expected_url2)
        
        # Verify the URL contains IP2 and not IP1
        actual_url = mock_get.call_args[0][0]
        assert ip2 in actual_url, f"URL should contain IP2 ({ip2})"
        assert ip1 not in actual_url, f"URL should not contain IP1 ({ip1})"


@given(
    ip1=ip_strategy,
    ip2=ip_strategy,
    host_local=host_local_strategy,
    device1=device_info_strategy,
    device2=device_info_strategy
)
@settings(max_examples=100)
def test_property_delete_docker_isolation(ip1, ip2, host_local, device1, device2):
    """
    Property 8: Machine Operation Isolation - delete_docker
    
    For any two different IP addresses, deleting a machine on IP1 should only
    affect machines on IP1 and not affect machines on IP2.
    """
    # Ensure we're testing with different IPs
    assume(ip1 != ip2)
    
    phone1, index1 = device1[0], device1[1]
    phone2, index2 = device2[0], device2[1]
    
    # Mock requests.get to capture API calls
    with patch('MachineManage.delete_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Delete machine on IP1
        delete_docker(ip1, host_local, index1, phone1)
        
        # Verify the API call was made with IP1
        expected_name1 = f"T100{index1}-{phone1}"
        expected_url1 = f"http://{host_local}/dc_api/v1/remove/{ip1}/{expected_name1}"
        mock_get.assert_called_once_with(expected_url1)
        
        # Verify the URL contains IP1 and not IP2
        actual_url = mock_get.call_args[0][0]
        assert ip1 in actual_url, f"URL should contain IP1 ({ip1})"
        assert ip2 not in actual_url, f"URL should not contain IP2 ({ip2})"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Delete machine on IP2
        delete_docker(ip2, host_local, index2, phone2)
        
        # Verify the API call was made with IP2
        expected_name2 = f"T100{index2}-{phone2}"
        expected_url2 = f"http://{host_local}/dc_api/v1/remove/{ip2}/{expected_name2}"
        mock_get.assert_called_once_with(expected_url2)
        
        # Verify the URL contains IP2 and not IP1
        actual_url = mock_get.call_args[0][0]
        assert ip2 in actual_url, f"URL should contain IP2 ({ip2})"
        assert ip1 not in actual_url, f"URL should not contain IP1 ({ip1})"


@given(
    ip1=ip_strategy,
    ip2=ip_strategy,
    host_local=host_local_strategy,
    device_list1=st.lists(device_info_strategy, min_size=1, max_size=5),
    device_list2=st.lists(device_info_strategy, min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_property_batch_operations_isolation(ip1, ip2, host_local, device_list1, device_list2):
    """
    Property 8: Machine Operation Isolation - batch operations
    
    For any two different IP addresses, batch operations (stop_batch, start_batch)
    on IP1 should only affect machines on IP1 and not affect machines on IP2.
    
    This test verifies that batch operations maintain IP isolation across
    multiple devices.
    """
    # Ensure we're testing with different IPs
    assume(ip1 != ip2)
    
    # Test stop_batch isolation
    with patch('MachineManage.stop_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Stop batch on IP1
        stop_batch(ip1, host_local, device_list1)
        
        # Verify all API calls were made with IP1
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip1 in url, f"All stop_batch URLs should contain IP1 ({ip1})"
            assert ip2 not in url, f"No stop_batch URLs should contain IP2 ({ip2})"
        
        # Verify the number of calls matches the device list
        assert mock_get.call_count == len(device_list1), \
            f"Should make {len(device_list1)} API calls for IP1"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Stop batch on IP2
        stop_batch(ip2, host_local, device_list2)
        
        # Verify all API calls were made with IP2
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip2 in url, f"All stop_batch URLs should contain IP2 ({ip2})"
            assert ip1 not in url, f"No stop_batch URLs should contain IP1 ({ip1})"
        
        # Verify the number of calls matches the device list
        assert mock_get.call_count == len(device_list2), \
            f"Should make {len(device_list2)} API calls for IP2"
    
    # Test start_batch isolation
    with patch('MachineManage.start_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Start batch on IP1
        start_batch(ip1, host_local, device_list1)
        
        # Verify all API calls were made with IP1
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip1 in url, f"All start_batch URLs should contain IP1 ({ip1})"
            assert ip2 not in url, f"No start_batch URLs should contain IP2 ({ip2})"
        
        # Verify the number of calls matches the device list
        assert mock_get.call_count == len(device_list1), \
            f"Should make {len(device_list1)} API calls for IP1"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Start batch on IP2
        start_batch(ip2, host_local, device_list2)
        
        # Verify all API calls were made with IP2
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip2 in url, f"All start_batch URLs should contain IP2 ({ip2})"
            assert ip1 not in url, f"No start_batch URLs should contain IP1 ({ip1})"
        
        # Verify the number of calls matches the device list
        assert mock_get.call_count == len(device_list2), \
            f"Should make {len(device_list2)} API calls for IP2"


@given(
    ip1=ip_strategy,
    ip2=ip_strategy,
    host_local=host_local_strategy,
    names1=st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=5),
    names2=st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_property_stop_machines_all_isolation(ip1, ip2, host_local, names1, names2):
    """
    Property 8: Machine Operation Isolation - stop_machines_all
    
    For any two different IP addresses, stopping all machines on IP1 should only
    affect machines on IP1 and not affect machines on IP2.
    
    This test verifies that the stop_machines_all function maintains IP isolation
    when stopping multiple machines by name.
    """
    # Ensure we're testing with different IPs
    assume(ip1 != ip2)
    
    # Mock requests.get to capture API calls
    with patch('MachineManage.stop_machine.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = '{"code": 200, "message": "success"}'
        mock_get.return_value = mock_response
        
        # Stop all machines on IP1
        stop_machines_all(ip1, host_local, names1)
        
        # Verify all API calls were made with IP1
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip1 in url, f"All stop URLs should contain IP1 ({ip1})"
            assert ip2 not in url, f"No stop URLs should contain IP2 ({ip2})"
        
        # Verify the number of calls matches the name list
        assert mock_get.call_count == len(names1), \
            f"Should make {len(names1)} API calls for IP1"
        
        # Reset mock
        mock_get.reset_mock()
        
        # Stop all machines on IP2
        stop_machines_all(ip2, host_local, names2)
        
        # Verify all API calls were made with IP2
        for call_args in mock_get.call_args_list:
            url = call_args[0][0]
            assert ip2 in url, f"All stop URLs should contain IP2 ({ip2})"
            assert ip1 not in url, f"No stop URLs should contain IP1 ({ip1})"
        
        # Verify the number of calls matches the name list
        assert mock_get.call_count == len(names2), \
            f"Should make {len(names2)} API calls for IP2"


if __name__ == "__main__":
    # Run the property tests
    print("Running Property 8: Machine Operation Isolation tests...")
    print("=" * 60)
    
    tests = [
        ("stop_docker isolation", test_property_stop_docker_isolation),
        ("start_docker isolation", test_property_start_docker_isolation),
        ("delete_docker isolation", test_property_delete_docker_isolation),
        ("batch operations isolation", test_property_batch_operations_isolation),
        ("stop_machines_all isolation", test_property_stop_machines_all_isolation)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ test_property_{test_name.replace(' ', '_')} passed (100 examples)")
        except Exception as e:
            print(f"✗ test_property_{test_name.replace(' ', '_')} failed: {e}")
            failed_tests.append((test_name, e))
    
    print("=" * 60)
    
    if failed_tests:
        print(f"✗ {len(failed_tests)} test(s) failed:")
        for test_name, error in failed_tests:
            print(f"  - {test_name}: {error}")
        raise Exception(f"{len(failed_tests)} test(s) failed")
    else:
        print("✓ All Property 8 tests passed!")
