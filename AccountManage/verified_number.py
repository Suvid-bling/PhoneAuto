import requests
import time
from typing import Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sys
import os

# Add parent directory to path to import SMSLogin modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SMSLogin.SmsRelogin import get_SmsUrl

# Thread lock for file operations
file_lock = threading.Lock()

def sms_request(url):
    headers = {
        'User-Agent': 'curl/8.7.1',
        'Accept': '*/*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        status_code = str(response.status_code)
        
        # Check if it's a successful response (200-299)
        if response.status_code >= 200 and response.status_code < 300:
            try:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('key_expiration_time'), status_code
                else:
                    return "None                ", status_code
            except ValueError as json_error:
                return "None                ", status_code
        else:
            # Handle non-2xx status codes (like 404, 500, etc.)
            return "None                ", status_code
            
    except requests.exceptions.Timeout:
        return "None                ", "Timeout"
    except requests.exceptions.ConnectionError:
        return "None                ", "Connection Error"
    except requests.exceptions.RequestException as e:
        # Try to get status code from the exception's response
        if hasattr(e, 'response') and e.response is not None:
            status_code = str(e.response.status_code)
        else:
            status_code = "Request Failed"
        return "None                ", status_code
    except Exception as e:
        return "None                ", "Unknown Error"

def list_EndAdd(phone_number="4502395386", text="teststring", file_path: str = "PhoneInitial/SMSLogin/active_phonenumber.txt"):
    """
    Add text to the end of an existing phone number entry and sort by phone number.
    Pads text with spaces to ensure it's exactly 20 characters long.
    
    Args:
        phone_number: The phone number to find and modify
        text: Text to append to the end of the list entry
        file_path: Path to the file containing phone number data
    """
    import ast
    import os
    
    # Pad text with spaces to make it exactly 20 characters
    if len(text) < 20:
        text = text + ' ' * (20 - len(text))
    elif len(text) > 20:
        text = text[:20]  # Truncate if longer than 20 characters
    
    # Read existing data
    entries = []
    found_entry = False
        
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Parse the list from string representation
                        entry = ast.literal_eval(line.rstrip(','))
                        
                        # If this is the phone number we're looking for, append the text
                        if entry[0] == phone_number:
                            entry.append(text)
                            found_entry = True
                        
                        entries.append(entry)
                    except (ValueError, SyntaxError) as e:
                        continue
    
    if not found_entry:
        return False
    
    # Sort by phone number
    entries.sort(key=lambda x: x[0])
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"{entry},\n")
    
    return True 

def get_allNumber(file_path: str = "PhoneInitial/SMSLogin/active_phonenumber.txt"):
    """
    Get all phone numbers from the specified file.
    
    Args:
        file_path: Path to the file containing phone number data
        
    Returns:
        list: List of all phone numbers found in the file
    """
    import ast
    import os
    
    phone_numbers = []
    
    if not os.path.exists(file_path):
        return phone_numbers
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        # Parse the list from string representation
                        entry = ast.literal_eval(line.rstrip(','))
                        
                        # Extract phone number (first element of the list)
                        if isinstance(entry, list) and len(entry) > 0:
                            phone_number = entry[0]
                            phone_numbers.append(phone_number)
                        
                    except (ValueError, SyntaxError) as e:
                        continue
    
    except Exception as e:
        return []
    
    return phone_numbers

