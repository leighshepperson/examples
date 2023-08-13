from random import random, uniform

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

data = {
    "X": [11, 23, 33, 49, 50],
    "Y1": [14.5, 20.4, 38.3, 44.2, 53.1],
    "Y2": [15.6, 25.7, 35.8, 45.9, 55.0],
    "x_name": ["planed", "A", "A", "A", "A"],
    "y1_name": ["expected", "B", "B", "B", "B"],
    "y2_name": ["realised", "C", "C", "C", "C"],
    "name": ["foo1", "foo2", "foo3", "foo4", "foo5"],
}


def generate_data(n, scale="billions"):
    # Define scale factor based on scale
    factor = 1e9 if scale == "billions" else 1e6

    # Generate a random base number in the specified scale
    base_number = uniform(0.5 * factor, 1.5 * factor)

    # Generate values in the range of 10% of the base number
    X = [base_number + uniform(-0.1 * base_number, 0.1 * base_number) for _ in range(n)]
    Y1 = [
        base_number + uniform(-0.1 * base_number, 0.1 * base_number) for _ in range(n)
    ]
    Y2 = [
        base_number + uniform(-0.1 * base_number, 0.1 * base_number) for _ in range(n)
    ]

    data = {
        "X": X,
        "Y1": Y1,
        "Y2": Y2,
        "x_name": ["A"] * (n),
        "y1_name": ["B"] * (n),
        "y2_name": ["C"] * (n),
        "name": [f"foo{i + 1}" for i in range(n)],
    }

    return pd.DataFrame(data)


# Test the function
df = generate_data(10, scale="billions")


unique_names = df["name"].unique()
colors = px.colors.qualitative.Plotly[: len(unique_names)]
color_map = dict(zip(unique_names, colors))

fig = go.Figure()


def calculate_color(value, threshold=20):
    normalized = value / threshold
    if normalized > 1:
        normalized = 1
    if normalized < -1:
        normalized = -1
    if normalized > 0:
        return f"rgb(255, {255 * (1 - normalized)}, {255 * (1 - normalized)})"  # Transition to red
    else:
        return f"rgb({255 * (1 + normalized)}, 255, {255 * (1 + normalized)})"  # Transition to green


