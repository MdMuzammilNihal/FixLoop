"""
Test file for advanced data visualization capabilities.
This file contains multiple types of visualization libraries and plotting scenarios
to test how well the AI assistant handles visualization code and provides effective solutions.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import random
import math
from typing import List, Dict, Tuple, Optional

# ====== Basic Matplotlib Plotting Functions ======

def test_basic_line_plot():
    """Create a basic line plot with matplotlib"""
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Sin(x)')
    plt.title('Basic Sine Wave Plot')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.legend()
    plt.grid(True)
    plt.savefig('basic_line_plot.png')
    print("Created basic line plot: basic_line_plot.png")

def test_multiple_line_plot():
    """Create a plot with multiple lines"""
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.tan(x)
    
    plt.figure(figsize=(12, 8))
    plt.plot(x, y1, 'b-', label='Sin(x)')
    plt.plot(x, y2, 'r-', label='Cos(x)')
    plt.plot(x, y3, 'g-', label='Tan(x)')
    plt.title('Multiple Trigonometric Functions')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.legend()
    plt.grid(True)
    # Add y-axis limits to prevent tan(x) from dominating the plot
    plt.ylim(-3, 3)
    plt.savefig('multiple_line_plot.png')
    print("Created multiple line plot: multiple_line_plot.png")

def test_scatter_plot():
    """Create a scatter plot with varied point sizes and colors"""
    np.random.seed(42)
    x = np.random.rand(50)
    y = np.random.rand(50)
    colors = np.random.rand(50)
    sizes = 1000 * np.random.rand(50)
    
    plt.figure(figsize=(10, 8))
    plt.scatter(x, y, c=colors, s=sizes, alpha=0.7, cmap='viridis')
    plt.colorbar(label='Color Value')
    plt.title('Scatter Plot with Varying Point Sizes and Colors')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.savefig('scatter_plot.png')
    print("Created scatter plot: scatter_plot.png")

def test_bar_chart():
    """Create a bar chart"""
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = [23, 45, 56, 78, 32]
    
    plt.figure(figsize=(10, 6))
    plt.bar(categories, values, color='skyblue')
    plt.title('Simple Bar Chart')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('bar_chart.png')
    print("Created bar chart: bar_chart.png")

def test_histogram():
    """Create a histogram"""
    # Generate random data with a normal distribution
    np.random.seed(42)
    data = np.random.normal(0, 1, 1000)
    
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, alpha=0.7, color='green')
    plt.title('Histogram of Normal Distribution')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.savefig('histogram.png')
    print("Created histogram: histogram.png")

def test_pie_chart():
    """Create a pie chart"""
    labels = ['Category A', 'Category B', 'Category C', 'Category D']
    sizes = [15, 30, 45, 10]
    explode = (0, 0.1, 0, 0)  # Make the second slice stand out
    
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Pie Chart Example')
    plt.savefig('pie_chart.png')
    print("Created pie chart: pie_chart.png")

# ====== Advanced Plotting Functions ======

def test_subplots():
    """Create a figure with multiple subplots"""
    plt.figure(figsize=(12, 10))
    
    # 2x2 grid of subplots
    plt.subplot(2, 2, 1)  # row, column, index
    x = np.linspace(0, 10, 100)
    plt.plot(x, np.sin(x))
    plt.title('Sine')
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot(x, np.cos(x), 'r-')
    plt.title('Cosine')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(x, np.sin(x) + np.cos(x), 'g-')
    plt.title('Sine + Cosine')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    plt.plot(x, np.sin(x) * np.cos(x), 'm-')
    plt.title('Sine * Cosine')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('subplots.png')
    print("Created subplot figure: subplots.png")

def test_3d_plot():
    """Create a 3D surface plot"""
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create data for 3D plot
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))
    
    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
    
    # Add labels and colorbar
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('3D Surface Plot')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    plt.savefig('3d_plot.png')
    print("Created 3D plot: 3d_plot.png")

def test_contour_plot():
    """Create a contour plot"""
    # Create data for contour plot
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    
    plt.figure(figsize=(10, 8))
    contour = plt.contourf(X, Y, Z, 20, cmap='RdGy')
    plt.colorbar(contour, label='Z Value')
    plt.title('Contour Plot')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.savefig('contour_plot.png')
    print("Created contour plot: contour_plot.png")

def test_heatmap():
    """Create a heatmap using numpy and matplotlib"""
    # Generate some random data
    np.random.seed(42)
    data = np.random.rand(10, 12)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(data, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Value')
    plt.title('Heat Map')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.savefig('heatmap.png')
    print("Created heatmap: heatmap.png")

# ====== Pandas Visualization ======

def test_pandas_plotting():
    """Test Pandas built-in plotting capabilities"""
    # Create a DataFrame with some example data
    dates = pd.date_range('20230101', periods=100)
    df = pd.DataFrame({
        'A': np.cumsum(np.random.randn(100)),
        'B': np.cumsum(np.random.randn(100) * 0.5),
        'C': np.cumsum(np.random.randn(100) * 0.1),
        'D': np.cumsum(np.random.randn(100) * 2)
    }, index=dates)
    
    # Line plot
    ax = df.plot(figsize=(12, 6))
    ax.set_title('Pandas Line Plot')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    plt.savefig('pandas_line_plot.png')
    print("Created pandas line plot: pandas_line_plot.png")
    
    # Histogram of all columns
    ax = df.hist(figsize=(12, 8), bins=20)
    plt.tight_layout()
    plt.savefig('pandas_histogram.png')
    print("Created pandas histogram: pandas_histogram.png")
    
    # Box plot
    ax = df.boxplot(figsize=(10, 6))
    plt.title('Box Plot of DataFrame Columns')
    plt.savefig('pandas_box_plot.png')
    print("Created pandas box plot: pandas_box_plot.png")
    
    # Scatter matrix
    from pandas.plotting import scatter_matrix
    scatter_matrix(df, alpha=0.8, figsize=(12, 12), diagonal='kde')
    plt.tight_layout()
    plt.savefig('pandas_scatter_matrix.png')
    print("Created pandas scatter matrix: pandas_scatter_matrix.png")

# ====== Missing import test ======

def test_missing_import():
    """Test with a visualization library that might not be installed"""
    try:
        # Import seaborn (may not be installed)
        import seaborn as sns
        print("Seaborn is installed, creating a seaborn plot...")
        
        # Create some data
        np.random.seed(42)
        tips = pd.DataFrame({
            'total_bill': np.random.uniform(10, 50, 100),
            'tip': np.random.uniform(1, 10, 100),
            'sex': np.random.choice(['Male', 'Female'], 100),
            'time': np.random.choice(['Lunch', 'Dinner'], 100)
        })
        
        # Create a seaborn plot
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='total_bill', y='tip', hue='sex', style='time', data=tips)
        plt.title('Seaborn Scatter Plot')
        plt.savefig('seaborn_plot.png')
        print("Created seaborn plot: seaborn_plot.png")
        
    except ImportError:
        print("Seaborn is not installed. This is expected as we're testing handling of missing imports.")
        print("Suggestion: Install seaborn with 'pip install seaborn'")

# ====== Main execution ======

def run_all_visualization_tests():
    """Run all visualization tests"""
    
    print("\n===== Testing Basic Matplotlib Plots =====")
    test_basic_line_plot()
    test_multiple_line_plot()
    test_scatter_plot()
    test_bar_chart()
    test_histogram()
    test_pie_chart()
    
    print("\n===== Testing Advanced Plots =====")
    test_subplots()
    try:
        test_3d_plot()
    except Exception as e:
        print(f"Error in 3D plot: {e}")
    test_contour_plot()
    test_heatmap()
    
    print("\n===== Testing Pandas Visualization =====")
    try:
        test_pandas_plotting()
    except Exception as e:
        print(f"Error in pandas plotting: {e}")
    
    print("\n===== Testing Missing Import Handling =====")
    test_missing_import()

if __name__ == "__main__":
    print("Running Advanced Visualization Tests")
    run_all_visualization_tests()
    print("All visualization tests completed") 