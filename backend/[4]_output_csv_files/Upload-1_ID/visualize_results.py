import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_column_graphs(filename):
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found in the current directory.")
        return

    # Load the data
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Select only numeric columns (assuming we want to plot numerical data)
    cols_to_plot = df.select_dtypes(include=['number']).columns
    
    if len(cols_to_plot) == 0:
        print("No numeric columns found to plot.")
        # Fallback to all columns if no numeric found
        cols_to_plot = df.columns

    num_plots = len(cols_to_plot)
    print(f"Generating {num_plots} graphs...")

    # Create subplots: one row for each column
    fig = make_subplots(
        rows=num_plots, 
        cols=1, 
        subplot_titles=cols_to_plot,
        vertical_spacing=0.05 / max(1, (num_plots / 2)) # Adjust spacing dynamically
    )

    # Add a line graph for each column
    for i, col in enumerate(cols_to_plot):
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df[col], 
                mode='lines', 
                name=col
            ),
            row=i + 1, 
            col=1
        )

    # Update the layout to use the white theme and ensure it's tall enough
    fig.update_layout(
        template='plotly_white',
        height=300 * num_plots,  # Set height: 300px per graph
        title_text=f"Visualization of {filename}",
        showlegend=False  # Hide legend to reduce clutter
    )

    # Show the graph
    fig.show()

if __name__ == "__main__":
    create_column_graphs('9_layer_output.csv')