# Loop through each data point
for index, row in df.iterrows():
    # Calculate percentage differences
    diff_X = -((row["X"] - row["Y2"]) / row["Y2"]) * 100
    diff_Y1 = -((row["Y1"] - row["Y2"]) / row["Y2"]) * 100

    y_start_X = row["Y2"]
    y_end_X = row["X"]
    y_start_Y1 = row["Y2"]
    y_end_Y1 = row["Y1"]

    # Decide color and position for annotations based on difference
    color_X = "green" if diff_X > 0 else "red"
    color_Y1 = "green" if diff_Y1 > 0 else "red"
    y_position_X = y_end_X + 1 if diff_X > 0 else y_end_X - 1
    y_position_Y1 = y_end_Y1 + 1 if diff_Y1 > 0 else y_end_Y1 - 1

    current_color = color_map[row["name"]]

    # Determine if this trace should show in legend
    show_in_legend = row["name"] not in [t["name"] for t in fig.data]

    def format_currency(value):
        if abs(value) < 1_000:
            return f"{value:.2f}"
        elif abs(value) < 1_000_000:
            return f"{value / 1_000:.2f}K"
        elif abs(value) < 1_000_000_000:
            return f"{value / 1_000_000:.2f}M"
        else:
            return f"{value / 1_000_000_000:.2f}B"

    diff_value_X = -(row["X"] - row["Y2"])
    diff_value_Y1 = -(row["Y1"] - row["Y2"])

    hoverinfo = (
        f"<b>{row['name']}</b><br><br>"
        f"Left ({row['x_name']}): {format_currency(row['X'])}<br>"
        f"Right ({row['y1_name']}): {format_currency(row['Y1'])}<br>"
        f"Center ({row['y2_name']}): {format_currency(row['Y2'])}<br>"
        f"Diff X to Y2 (%): {diff_X:.2f}% (Value): {format_currency(diff_value_X)}<br>"
        f"Diff Y1 to Y2 (%): {diff_Y1:.2f}% (Value): {format_currency(diff_value_Y1)}<br>"
    )

    x_start_X = index - 0.1  # Adjusted from -0.25
    x_end_X = index  # Adjusted from -0.15
    x_start_Y1 = index  # Adjusted from +0.15
    x_end_Y1 = index + 0.1  # Adjusted from +0.25

    fig.add_trace(
        go.Scatter(
            x=[x_start_X, x_end_X, x_end_X, x_start_X],
            y=[y_start_X, y_start_X, y_end_X, y_end_X],
            fill="toself",
            fillcolor=color_X,
            opacity=0.3,
            mode="none",
            legendgroup=row["name"],
            text=hoverinfo,  # Use hovertemplate,
            hoverlabel=dict(bgcolor=current_color),
            hoverinfo="text",
            showlegend=False,
            name=row["name"],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x_start_Y1, x_end_Y1, x_end_Y1, x_start_Y1],
            y=[y_start_Y1, y_start_Y1, y_end_Y1, y_end_Y1],
            fill="toself",
            fillcolor=color_Y1,
            opacity=0.3,
            mode="none",  # Show lines and markers
            legendgroup=row["name"],
            text=hoverinfo,  # Use hovertemplate
            hoverinfo="text",
            hoverlabel=dict(bgcolor=current_color),
            showlegend=False,  # Important so that this does not show up as a separate entity in the legend
            name=row["name"],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x_start_X],
            y=[y_end_X],
            text=[rf"{diff_X:.2f}%"],
            mode="text",
            textposition="top left" if diff_X < 0 else "bottom left",
            legendgroup=row["name"],
            showlegend=False,
            name=row["name"],
            hoverinfo="none",
        )
    )
    # For bottom right anchoring:
    fig.add_trace(
        go.Scatter(
            x=[x_end_Y1],
            y=[y_end_Y1],
            text=[rf"{diff_Y1:.2f}%"],
            mode="text",
            textposition="top right" if diff_Y1 < 0 else "bottom right",
            legendgroup=row["name"],
            showlegend=False,
            name=row["name"],
            hoverinfo="none",
        )
    )

    # Horizontal line for Y2 (the reference) with markers
    fig.add_trace(
        go.Scatter(
            x=[index],
            y=[row["Y2"]],
            mode="lines+markers",
            line=dict(color=current_color),
            marker=dict(color=current_color, size=10),
            hovertext=hoverinfo,
            hoverinfo="text",
            legendgroup=row["name"],
            showlegend=show_in_legend,
            name=row["name"],
        )
    )
# Adjust the layout for clarity
fig.update_layout(
    showlegend=True,
    xaxis=dict(tickvals=list(range(len(df))), ticktext=df["name"].tolist()),
)

fig.show()


class CustomDivergencePlot:
    def __init__(self, df):
        self.df = df
        self.unique_names = df["name"].unique()
        self.colors = px.colors.qualitative.Plotly[: len(self.unique_names)]
        self.color_map = dict(zip(self.unique_names, self.colors))
        self.fig = go.Figure()

    @staticmethod
    def calculate_color(value, threshold=20):
        normalized = value / threshold
        normalized = min(max(normalized, -1), 1)
        if normalized > 0:
            return f"rgb(255, {255 * (1 - normalized)}, {255 * (1 - normalized)})"
        else:
            return f"rgb({255 * (1 + normalized)}, 255, {255 * (1 + normalized)})"

    @staticmethod
    def format_currency(value):
        if abs(value) < 1_000:
            return f"{value:.2f}"
        elif abs(value) < 1_000_000:
            return f"{value / 1_000:.2f}K"
        elif abs(value) < 1_000_000_000:
            return f"{value / 1_000_000:.2f}M"
        else:
            return f"{value / 1_000_000_000:.2f}B"

    def _add_traces(self, row, index):
        # ... [Keeping the original calculations from the for loop here, excluding the figure instantiation] ...

        self.fig.add_trace(go.Scatter(...))
        # ... [Remaining add_trace() calls from the for loop] ...

    def plot(self):
        for index, row in self.df.iterrows():
            self._add_traces(row, index)

        self.fig.update_layout(
            showlegend=True,
            xaxis=dict(
                tickvals=list(range(len(self.df))), ticktext=self.df["name"].tolist()
            ),
        )
        self.fig.show()


# Usage:
plotter = CustomDivergencePlot(df)
plotter.plot()
