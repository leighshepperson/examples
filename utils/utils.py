import itertools

import pandas as pd
import plotly.express as px

from typing import Union, Dict, Tuple

from plotly.subplots import make_subplots

def extract_subplots_info_v5(fig):
    subplots_info = []
    
    # Identify unique facet rows and columns from the traces' xaxis and yaxis attributes
    facet_rows = sorted({trace.yaxis for trace in fig.data})
    facet_cols = sorted({trace.xaxis for trace in fig.data})

    for i, row in enumerate(facet_rows):
        for j, col in enumerate(facet_cols):
            # Count the number of traces that belong to the current combination of facet row and column
            num_traces = sum(1 for trace in fig.data if trace.yaxis == row and trace.xaxis == col)
            
            # Only append subplots with traces
            if num_traces > 0:
                subplots_info.append({
                    'facet_row': i,
                    'facet_col': j,
                    'num_traces': num_traces
                })
    
    return subplots_info


def format_currency(value: Union[int, float]) -> str:
    if abs(value) < 1_000:
        return f"{value:.2f}"
    elif abs(value) < 1_000_000:
        return f"{value / 1_000:.2f}K"
    elif abs(value) < 1_000_000_000:
        return f"{value / 1_000_000:.2f}M"
    else:
        return f"{value / 1_000_000_000:.2f}B"


def create_color_map(df: pd.DataFrame, color: str) -> Dict[str, str]:
    unique_names = df[color].unique()

    base_colors = px.colors.qualitative.Plotly
    repeated_colors = list(
        itertools.islice(itertools.cycle(base_colors), len(unique_names))
    )

    return dict(zip(unique_names, repeated_colors))


def compute_difference(
    value1: Union[int, float], value2: Union[int, float]
) -> Tuple[Union[int, float], Union[int, float]]:
    diff_percentage = -((value1 - value2) / value2) * 100
    diff_value = -(value1 - value2)
    return diff_percentage, diff_value


def create_facet_figure(data, facet_row):
    """
    Creates a faceted figure based on a facet_row.

    Parameters:
    - data: DataFrame
        The data to plot.
    - facet_row: str
        The name of the column by which to create facets.

    Returns:
    - fig: plotly.graph_objects.Figure
        The faceted figure.
    - facet_values: dict
        A dictionary mapping each unique value in the facet_row column to its subplot row number.
    """

    unique_values = data[facet_row].unique()
    fig = make_subplots(
        rows=len(unique_values), cols=1, subplot_titles=unique_values.tolist()
    )
    facet_values = dict(zip(unique_values, range(1, len(unique_values) + 1)))

    return fig, facet_values
