# Test file for exception handling capabilities

# Division by zero error
def divide_numbers(a, b):
    return a / b

# Index error
def access_element(lst, index):
    return lst[index]

# Type error
def add_values(a, b):
    return a + b

# File not found error
def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Key error
def get_value(dictionary, key):
    return dictionary[key]

# Value error
def convert_to_int(value):
    return int(value)

# Attribute error
def call_method(obj, method_name):
    method = getattr(obj, method_name)
    return method()

# Import error
def use_library(library_name):
    try:
        module = __import__(library_name)
        return f"Successfully imported {library_name}"
    except ImportError:
        return f"Failed to import {library_name}"

# Name error
def use_undefined_variable():
    return undefined_variable

# Exception handling with try/except
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except TypeError:
        return "Invalid types for division"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Main execution
if __name__ == "__main__":
    # Test safe function
    print(f"Safe divide 10/2: {safe_divide(10, 2)}")
    print(f"Safe divide 10/0: {safe_divide(10, 0)}")
    print(f"Safe divide 'hello'/2: {safe_divide('hello', 2)}")
    
    # Test unsafe functions
    try:
        print(f"Unsafe divide 10/0: {divide_numbers(10, 0)}")
    except ZeroDivisionError as e:
        print(f"Caught exception: {e}")
    
    try:
        empty_list = []
        print(f"Access element 5 in empty list: {access_element(empty_list, 5)}")
    except IndexError as e:
        print(f"Caught exception: {e}")
    
    try:
        print(f"Add string to number: {add_values('hello', 5)}")
    except TypeError as e:
        print(f"Caught exception: {e}")
    
    try:
        print(f"Read non-existent file: {read_file('nonexistent.txt')}")
    except FileNotFoundError as e:
        print(f"Caught exception: {e}")
    
    try:
        empty_dict = {}
        print(f"Access non-existent key: {get_value(empty_dict, 'key')}")
    except KeyError as e:
        print(f"Caught exception: {e}")
    
    try:
        print(f"Convert invalid string to int: {convert_to_int('hello')}")
    except ValueError as e:
        print(f"Caught exception: {e}")
    
    try:
        print(f"Call method on object that doesn't have it: {call_method(5, 'my_method')}")
    except AttributeError as e:
        print(f"Caught exception: {e}")
    
    try:
        print(use_undefined_variable())
    except NameError as e:
        print(f"Caught exception: {e}")
    
    # Test import error
    print(use_library("nonexistent_library"))
    print(use_library("math"))  # This should succeed 