"""
Test file for advanced optimization capabilities.
This file contains complex algorithms and patterns that could be significantly optimized.
"""
import time
import random
import math
from typing import List, Dict, Tuple

# Inefficient recursive Fibonacci implementation
def fibonacci_recursive(n: int) -> int:
    """Calculate Fibonacci number using inefficient recursive approach"""
    if n <= 1:
        return n
    else:
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

# Inefficient string operations
def build_large_string(n: int) -> str:
    """Build a large string using inefficient concatenation"""
    result = ""
    for i in range(n):
        result = result + str(i) + "-"
    return result

# Inefficient nested loops with redundant calculations
def matrix_operations(matrix: List[List[int]]) -> Dict[str, List[int]]:
    """Perform operations on a matrix with inefficient nested loops"""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    row_sums = []
    col_sums = []
    
    # Calculate row sums inefficiently
    for i in range(rows):
        row_sum = 0
        for j in range(cols):
            row_sum += matrix[i][j]
        row_sums.append(row_sum)
    
    # Calculate column sums inefficiently
    for j in range(cols):
        col_sum = 0
        for i in range(rows):
            col_sum += matrix[i][j]
        col_sums.append(col_sum)
    
    # Find max value in each row inefficiently
    row_maxes = []
    for i in range(rows):
        row_max = float('-inf')
        for j in range(cols):
            if matrix[i][j] > row_max:
                row_max = matrix[i][j]
        row_maxes.append(row_max)
    
    return {
        "row_sums": row_sums,
        "col_sums": col_sums,
        "row_maxes": row_maxes
    }

# Inefficient sorting algorithm (bubble sort)
def bubble_sort(arr: List[int]) -> List[int]:
    """Sort an array using inefficient bubble sort"""
    n = len(arr)
    # Create a deep copy to avoid modifying the original
    result = arr.copy()
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                # Swap elements
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result

# Inefficient data processing with redundant computations
def process_data(data: List[Dict[str, int]]) -> Dict[str, float]:
    """Process data with inefficient approaches and redundant computations"""
    # Calculate statistics inefficiently
    total_a = 0
    total_b = 0
    total_c = 0
    count = len(data)
    
    for item in data:
        total_a += item.get('a', 0)
        total_b += item.get('b', 0)
        total_c += item.get('c', 0)
    
    avg_a = total_a / count if count > 0 else 0
    avg_b = total_b / count if count > 0 else 0
    avg_c = total_c / count if count > 0 else 0
    
    # Calculate standard deviations inefficiently
    sum_squared_diff_a = 0
    sum_squared_diff_b = 0
    sum_squared_diff_c = 0
    
    for item in data:
        sum_squared_diff_a += (item.get('a', 0) - avg_a) ** 2
        sum_squared_diff_b += (item.get('b', 0) - avg_b) ** 2
        sum_squared_diff_c += (item.get('c', 0) - avg_c) ** 2
    
    std_a = math.sqrt(sum_squared_diff_a / count) if count > 0 else 0
    std_b = math.sqrt(sum_squared_diff_b / count) if count > 0 else 0
    std_c = math.sqrt(sum_squared_diff_c / count) if count > 0 else 0
    
    # Calculate correlations inefficiently
    ab_product_sum = 0
    ac_product_sum = 0
    bc_product_sum = 0
    
    for item in data:
        a_val = item.get('a', 0)
        b_val = item.get('b', 0)
        c_val = item.get('c', 0)
        
        ab_product_sum += (a_val - avg_a) * (b_val - avg_b)
        ac_product_sum += (a_val - avg_a) * (c_val - avg_c)
        bc_product_sum += (b_val - avg_b) * (c_val - avg_c)
    
    corr_ab = ab_product_sum / (std_a * std_b * count) if std_a > 0 and std_b > 0 and count > 0 else 0
    corr_ac = ac_product_sum / (std_a * std_c * count) if std_a > 0 and std_c > 0 and count > 0 else 0
    corr_bc = bc_product_sum / (std_b * std_c * count) if std_b > 0 and std_c > 0 and count > 0 else 0
    
    return {
        "avg_a": avg_a,
        "avg_b": avg_b,
        "avg_c": avg_c,
        "std_a": std_a,
        "std_b": std_b,
        "std_c": std_c,
        "corr_ab": corr_ab,
        "corr_ac": corr_ac,
        "corr_bc": corr_bc
    }

# Inefficient text processing
def count_word_frequencies(text: str) -> Dict[str, int]:
    """Count word frequencies in text using inefficient methods"""
    # Split by whitespace and remove punctuation inefficiently
    words = []
    for word in text.split():
        clean_word = ""
        for char in word:
            if char.isalnum():
                clean_word += char.lower()
        if clean_word:
            words.append(clean_word)
    
    # Count frequencies inefficiently
    frequencies = {}
    for word in words:
        if word in frequencies:
            frequencies[word] += 1
        else:
            frequencies[word] = 1
    
    return frequencies

# Inefficient prime number checker
def is_prime(n: int) -> bool:
    """Check if a number is prime using a very inefficient algorithm"""
    if n <= 1:
        return False
    
    # Check every number from 2 to n-1
    for i in range(2, n):
        if n % i == 0:
            return False
    
    return True

# Main function to demonstrate the inefficient code
def run_optimization_tests():
    # Test Fibonacci
    print("Testing Fibonacci calculation...")
    start = time.time()
    fib_result = fibonacci_recursive(25)
    end = time.time()
    print(f"Fibonacci(25) = {fib_result}, took {end - start:.4f} seconds")
    
    # Test string building
    print("\nTesting string building...")
    start = time.time()
    string_result = build_large_string(10000)
    end = time.time()
    print(f"Built string of length {len(string_result)}, took {end - start:.4f} seconds")
    
    # Test matrix operations
    print("\nTesting matrix operations...")
    matrix = [[random.randint(1, 100) for _ in range(50)] for _ in range(50)]
    start = time.time()
    matrix_result = matrix_operations(matrix)
    end = time.time()
    print(f"Matrix operations completed, took {end - start:.4f} seconds")
    
    # Test sorting
    print("\nTesting sorting algorithm...")
    array = [random.randint(1, 1000) for _ in range(1000)]
    start = time.time()
    sorted_result = bubble_sort(array)
    end = time.time()
    print(f"Sorted {len(array)} elements, took {end - start:.4f} seconds")
    
    # Test data processing
    print("\nTesting data processing...")
    data = [{'a': random.randint(1, 100), 'b': random.randint(1, 100), 'c': random.randint(1, 100)} 
            for _ in range(1000)]
    start = time.time()
    stats_result = process_data(data)
    end = time.time()
    print(f"Processed {len(data)} data points, took {end - start:.4f} seconds")
    
    # Test word frequency counting
    print("\nTesting word frequency counting...")
    text = "This is a sample text. This text contains repeated words. The words in this text will be counted."
    text = text * 100  # Make it longer
    start = time.time()
    freq_result = count_word_frequencies(text)
    end = time.time()
    print(f"Counted frequencies in text of length {len(text)}, took {end - start:.4f} seconds")
    
    # Test prime number checking
    print("\nTesting prime number checking...")
    numbers = [random.randint(1000, 10000) for _ in range(10)]
    for num in numbers[:3]:  # Only show a few for brevity
        start = time.time()
        is_prime_result = is_prime(num)
        end = time.time()
        print(f"is_prime({num}) = {is_prime_result}, took {end - start:.4f} seconds")

if __name__ == "__main__":
    print("Running Advanced Optimization Tests")
    run_optimization_tests()
    print("All optimization tests completed") 