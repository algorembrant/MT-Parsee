import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots
import os

def format_title(text):
    """
    Formats the column name for the graph title.
    """
    words = text.split('_')
    
    lower_words = [w.lower() for w in words]
    if 'rolling' in lower_words:
        try:
            index = lower_words.index('rolling')
            words = words[index + 1:]
        except ValueError:
            pass

    clean_words = []
    seen = set()

    for word in words:
        if word.lower() not in seen and word.strip() != "" and word.lower() != 'rolling':
            seen.add(word.lower())
            if word.isupper():
                clean_words.append(word)
            else:
                clean_words.append(word.capitalize())

    return " ".join(clean_words)

def create_column_graphs(filename):
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        return

    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    cols_to_plot = df.select_dtypes(include=['number']).columns
    
    if len(cols_to_plot) == 0:
        print("No numeric columns found to plot.")
        cols_to_plot = df.columns

    formatted_titles = [format_title(col) for col in cols_to_plot]
    num_plots = len(cols_to_plot)
    print(f"Generating {num_plots} graphs...")

    colors = pc.qualitative.Plotly 

    plot_titles = []
    for t in formatted_titles:
        plot_titles.append(t)
        plot_titles.append("") 

    fig = make_subplots(
        rows=num_plots, 
        cols=2, 
        subplot_titles=plot_titles,
        column_widths=[0.75, 0.25], 
        shared_yaxes=False, 
        horizontal_spacing=0.03, 
        vertical_spacing=0.05 / max(1, (num_plots / 2))
    )

    for i, col in enumerate(cols_to_plot):
        row_num = i + 1
        current_color = colors[i % len(colors)]

        y_min = df[col].min()
        y_max = df[col].max()
        y_range = y_max - y_min
        
        if y_range == 0:
            bin_size = 1
        else:
            bin_size = y_range / 100.0

        # 1. Line Graph (Left)
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df[col], 
                mode='lines', 
                name=formatted_titles[i],
                line=dict(color=current_color),
                legendgroup=f"group_{i}"
            ),
            row=row_num, 
            col=1
        )

        # 2. Distribution (Right)
        fig.add_trace(
            go.Histogram(
                y=df[col], 
                orientation='h', 
                name='Dist',
                marker=dict(color=current_color),
                showlegend=False,
                histnorm='percent',
                hoverinfo='y+x',
                ybins=dict(
                    start=y_min,
                    size=bin_size
                )
            ),
            row=row_num, 
            col=2
        )

        fig.update_yaxes(
            title_text=None,
            showticklabels=True, 
            side='right',
            row=row_num, 
            col=2
        )
        
        fig.update_xaxes(
            title_text="%", 
            row=row_num, 
            col=2
        )

    # Calculate total height based on number of plots
    total_height = 300 * num_plots
    
    fig.update_layout(
        template='plotly_white',
        height=total_height,
        width=1200, # Set a fixed width for the exported file
        title_text=f"Visualization of {filename}",
        showlegend=False,
        bargap=0.05
    )

    # --- EXPORT SECTION ---
    base_name = os.path.splitext(filename)[0]
    
    # Save as PNG
    png_filename = f"{base_name}_graphs.png"
    print(f"Saving {png_filename}...")
    fig.write_image(png_filename)

    # Save as PDF
    pdf_filename = f"{base_name}_graphs.pdf"
    print(f"Saving {pdf_filename}...")
    fig.write_image(pdf_filename)
    
    print("Done!")
    # fig.show() # Optional: Comment out if you only want files, not the browser window

if __name__ == "__main__":
    create_column_graphs('9_layer_output.csv')