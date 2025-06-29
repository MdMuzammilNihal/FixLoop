# Basic Python code with some issues for testing analysis
def calculate_factorial(n):
    if n < 0:
        return "Cannot calculate factorial for negative numbers"
    elif n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n + 1):
            result = result * i
        return result

# Inefficient code with unnecessary variables
def find_max(numbers):
    maximum = numbers[0]
    for num in numbers:
        if num > maximum:
            maximum = num
    return maximum

# Function with style issues
def printMessage(msg):
    print (msg)
    return None

# Code with potential bugs
def divide(a, b):
    return a / b  # No error handling for division by zero

# Main execution
if __name__ == "__main__":
    # Use predefined input instead of waiting for user input
    print("Enter a number: 5")  # Simulate input prompt
    user_input = "5"  # Predefined input
    number = int(user_input)  # No try/except for conversion errors
    
    result = calculate_factorial(number)
    printMessage(f"The factorial of {number} is {result}")
    
    numbers = [5, 2, 8, 1, 9, 3]
    max_num = find_max(numbers)
    printMessage(f"The maximum number is {max_num}")
    
    # Potential division by zero
    division_result = divide(10, number)
    printMessage(f"10 divided by {number} is {division_result}") 