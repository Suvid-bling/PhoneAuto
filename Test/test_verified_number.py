import unittest
import tempfile
import os
import sys
import json
from unittest.mock import patch, Mock, MagicMock

# Add parent directory to path to import AccountManage
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AccountManage.verified_number import (
    sms_request,
    list_EndAdd,
    get_allNumber,
    process_single_number,
    process_numbers_multithreaded
)


class TestVerifiedNumber(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_numbers.txt")
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    @patch('verified_number.requests.get')
    def test_sms_request_success(self, mock_get):
        """Test successful SMS request with valid response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 0,
            'data': {'key_expiration_time': '2026-01-27T00:00:00Z'}
        }
        mock_get.return_value = mock_response
        
        result = sms_request("http://test.com/api")
        
        self.assertEqual(result, ('2026-01-27T00:00:00Z', '200'))

    @patch('verified_number.requests.get')
    def test_sms_request_timeout(self, mock_get):
        """Test SMS request timeout handling."""
        mock_get.side_effect = Exception("Timeout")
        
        result = sms_request("http://test.com/api")
        
        self.assertEqual(result, ("None                ", "Unknown Error"))

    @patch('verified_number.requests.get')
    def test_sms_request_404_error(self, mock_get):
        """Test SMS request with 404 status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = sms_request("http://test.com/api")
        
        self.assertEqual(result, ("None                ", "404"))

    def test_list_EndAdd_new_entry(self):
        """Test adding text to existing phone number entry."""
        # Create test file with sample data
        with open(self.test_file, 'w') as f:
            f.write("['4502395386', 1, 'http://test.com', 'https://api.com'],\n")
        
        result = list_EndAdd("4502395386", "test", self.test_file)
        
        self.assertTrue(result)
        
        # Verify the entry was updated
        with open(self.test_file, 'r') as f:
            content = f.read()
            self.assertIn("test", content)

    def test_list_EndAdd_nonexistent_phone(self):
        """Test adding text to non-existent phone number."""
        # Create test file with sample data
        with open(self.test_file, 'w') as f:
            f.write("['4502395386', 1, 'http://test.com', 'https://api.com'],\n")
        
        result = list_EndAdd("9999999999", "test", self.test_file)
        
        self.assertFalse(result)

    def test_get_allNumber_valid_file(self):
        """Test getting all phone numbers from valid file."""
        # Create test file with sample data
        with open(self.test_file, 'w') as f:
            f.write("['4502395386', 1, 'http://test.com', 'https://api.com'],\n")
            f.write("['4502395402', 1, 'http://test2.com', 'https://api2.com'],\n")
        
        result = get_allNumber(self.test_file)
        
        self.assertEqual(result, ['4502395386', '4502395402'])

    def test_get_allNumber_empty_file(self):
        """Test getting phone numbers from empty file."""
        # Create empty test file
        with open(self.test_file, 'w') as f:
            pass
        
        result = get_allNumber(self.test_file)
        
        self.assertEqual(result, [])

    def test_get_allNumber_nonexistent_file(self):
        """Test getting phone numbers from non-existent file."""
        result = get_allNumber("nonexistent_file.txt")
        
        self.assertEqual(result, [])

    @patch('verified_number.get_SmsUrl')
    @patch('verified_number.sms_request')
    @patch('verified_number.list_EndAdd')
    @patch('builtins.print')  # Suppress print statements during testing
    def test_process_single_number_success(self, mock_print, mock_list_add, mock_sms_req, mock_get_url):
        """Test successful processing of single phone number."""
        mock_get_url.return_value = "http://test.com/api"
        mock_sms_req.return_value = ("2026-01-27T00:00:00Z", "200")
        mock_list_add.return_value = True
        
        result = process_single_number("4502395386", 1, 1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['phone_number'], "4502395386")
        self.assertEqual(result['expiration_time'], "2026-01-27T00:00:00Z")

    @patch('verified_number.get_SmsUrl')
    @patch('verified_number.list_EndAdd')
    @patch('builtins.print')  # Suppress print statements during testing
    def test_process_single_number_no_sms_url(self, mock_print, mock_list_add, mock_get_url):
        """Test processing phone number with no SMS URL."""
        mock_get_url.return_value = None
        mock_list_add.return_value = True
        
        result = process_single_number("4502395386", 1, 1)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'No SMS URL found')

    @patch('verified_number.process_single_number')
    @patch('builtins.print')  # Suppress print statements during testing
    def test_process_numbers_multithreaded(self, mock_print, mock_process):
        """Test multithreaded processing of phone numbers."""
        mock_process.return_value = {
            'phone_number': '4502395386',
            'success': True,
            'expiration_time': '2026-01-27T00:00:00Z'
        }
        
        phone_numbers = ['4502395386', '4502395402']
        result = process_numbers_multithreaded(phone_numbers, max_workers=2)
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['success'] for r in result))


if __name__ == '__main__':
    unittest.main()