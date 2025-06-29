# Data visualization test with matplotlib

import numpy as np
import matplotlib.pyplot as plt

# Generate data for plotting
def generate_data(n=100):
    x = np.linspace(0, 10, n)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.exp(-0.1*x) * np.sin(x)
    return x, y1, y2, y3

# Create a simple line plot
def create_line_plot(x, y, title="Line Plot"):
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.savefig('line_plot.png')
    plt.close()
    return 'line_plot.png'

# Create a scatter plot
def create_scatter_plot(x, y, title="Scatter Plot"):
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.6, s=50, c=y, cmap='viridis')
    plt.colorbar(label='Y values')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.savefig('scatter_plot.png')
    plt.close()
    return 'scatter_plot.png'

# Create a multi-line plot with legend
def create_multi_line_plot(x, y1, y2, y3, title="Multiple Lines Plot"):
    plt.figure(figsize=(10, 6))
    plt.plot(x, y1, 'b-', linewidth=2, label='sin(x)')
    plt.plot(x, y2, 'r-', linewidth=2, label='cos(x)')
    plt.plot(x, y3, 'g-', linewidth=2, label='exp(-0.1x)sin(x)')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid(True)
    plt.savefig('multi_line_plot.png')
    plt.close()
    return 'multi_line_plot.png'

# Create a subplots figure
def create_subplots(x, y1, y2, y3, title="Subplots Example"):
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle(title, fontsize=16)
    
    axs[0].plot(x, y1, 'b-')
    axs[0].set_title('Sine Wave')
    axs[0].set_ylabel('sin(x)')
    axs[0].grid(True)
    
    axs[1].plot(x, y2, 'r-')
    axs[1].set_title('Cosine Wave')
    axs[1].set_ylabel('cos(x)')
    axs[1].grid(True)
    
    axs[2].plot(x, y3, 'g-')
    axs[2].set_title('Damped Sine Wave')
    axs[2].set_xlabel('X-axis')
    axs[2].set_ylabel('exp(-0.1x)sin(x)')
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.savefig('subplots.png')
    plt.close()
    return 'subplots.png'

# Main execution
if __name__ == "__main__":
    # Generate data
    x, y1, y2, y3 = generate_data()
    
    # Create various plots
    line_plot = create_line_plot(x, y1, "Sine Wave")
    scatter_plot = create_scatter_plot(x, y1, "Sine Values Scatter Plot")
    multi_line = create_multi_line_plot(x, y1, y2, y3, "Trigonometric Functions")
    subplots = create_subplots(x, y1, y2, y3, "Waveforms Comparison")
    
    # Print the file paths of the generated plots
    print(f"Generated plots: {line_plot}, {scatter_plot}, {multi_line}, {subplots}") 