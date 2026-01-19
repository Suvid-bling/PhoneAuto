import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Autolization.AutoOperate import AutoPhone


class TestUpdateApp(unittest.TestCase):
    
    @patch('Autolization.AutoOperate.subprocess.run')
    def test_update_app_success(self, mock_run):
        # Mock successful installation
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        phone = AutoPhone(ip="192.168.124.26", port="5002", auto_connect=False)
        result = phone.update_app()
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
    @patch('Autolization.AutoOperate.subprocess.run')
    def test_update_app_failure(self, mock_run):
        # Mock failed installation
        mock_run.return_value = MagicMock(returncode=1, stderr="Installation failed")
        
        phone = AutoPhone(ip="192.168.124.26", port="5002", auto_connect=False)
        result = phone.update_app()
        
        self.assertFalse(result)
        mock_run.assert_called_once()


class TestUpdateAppIntegration(unittest.TestCase):
    """Integration test - requires real device connected"""
    
    def test_update_app_real_device(self):
        # Skip if no device available
        import subprocess
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        if "192.168.124.26:5002" not in result.stdout:
            self.skipTest("Device 192.168.124.26:5002 not connected")
        
        phone = AutoPhone(ip="192.168.124.26", port="5002", auto_connect=False)
        result = phone.update_app()
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
