# -*- encoding=utf8 -*-

import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Autolization.AutoOperate import AutoPhone


def test_wait_for_image_snap_time():
    """Test the snap time (screenshot interval) of wait_for_image function"""
    
    # Initialize AutoPhone
    auto_phone = AutoPhone()
    
    # Test parameters
    test_image = "tpl1766712390329.png"  # Use an existing test image
    timeout = 10  # Short timeout for testing
    interval = 1  # Default interval
    
    print(f"\n{'='*60}")
    print(f"Testing wait_for_image snap time")
    print(f"{'='*60}")
    print(f"Image: {test_image}")
    print(f"Timeout: {timeout}s")
    print(f"Interval: {interval}s")
    print(f"{'='*60}\n")
    
    # Measure actual snap time
    start_time = time.time()
    result = auto_phone.wait_for_image(test_image, timeout=timeout, interval=interval)
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"Test Results:")
    print(f"{'='*60}")
    print(f"Total elapsed time: {elapsed_time:.2f}s")
    print(f"Expected interval: {interval}s")
    print(f"Result found: {result is not None}")
    
    if result:
        print(f"Match confidence: {result.get('confidence', 'N/A')}")
        print(f"Match position: {result.get('result', 'N/A')}")
    
    print(f"{'='*60}\n")
    
    return result


def test_different_intervals():
    """Test wait_for_image with different snap intervals"""
    
    auto_phone = AutoPhone()
    test_image = "tpl1766712390329.png"
    intervals = [0.5, 1, 2]  # Different intervals to test
    
    print(f"\n{'='*60}")
    print(f"Testing different snap intervals")
    print(f"{'='*60}\n")
    
    for interval in intervals:
        print(f"Testing with interval: {interval}s")
        start_time = time.time()
        result = auto_phone.wait_for_image(test_image, timeout=5, interval=interval)
        elapsed_time = time.time() - start_time
        
        print(f"  Elapsed time: {elapsed_time:.2f}s")
        print(f"  Found: {result is not None}")
        print()


if __name__ == "__main__":
    # Run basic snap time test
    test_wait_for_image_snap_time()
    
    # Run interval comparison test
    # test_different_intervals()