def process_single_number(phone_number: str, index: int, total: int) -> Dict[str, Any]:
    """
    Process a single phone number - get SMS URL and expiration time.
    ALWAYS adds both expiration_time and status to file, regardless of success.
    
    Args:
        phone_number: The phone number to process
        index: Current index for progress tracking
        total: Total number of phone numbers
        
    Returns:
        dict: Result containing phone number, success status, and data
    """
    print(f"Processing {index}/{total}: {phone_number}")
    
    try:
        # Get SMS URL for this phone number
        sms_url = get_SmsUrl(phone_number)
        
        if not sms_url:
            # Still add to file even if no SMS URL found
            with file_lock:
                success1 = list_EndAdd(phone_number, "No SMS URL")
                success2 = list_EndAdd(phone_number, "No URL")
            
            return {
                'phone_number': phone_number,
                'success': False,
                'error': 'No SMS URL found',
                'sms_url': None,
                'expiration_time': "No SMS URL",
                'status': "No URL"
            }
               
        # Request the SMS URL - ALWAYS get both values
        expiration_time, status = sms_request(sms_url)
        
        # ALWAYS add both values to file, regardless of success
        with file_lock:
            success1 = list_EndAdd(phone_number, expiration_time)
            success2 = list_EndAdd(phone_number, status)
        
        # Determine if this is considered a "success" (found valid expiration time)
        is_success = expiration_time and expiration_time != "None                "
        
        if is_success:
            return {
                'phone_number': phone_number,
                'success': True,
                'sms_url': sms_url,
                'expiration_time': expiration_time,
                'status': status
            }
        else:
            return {
                'phone_number': phone_number,
                'success': False,
                'error': f'No expiration time found, Status: {status}',
                'sms_url': sms_url,
                'expiration_time': expiration_time,
                'status': status
            }
            
    except Exception as e:
        # Even on exception, try to add error info to file
        with file_lock:
            success1 = list_EndAdd(phone_number, "Error")
            success2 = list_EndAdd(phone_number, f"Exception: {str(e)[:20]}")
        
        return {
            'phone_number': phone_number,
            'success': False,
            'error': str(e),
            'sms_url': None,
            'expiration_time': "Error",
            'status': f"Exception: {str(e)[:20]}"
            }

def process_numbers_multithreaded(phone_numbers: list, max_workers: int = 5) -> list:
    """
    Process multiple phone numbers concurrently using ThreadPoolExecutor.
    
    Args:
        phone_numbers: List of phone numbers to process
        max_workers: Maximum number of concurrent threads (default: 5)
        
    Returns:
        list: List of successful results
    """
    successful_results = []
    total = len(phone_numbers)
    
    print(f"Processing {total} phone numbers with {max_workers} concurrent threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_phone = {
            executor.submit(process_single_number, phone_number, i+1, total): phone_number 
            for i, phone_number in enumerate(phone_numbers)
        }
        
        # Process completed tasks
        for future in as_completed(future_to_phone):
            phone_number = future_to_phone[future]
            result = future.result()
            if result['success']:
                successful_results.append(result)
    
    return successful_results

if __name__ == "__main__":
    all_numbers = get_allNumber()
      
    # Ask user for threading preference
    use_threading = input("Use multithreading? (y/n, default=y): ").lower()
    use_threading = use_threading != 'n'
    
    if use_threading:
        # Get number of threads from user
        try:
            max_workers = int(input("Number of concurrent threads (default=5, max=10): ") or "5")
            max_workers = min(max_workers, 10)  # Limit to 10 to avoid overwhelming the server
        except ValueError:
            max_workers = 5
        
        # Process with multithreading
        start_time = time.time()
        successful_results = process_numbers_multithreaded(all_numbers, max_workers)
        end_time = time.time()
        
        print(f"Processing complete! Found {len(successful_results)} numbers with expiration times in {end_time - start_time:.2f} seconds")
        
    else:
        # Original sequential processing
        successful_results = []
        
        start_time = time.time()
        for i, phone_number in enumerate(all_numbers, 1):
            result = process_single_number(phone_number, i, len(all_numbers))
            if result['success']:
                successful_results.append(result)
            
            # Add delay for sequential processing
            time.sleep(0.5)
        
        end_time = time.time()
        
        print(f"Processing complete! Found {len(successful_results)} numbers with expiration times in {end_time - start_time:.2f} seconds")
    
    # Save results to file
    if successful_results:
        import json
        output_file = 'complete_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(successful_results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to '{output_file}'")