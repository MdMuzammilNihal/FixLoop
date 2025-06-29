# Buggy Python code to test the fix capabilities

# Bug: off-by-one error in range
def sum_numbers(n):
    total = 0
    for i in range(0, n - 1):  # Should be range(0, n) or range(n)
        total += i
    return total

# Bug: incorrect logic for leap year determination
def is_leap_year(year):
    if year % 4 == 0:  # Missing the century rule
        return True
    else:
        return False

# Bug: reversed comparison operator
def find_minimum(numbers):
    if not numbers:
        return None
    min_value = numbers[0]
    for num in numbers:
        if num > min_value:  # Should be num < min_value
            min_value = num
    return min_value

# Bug: index error when list is empty
def get_last_element(items):
    # Should check if the list is empty
    return items[len(items) - 1]

# Bug: infinite loop
def count_down(start):
    current = start
    while current > 0:
        print(current)
        current += 1  # Should be current -= 1

# Bug: tuple unpacking error
def swap_values(a, b):
    a, b = b, a  # Missing return statement
    
# Bug: indentation error in function
def process_data(data):
    result = []
    for item in data:
        processed = item * 2
    result.append(processed)  # Should be indented to be part of the loop
    return result

# Main execution
if __name__ == "__main__":
    # Test sum function
    print(f"Sum of numbers from 0 to 4: {sum_numbers(5)}")
    
    # Test leap year
    print(f"Is 2000 a leap year? {is_leap_year(2000)}")
    
    # Test minimum finder
    numbers = [5, 2, 8, 1, 9, 3]
    print(f"Minimum value: {find_minimum(numbers)}")
    
    # Test getting last element
    print(f"Last element: {get_last_element(numbers)}")
    
    # Test data processing
    print(f"Processed data: {process_data([1, 2, 3, 4])}") 