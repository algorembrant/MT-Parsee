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

    # CHANGED: shared_yaxes=False allows us to position the Hist Y-axis on the right independently
    fig = make_subplots(
        rows=num_plots, 
        cols=2, 
        subplot_titles=plot_titles,
        column_widths=[0.75, 0.25], 
        shared_yaxes=False,  # <--- CHANGED: False to allow separate axes (Left & Right)
        horizontal_spacing=0.03, 
        vertical_spacing=0.05 / max(1, (num_plots / 2))
    )

    for i, col in enumerate(cols_to_plot):
        row_num = i + 1
        current_color = colors[i % len(colors)]

        # Calculate dynamic bin settings (1% of the full range)
        y_min = df[col].min()
        y_max = df[col].max()
        y_range = y_max - y_min
        
        # Avoid division by zero if column has constant value
        if y_range == 0:
            bin_size = 1
        else:
            bin_size = y_range / 100.0  # <--- 1% Bin Size

        # 1. Line Graph (Left Axis)
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

        # 2. Distribution / Histogram (Right Axis)
        fig.add_trace(
            go.Histogram(
                y=df[col], 
                orientation='h', 
                name='Dist',
                marker=dict(color=current_color),
                showlegend=False,
                histnorm='percent',  # Normalized to percentage
                hoverinfo='y+x',
                ybins=dict(          # <--- APPLIED HERE: Dynamic 1% binning
                    start=y_min,
                    size=bin_size
                )
            ),
            row=row_num, 
            col=2
        )

        # Update Hist Y-axis to be on the Right
        fig.update_yaxes(
            title_text=None,
            showticklabels=True, 
            side='right', # <--- Puts the axis numbers on the right
            row=row_num, 
            col=2
        )
        
        # Link the range of the Hist axis to the Line axis so they align visually
        # (Optional: ensures that if one auto-scales, they stay relatively similar, 
        # though explicit 'matches' is complex with independent sides. 
        # Since data is identical, default auto-range usually works well.)
        
        # X-axis label for Histogram
        fig.update_xaxes(
            title_text="%", 
            row=row_num, 
            col=2
        )

    fig.update_layout(
        template='plotly_white',
        height=300 * num_plots,
        title_text=f"", #no tittle but just edit this part
        showlegend=False,
        bargap=0.05
    )

    fig.show()

if __name__ == "__main__":
    create_column_graphs('9_layer_output.csv')