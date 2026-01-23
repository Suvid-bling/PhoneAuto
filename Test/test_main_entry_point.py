"""
Unit tests for the main entry point (auto_SmsRelogin.py)

Tests command-line argument parsing and main function behavior.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMainEntryPoint(unittest.TestCase):
    """Test the main entry point command-line interface"""
    
    def test_help_argument(self):
        """Test that --help displays usage information"""
        # Import here to avoid module-level import issues
        from AutoTasks import auto_SmsRelogin
        
        with patch('sys.argv', ['auto_SmsRelogin.py', '--help']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    auto_SmsRelogin.main()
                except SystemExit as e:
                    # --help should exit with code 0
                    self.assertEqual(e.code, 0)
                    output = fake_out.getvalue()
                    self.assertIn('Multi-IP SMS Relogin Automation', output)
                    self.assertIn('--mode', output)
                    self.assertIn('--max-parallel', output)
    
    def test_sequential_mode_argument(self):
        """Test sequential mode argument parsing"""
        from AutoTasks import auto_SmsRelogin
        
        with patch('sys.argv', ['auto_SmsRelogin.py', '--mode', 'sequential']):
            with patch('AutoTasks.auto_SmsRelogin.process_all_ips') as mock_process:
                mock_process.return_value = {
                    'total_ips': 2,
                    'completed_ips': 2,
                    'failed_ips': 0,
                    'results': {}
                }
                
                try:
                    auto_SmsRelogin.main()
                except SystemExit as e:
                    # Should exit with code 0 on success
                    self.assertEqual(e.code, 0)
                    # Verify process_all_ips was called with correct mode
                    mock_process.assert_called_once_with(mode='sequential', max_parallel=3)
    
    def test_parallel_mode_argument(self):
        """Test parallel mode argument parsing"""
        from AutoTasks import auto_SmsRelogin
        
        with patch('sys.argv', ['auto_SmsRelogin.py', '--mode', 'parallel', '--max-parallel', '5']):
            with patch('AutoTasks.auto_SmsRelogin.process_all_ips') as mock_process:
                mock_process.return_value = {
                    'total_ips': 2,
                    'completed_ips': 2,
                    'failed_ips': 0,
                    'results': {}
                }
                
                try:
                    auto_SmsRelogin.main()
                except SystemExit as e:
                    # Should exit with code 0 on success
                    self.assertEqual(e.code, 0)
                    # Verify process_all_ips was called with correct arguments
                    mock_process.assert_called_once_with(mode='parallel', max_parallel=5)
    
    def test_invalid_max_parallel(self):
        """Test that invalid max_parallel value is rejected"""
        from AutoTasks import auto_SmsRelogin
        
        with patch('sys.argv', ['auto_SmsRelogin.py', '--max-parallel', '0']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    auto_SmsRelogin.main()
                except SystemExit as e:
                    # Should exit with error code
                    self.assertEqual(e.code, 1)
                    output = fake_out.getvalue()
                    self.assertIn('must be at least 1', output)
    
    def test_failed_ips_exit_code(self):
        """Test that failed IPs result in non-zero exit code"""
        from AutoTasks import auto_SmsRelogin
        
        with patch('sys.argv', ['auto_SmsRelogin.py', '--mode', 'sequential']):
            with patch('AutoTasks.auto_SmsRelogin.process_all_ips') as mock_process:
                mock_process.return_value = {
                    'total_ips': 2,
                    'completed_ips': 1,
                    'failed_ips': 1,
                    'results': {
                        '192.168.1.1': {'success_count': 5, 'failure_count': 0},
                        '192.168.1.2': {'error': 'Connection failed'}
                    }
                }
                
                try:
                    auto_SmsRelogin.main()
                except SystemExit as e:
                    # Should exit with error code when IPs fail
                    self.assertEqual(e.code, 1)
    
    def test_print_summary_with_success(self):
        """Test summary printing with successful results"""
        from AutoTasks.auto_SmsRelogin import print_summary
        
        results = {
            'total_ips': 2,
            'completed_ips': 2,
            'failed_ips': 0,
            'results': {
                '192.168.1.1': {
                    'processed_batches': 3,
                    'success_count': 10,
                    'failure_count': 2
                },
                '192.168.1.2': {
                    'processed_batches': 2,
                    'success_count': 8,
                    'failure_count': 1
                }
            }
        }
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_summary(results)
            output = fake_out.getvalue()
            
            self.assertIn('PROCESSING SUMMARY', output)
            self.assertIn('Total IPs: 2', output)
            self.assertIn('Completed: 2', output)
            self.assertIn('Failed: 0', output)
            self.assertIn('192.168.1.1', output)
            self.assertIn('192.168.1.2', output)
            self.assertIn('COMPLETED', output)
    
    def test_print_summary_with_errors(self):
        """Test summary printing with error results"""
        from AutoTasks.auto_SmsRelogin import print_summary
        
        results = {
            'total_ips': 2,
            'completed_ips': 1,
            'failed_ips': 1,
            'results': {
                '192.168.1.1': {
                    'processed_batches': 3,
                    'success_count': 10,
                    'failure_count': 2
                },
                '192.168.1.2': {
                    'error': 'Connection timeout'
                }
            }
        }
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_summary(results)
            output = fake_out.getvalue()
            
            self.assertIn('PROCESSING SUMMARY', output)
            self.assertIn('Total IPs: 2', output)
            self.assertIn('Completed: 1', output)
            self.assertIn('Failed: 1', output)
            self.assertIn('192.168.1.2', output)
            self.assertIn('FAILED', output)
            self.assertIn('Connection timeout', output)


if __name__ == '__main__':
    unittest.main()
