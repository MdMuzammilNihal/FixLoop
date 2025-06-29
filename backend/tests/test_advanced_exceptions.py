"""
Test file for advanced exception handling capabilities.
This file contains multiple types of exceptions and error scenarios to test how well
the AI assistant handles different types of errors and provides solutions.
"""
import os
import sys
import time
import json
import pickle
import sqlite3
from typing import Dict, List, Any, Union, Optional
import numpy as np  # Will fail if numpy not installed

class CustomError(Exception):
    """Custom exception class for testing purposes"""
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

def test_basic_exceptions():
    """Test handling of basic Python exceptions"""
    
    # 1. Division by zero
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        print(f"Caught expected ZeroDivisionError: {e}")
    
    # 2. Index error
    try:
        my_list = [1, 2, 3]
        item = my_list[10]
    except IndexError as e:
        print(f"Caught expected IndexError: {e}")
    
    # 3. Key error
    try:
        my_dict = {"a": 1, "b": 2}
        value = my_dict["c"]
    except KeyError as e:
        print(f"Caught expected KeyError: {e}")
    
    # 4. Type error
    try:
        result = "string" + 5
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
    
    # 5. Name error
    try:
        print(undefined_variable)
    except NameError as e:
        print(f"Caught expected NameError: {e}")
    
    # 6. Value error
    try:
        int("not a number")
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")

def test_file_exceptions():
    """Test handling of file-related exceptions"""
    
    # 1. File not found
    try:
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        print(f"Caught expected FileNotFoundError: {e}")
    
    # 2. Permission error (simulated)
    try:
        raise PermissionError("Permission denied: 'restricted_file.txt'")
    except PermissionError as e:
        print(f"Caught expected PermissionError: {e}")
    
    # 3. File exists error (simulated)
    try:
        raise FileExistsError("File already exists: 'existing_file.txt'")
    except FileExistsError as e:
        print(f"Caught expected FileExistsError: {e}")
    
    # 4. IsADirectoryError (simulated)
    try:
        raise IsADirectoryError("Is a directory: 'dir_not_file'")
    except IsADirectoryError as e:
        print(f"Caught expected IsADirectoryError: {e}")

def test_import_exceptions():
    """Test handling of import-related exceptions"""
    
    # 1. ModuleNotFoundError
    try:
        import nonexistent_module
    except ModuleNotFoundError as e:
        print(f"Caught expected ModuleNotFoundError: {e}")
    
    # 2. ImportError (simulated)
    try:
        raise ImportError("Cannot import name 'nonexistent_function' from 'os'")
    except ImportError as e:
        print(f"Caught expected ImportError: {e}")

def test_syntax_related():
    """Test handling of syntax-related exceptions (indirectly)"""
    
    # SyntaxError can't be caught directly as it's a compile-time error
    # But we can test the handling of code with syntax errors
    code_with_syntax_error = """
def function_with_syntax_error():
    if True
        print("Missing colon after if statement")
    """
    
    print("The code above has a syntax error (missing colon after if statement)")
    
    # IndentationError can't be caught directly either
    code_with_indentation_error = """
def function_with_indentation_error():
    if True:
    print("Incorrect indentation")
    """
    
    print("The code above has an indentation error")

def test_complex_exceptions():
    """Test handling of more complex exception scenarios"""
    
    # 1. Nested exceptions
    try:
        try:
            result = 1 / 0
        except ZeroDivisionError:
            # Re-raise with different exception type
            raise ValueError("Cannot proceed due to division by zero")
    except ValueError as e:
        print(f"Caught expected ValueError from nested exception: {e}")
    
    # 2. Custom exceptions
    try:
        raise CustomError("This is a custom error", 42)
    except CustomError as e:
        print(f"Caught expected CustomError: {e}, code: {e.error_code}")
    
    # 3. Exception with cleanup in finally block
    temp_created = False
    try:
        # Simulate creating a temporary resource
        temp_created = True
        print("Temporary resource created")
        raise RuntimeError("Something went wrong")
    except RuntimeError as e:
        print(f"Caught expected RuntimeError: {e}")
    finally:
        if temp_created:
            # Cleanup
            print("Cleaning up temporary resource")
    
    # 4. Exception groups (Python 3.11+) or simulated for older versions
    try:
        # Check Python version and use ExceptionGroup if available (3.11+)
        if sys.version_info >= (3, 11):
            raise ExceptionGroup(
                "Multiple errors",
                [
                    ValueError("First error"),
                    TypeError("Second error"),
                    KeyError("Third error")
                ]
            )
        else:
            # Simulate for older Python versions
            raise Exception("Multiple errors: ValueError, TypeError, KeyError")
    except Exception as e:
        print(f"Caught multiple exceptions (as ExceptionGroup or simulated): {e}")
    
    # 5. Async exception handling (simulated)
    print("In async code, exceptions need to be handled inside the coroutine or task")

