import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from MachineManage.start_machine import wait_machines_ready


class TestWaitMachinesReady(unittest.TestCase):
    
    @patch('MachineManage.start_machine.check_machinestate')
    @patch('time.sleep')
    def test_all_machines_ready_immediately(self, mock_sleep, mock_check):
        """Test when all machines are ready on first check"""
        mock_check.return_value = True
        
        device_info_list = [["1234567890", 1, "", ""], ["0987654321", 2, "", ""]]
        result = wait_machines_ready("192.168.1.100", "localhost:5000", device_info_list, max_wait_time=60, check_interval=5)
        
        self.assertTrue(result)
        mock_sleep.assert_not_called()
    
    @patch('MachineManage.start_machine.check_machinestate')
    @patch('time.sleep')
    def test_machines_ready_after_wait(self, mock_sleep, mock_check):
        """Test when machines become ready after some checks"""
        mock_check.side_effect = [False, False, True, True]
        
        device_info_list = [["1234567890", 1, "", ""]]
        result = wait_machines_ready("192.168.1.100", "localhost:5000", device_info_list, max_wait_time=60, check_interval=5)
        
        self.assertTrue(result)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('MachineManage.start_machine.check_machinestate')
    @patch('time.sleep')
    def test_timeout_waiting_for_machines(self, mock_sleep, mock_check):
        """Test timeout when machines never become ready"""
        mock_check.return_value = False
        
        device_info_list = [["1234567890", 1, "", ""]]
        result = wait_machines_ready("192.168.1.100", "localhost:5000", device_info_list, max_wait_time=20, check_interval=10)
        
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()
