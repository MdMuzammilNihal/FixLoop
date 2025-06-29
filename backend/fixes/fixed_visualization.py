# Add code to save visualizations automatically based on detected libraries
vis_save_code = """
# Auto-added visualization saving code
try:
    import os
    import inspect
    import sys
    import time
    
    VIS_PATTERNS = {
        'matplotlib': ['.plot(', '.bar(', '.scatter(', '.hist(', '.imshow(', '.pie(', '.boxplot(', '.figure(', '.subplot(', 'plt.show('],
        'seaborn': ['sns.', 'seaborn.', '.heatmap(', '.pairplot(', '.catplot(', '.violinplot(', '.jointplot('],
        'plotly': ['px.', 'plotly.', 'go.', '.add_trace(', '.update_layout(', '.show()'],
        'bokeh': ['.figure(', '.line(', 'bokeh.plotting', '.circle(', '.vbar(', '.hbar('],
        'altair': ['alt.', 'altair.', '.encode(', '.mark_', '.properties(', '.interactive()'],
        'pygal': ['pygal.', '.add(', '.render(', '.render_to_file('],
        'holoviews': ['hv.', 'holoviews.', '.opts('],
        'networkx': ['nx.draw', 'networkx.draw']
    }
    
    def detect_visualization_library_usage(code_str):
        detected = set()
        for lib, patterns in VIS_PATTERNS.items():
            if any(pattern in code_str for pattern in patterns):
                detected.add(lib)
        return detected
    
    # Check the code for visualization patterns
    vis_code = inspect.getsource(inspect.currentframe().f_globals['__main__'])
    detected_vis_libs = detect_visualization_library_usage(vis_code)
    
    if detected_vis_libs:
        timestamp = int(time.time())
        print(f"\\n[INFO] Detected visualization libraries: {', '.join(detected_vis_libs)}")
        
        # Create a directory for visualizations if it doesn't exist
        vis_dir = 'visualizations'
        if not os.path.exists(vis_dir):
            os.makedirs(vis_dir)
            print(f"[INFO] Created directory '{vis_dir}' for saving visualizations")
    
    # Save matplotlib/seaborn plots
    if 'matplotlib' in detected_vis_libs or 'seaborn' in detected_vis_libs:
        try:
            import matplotlib.pyplot as plt
            if plt.get_fignums():
                print("\\n[INFO] Saving matplotlib/seaborn plots...")
                for i, fig_num in enumerate(plt.get_fignums()):
                    fig = plt.figure(fig_num)
                    filename = f"{vis_dir}/plot_mpl_{timestamp}_{i+1}.png"
                    fig.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"[INFO] Plot saved to {filename}")
        except Exception as e:
            print(f"[INFO] Matplotlib save: {str(e)}")
    
    # Save plotly plots
    if 'plotly' in detected_vis_libs:
        try:
            import plotly
            import plotly.io as pio
            
            # Check if any plotly figures exist in globals
            found_plotly_figs = False
            for var_name, var_val in list(globals().items()):
                if str(type(var_val)).find('plotly.graph_objs') >= 0:
                    found_plotly_figs = True
                    print(f"\\n[INFO] Saving plotly figure {var_name}...")
                    filename = f"{vis_dir}/plot_plotly_{timestamp}_{var_name}.png"
                    pio.write_image(var_val, filename)
                    
                    # Also save interactive HTML version
                    html_filename = f"{vis_dir}/plot_plotly_{timestamp}_{var_name}.html"
                    pio.write_html(var_val, html_filename)
                    print(f"[INFO] Plot saved to {filename} and {html_filename}")
            
            if not found_plotly_figs:
                # Look for figures created with plotly express
                for var_name, var_val in list(globals().items()):
                    if str(type(var_val)).find('plotly.express') >= 0 or str(type(var_val)).find('plotly_express') >= 0:
                        print(f"\\n[INFO] Saving plotly express figure {var_name}...")
                        filename = f"{vis_dir}/plot_plotly_{timestamp}_{var_name}.png"
                        pio.write_image(var_val, filename)
                        
                        # Also save interactive HTML version
                        html_filename = f"{vis_dir}/plot_plotly_{timestamp}_{var_name}.html"
                        pio.write_html(var_val, html_filename)
                        print(f"[INFO] Plot saved to {filename} and {html_filename}")
        except Exception as e:
            print(f"[INFO] Plotly save: {str(e)}")
    
    # Save bokeh plots
    if 'bokeh' in detected_vis_libs:
        try:
            from bokeh.io import export_png, save, output_file
            import bokeh.plotting
            
            # Get all bokeh figures from globals
            for var_name, var_val in list(globals().items()):
                if str(type(var_val)).find('bokeh.plotting.figure.Figure') >= 0:
                    print(f"\\n[INFO] Saving bokeh figure {var_name}...")
                    # Save as PNG
                    try:
                        filename = f"{vis_dir}/plot_bokeh_{timestamp}_{var_name}.png"
                        export_png(var_val, filename=filename)
                        print(f"[INFO] Plot saved to {filename}")
                    except:
                        print("[INFO] Couldn't save bokeh plot as PNG, trying HTML...")
                    
                    # Save as HTML
                    html_filename = f"{vis_dir}/plot_bokeh_{timestamp}_{var_name}.html"
                    output_file(html_filename)
                    save(var_val)
                    print(f"[INFO] Plot saved to {html_filename}")
        except Exception as e:
            print(f"[INFO] Bokeh save: {str(e)}")
            
    # Save altair plots
    if 'altair' in detected_vis_libs:
        try:
            import altair as alt
            
            # Get all altair charts from globals
            for var_name, var_val in list(globals().items()):
                if str(type(var_val)).find('altair.vegalite') >= 0:
                    print(f"\\n[INFO] Saving altair chart {var_name}...")
                    # Save as PNG if possible
                    try:
                        filename = f"{vis_dir}/plot_altair_{timestamp}_{var_name}.png"
                        var_val.save(filename)
                        print(f"[INFO] Plot saved to {filename}")
                    except:
                        print("[INFO] Couldn't save altair plot as PNG, trying HTML...")
                    
                    # Save as HTML
                    html_filename = f"{vis_dir}/plot_altair_{timestamp}_{var_name}.html"
                    var_val.save(html_filename)
                    print(f"[INFO] Plot saved to {html_filename}")
        except Exception as e:
            print(f"[INFO] Altair save: {str(e)}")
    
    # Save pygal charts if detected
    if 'pygal' in detected_vis_libs:
        try:
            # Get all pygal charts from globals
            for var_name, var_val in list(globals().items()):
                if str(type(var_val)).find('pygal.') >= 0:
                    print(f"\\n[INFO] Saving pygal chart {var_name}...")
                    # Save as SVG
                    svg_filename = f"{vis_dir}/plot_pygal_{timestamp}_{var_name}.svg"
                    var_val.render_to_file(svg_filename)
                    # Also save as PNG if rendering is available
                    try:
                        png_filename = f"{vis_dir}/plot_pygal_{timestamp}_{var_name}.png"
                        var_val.render_to_png(png_filename)
                        print(f"[INFO] Plot saved to {svg_filename} and {png_filename}")
                    except:
                        print(f"[INFO] Plot saved to {svg_filename}")
        except Exception as e:
            print(f"[INFO] Pygal save: {str(e)}")
    
    # Save holoviews plots if detected
    if 'holoviews' in detected_vis_libs:
        try:
            import holoviews as hv
            
            # Get all holoviews objects from globals
            for var_name, var_val in list(globals().items()):
                if str(type(var_val)).find('holoviews.') >= 0:
                    print(f"\\n[INFO] Saving holoviews visualization {var_name}...")
                    filename = f"{vis_dir}/plot_hv_{timestamp}_{var_name}.png"
                    hv.save(var_val, filename)
                    print(f"[INFO] Plot saved to {filename}")
        except Exception as e:
            print(f"[INFO] Holoviews save: {str(e)}")
    
    # Save networkx plots if detected
    if 'networkx' in detected_vis_libs:
        try:
            import matplotlib.pyplot as plt
            
            # Look for matplotlib figures that might contain networkx plots
            if plt.get_fignums():
                print("\\n[INFO] Saving potential networkx plots...")
                for i, fig_num in enumerate(plt.get_fignums()):
                    fig = plt.figure(fig_num)
                    filename = f"{vis_dir}/plot_networkx_{timestamp}_{i+1}.png"
                    fig.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"[INFO] Plot saved to {filename}")
        except Exception as e:
            print(f"[INFO] Networkx save: {str(e)}")
            
except Exception as e:
    print(f"[INFO] Visualization save operations: {str(e)}")
"""

if detected_vis_libs and has_visualization_code:
    modified_code += "\n" + vis_save_code 