def test_database_exceptions():
    """Test handling of database-related exceptions"""
    
    # 1. SQLite operational error
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nonexistent_table")
    except sqlite3.OperationalError as e:
        print(f"Caught expected SQLite OperationalError: {e}")
    
    # 2. SQLite syntax error
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INT, name TEXT)")
        cursor.execute("INSERT INTO test_table VALUES (1, 'test')")
        cursor.execute("SELCT * FROM test_table")  # Intentional typo
    except sqlite3.OperationalError as e:
        print(f"Caught expected SQLite syntax error: {e}")

def test_resource_exceptions():
    """Test handling of resource-related exceptions"""
    
    # 1. Memory error (simulated)
    try:
        # Don't actually cause this as it could crash the program
        raise MemoryError("Out of memory when allocating large array")
    except MemoryError as e:
        print(f"Caught expected MemoryError: {e}")
    
    # 2. Timeout error (simulated)
    try:
        raise TimeoutError("Operation timed out after 30 seconds")
    except TimeoutError as e:
        print(f"Caught expected TimeoutError: {e}")
    
    # 3. Resource warning (simulated)
    print("ResourceWarning: unclosed file <_io.TextIOWrapper name='temp.txt' mode='r'>")

def test_calculation_exceptions():
    """Test handling of calculation-related exceptions"""
    
    # 1. Overflow error (simulated)
    try:
        raise OverflowError("Mathematical overflow during calculation")
    except OverflowError as e:
        print(f"Caught expected OverflowError: {e}")
    
    # 2. Zero division in different context
    try:
        numbers = [1, 2, 0, 4, 5]
        results = []
        for n in numbers:
            results.append(10 / n)
    except ZeroDivisionError as e:
        print(f"Caught expected ZeroDivisionError in loop: {e}")
    
    # 3. Floating point error (simulated)
    try:
        # This would actually produce inf, not an exception in Python
        x = float('inf')
        print(f"Calculating with infinity: {x} * 2 = {x * 2}")
        
        # Raise a FloatingPointError to simulate
        raise FloatingPointError("Floating point calculation error")
    except FloatingPointError as e:
        print(f"Caught expected FloatingPointError: {e}")

def test_serialization_exceptions():
    """Test handling of serialization-related exceptions"""
    
    # 1. JSON decode error
    try:
        invalid_json = "{'key': 'value'}"  # Should use double quotes
        data = json.loads(invalid_json)
    except json.JSONDecodeError as e:
        print(f"Caught expected JSONDecodeError: {e}")
    
    # 2. Pickle error
    class Unpicklable:
        def __reduce__(self):
            raise NotImplementedError("This class cannot be pickled")
    
    try:
        obj = Unpicklable()
        pickle_data = pickle.dumps(obj)
    except Exception as e:
        print(f"Caught expected pickling error: {e}")

def run_all_exception_tests():
    """Run all exception handling tests"""
    
    print("\n===== Testing Basic Exceptions =====")
    test_basic_exceptions()
    
    print("\n===== Testing File Exceptions =====")
    test_file_exceptions()
    
    print("\n===== Testing Import Exceptions =====")
    test_import_exceptions()
    
    print("\n===== Testing Syntax Related Issues =====")
    test_syntax_related()
    
    print("\n===== Testing Complex Exceptions =====")
    test_complex_exceptions()
    
    print("\n===== Testing Database Exceptions =====")
    test_database_exceptions()
    
    print("\n===== Testing Resource Exceptions =====")
    test_resource_exceptions()
    
    print("\n===== Testing Calculation Exceptions =====")
    test_calculation_exceptions()
    
    print("\n===== Testing Serialization Exceptions =====")
    test_serialization_exceptions()

if __name__ == "__main__":
    print("Running Advanced Exception Handling Tests")
    run_all_exception_tests()
    print("All exception tests completed") 