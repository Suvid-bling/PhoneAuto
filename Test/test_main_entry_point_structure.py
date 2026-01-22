"""
Structural tests for the main entry point (auto_SmsRelogin.py)

These tests verify the structure and components of the main entry point
without actually importing it (to avoid dependency issues).
"""

import ast
import os
import sys


def test_main_entry_point_structure():
    """Test that the main entry point has the required structure"""
    
    # Read the file
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse the AST
    tree = ast.parse(content)
    
    # Check for required imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    assert 'argparse' in imports, "Missing argparse import"
    assert 'AutoTasks.ip_orchestrator' in imports, "Missing ip_orchestrator import"
    
    # Check for required functions
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    assert 'print_summary' in functions, "Missing print_summary function"
    assert 'main' in functions, "Missing main function"
    
    # Check for main block
    has_main_block = False
    for node in tree.body:
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                    has_main_block = True
                    break
    
    assert has_main_block, "Missing if __name__ == '__main__' block"
    
    print("✓ All structural checks passed")
    return True


def test_argument_parser_structure():
    """Test that the argument parser is properly configured"""
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for required argument parser elements
    assert 'ArgumentParser' in content, "Missing ArgumentParser"
    assert '--mode' in content, "Missing --mode argument"
    assert '--max-parallel' in content, "Missing --max-parallel argument"
    assert "choices=['sequential', 'parallel']" in content, "Missing mode choices"
    
    print("✓ Argument parser structure is correct")
    return True


def test_process_all_ips_call():
    """Test that process_all_ips is called with correct parameters"""
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for process_all_ips call
    assert 'process_all_ips' in content, "Missing process_all_ips call"
    assert 'mode=args.mode' in content, "Missing mode parameter"
    assert 'max_parallel=args.max_parallel' in content, "Missing max_parallel parameter"
    
    print("✓ process_all_ips is called correctly")
    return True


def test_summary_printing():
    """Test that summary printing is implemented"""
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for summary printing
    assert 'print_summary(results)' in content, "Missing print_summary call"
    assert 'PROCESSING SUMMARY' in content, "Missing summary header"
    
    print("✓ Summary printing is implemented")
    return True


def test_old_function_removed():
    """Test that the old process_batch_relogin function is removed"""
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that old function is removed
    assert 'def process_batch_relogin' not in content, "Old process_batch_relogin function still exists"
    
    # Check that old imports are removed
    assert 'from MachineManage.stop_machine import' not in content, "Old machine management imports still exist"
    assert 'from MachineManage.start_machine import' not in content, "Old machine management imports still exist"
    
    print("✓ Old function and imports removed")
    return True


def test_exit_codes():
    """Test that proper exit codes are used"""
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'AutoTasks', 'auto_SmsRelogin.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for exit codes
    assert 'sys.exit(0)' in content, "Missing success exit code"
    assert 'sys.exit(1)' in content, "Missing error exit code"
    assert "results['failed_ips']" in content, "Missing failed_ips check"
    
    print("✓ Exit codes are properly implemented")
    return True


if __name__ == '__main__':
    print("Testing main entry point structure...\n")
    
    try:
        test_main_entry_point_structure()
        test_argument_parser_structure()
        test_process_all_ips_call()
        test_summary_printing()
        test_old_function_removed()
        test_exit_codes()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
