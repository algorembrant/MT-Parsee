import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
from plotly.subplots import make_subplots
import os

def format_title(text):
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
        cols_to_plot = df.columns

    formatted_titles = [format_title(col) for col in cols_to_plot]
    num_plots = len(cols_to_plot)
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
        horizontal_spacing=0.04, # Increased slightly for label clearance
        vertical_spacing=0.05 / max(1, (num_plots / 2))
    )

    for i, col in enumerate(cols_to_plot):
        row_num = i + 1
        current_color = colors[i % len(colors)]

        # Dynamic 1% Binning logic
        y_min, y_max = df[col].min(), df[col].max()
        y_range = y_max - y_min
        bin_size = (y_range / 100.0) if y_range != 0 else 1

        # 1. Line Graph (Left plane)
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[col], 
                mode='lines', name=formatted_titles[i],
                line=dict(color=current_color)
            ),
            row=row_num, col=1
        )

        # 2. Histogram (Right plane)
        fig.add_trace(
            go.Histogram(
                y=df[col], orientation='h', 
                marker=dict(color=current_color),
                histnorm='percent',
                ybins=dict(start=y_min, size=bin_size),
                showlegend=False
            ),
            row=row_num, col=2
        )

        # Configure Right Y-Axis Plane
        fig.update_yaxes(side='right', showticklabels=True, row=row_num, col=2)
        fig.update_xaxes(title_text="%", row=row_num, col=2)

    total_height = 400 * num_plots # Increased per-plot height for better clarity
    fig.update_layout(
        template='plotly_white',
        height=total_height,
        width=1400,
        title_text=f"Analysis: {filename}",
        showlegend=False,
        bargap=0.05
    )

    # --- OUTPUTS ---
    base_name = os.path.splitext(filename)[0]
    
    # 1. Save PNG (High Resolution)
    print(f"Exporting PNG...")
    fig.write_image(f"{base_name}.png", scale=2) 
    
    # 2. Save PDF
    print(f"Exporting PDF...")
    fig.write_image(f"{base_name}.pdf")

    # 3. Open Interactive Localhost
    print(f"Launching interactive localhost...")
    fig.show()

if __name__ == "__main__":
    create_column_graphs('9_layer_output.csv')