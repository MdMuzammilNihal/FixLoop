# Inefficient Python code to test optimization capabilities

# Inefficient string concatenation
def build_long_string(n):
    result = ""
    for i in range(n):
        result = result + str(i)
    return result

# Inefficient list manipulation with repeated operations
def merge_and_sort_lists(list1, list2):
    merged = []
    for item in list1:
        merged.append(item)
    for item in list2:
        merged.append(item)
    
    # Bubble sort implementation
    for i in range(len(merged)):
        for j in range(len(merged) - 1):
            if merged[j] > merged[j + 1]:
                merged[j], merged[j + 1] = merged[j + 1], merged[j]
    
    return merged

# Inefficient Fibonacci implementation with redundant calculations
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Inefficient prime number check
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

# Main execution
if __name__ == "__main__":
    # Test string concatenation
    long_string = build_long_string(1000)
    print(f"String length: {len(long_string)}")
    
    # Test list operations
    list1 = [5, 2, 8, 1, 9, 3]
    list2 = [7, 4, 6, 0]
    sorted_list = merge_and_sort_lists(list1, list2)
    print(f"Sorted list: {sorted_list}")
    
    # Test Fibonacci (limited to small numbers due to inefficiency)
    fib_result = fibonacci(10)
    print(f"Fibonacci of 10: {fib_result}")
    
    # Test prime numbers
    primes = [n for n in range(1, 100) if is_prime(n)]
    print(f"Prime numbers below 100: {primes}") 