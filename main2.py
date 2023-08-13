import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

data = {
    "X": [11, 23, 33, 49, 50] * 2,
    "Y1": [14.5, 20.4, 38.3, 44.2, 53.1] * 2,
    "Y2": [15.6, 15.6, 15.6, 15.6, 15.6] * 2,
    "x_name": ["A", "A", "A", "A", "A"] * 2,
    "y1_name": ["B", "B", "B", "B", "B"] * 2,
    "y2_name": ["C", "C", "C", "C", "C"] * 2,
    "name": ["foo1", "foo2", "foo3", "foo4", "foo5"]
    + ["foo6", "foo7", "foo8", "foo9", "foo10"],
}

df = pd.DataFrame(data)

unique_names = df["name"].unique()
colors = px.colors.qualitative.Plotly[: len(unique_names)]
color_map = dict(zip(unique_names, colors))

fig = go.Figure()


# Heatmap color scale function
def calculate_color(value, threshold=20):
    normalized = value / threshold
    if normalized > 1:
        normalized = 1
    if normalized < -1:
        normalized = -1
    if normalized > 0:
        return f"rgb({255 * (1 - normalized)}, 255, 255)"
    else:
        return f"rgb(255, 255, {255 * (1 + normalized)})"


# Loop through each data point
for index, row in df.iterrows():
    # Calculate percentage differences
    diff_X = ((row["X"] - row["Y2"]) / row["Y2"]) * 100
    diff_Y1 = ((row["Y1"] - row["Y2"]) / row["Y2"]) * 100

    # Calculate start and end points for the vertical lines
    y_start_X = row["Y2"]
    y_end_X = row["X"]
    y_start_Y1 = row["Y2"]
    y_end_Y1 = row["Y1"]

    # Decide color and position for annotations based on difference
    color_X = "red" if diff_X > 0 else "green"
    color_Y1 = "red" if diff_Y1 > 0 else "green"
    y_position_X = y_end_X + 1 if diff_X > 0 else y_end_X - 1
    y_position_Y1 = y_end_Y1 + 1 if diff_Y1 > 0 else y_end_Y1 - 1

    current_color = color_map[row["name"]]
    color_X = calculate_color(diff_X)
    color_Y1 = calculate_color(diff_Y1)

    # Determine if this trace should show in legend
    show_in_legend = row["name"] not in [t["name"] for t in fig.data]

    # Horizontal line for Y2 (the reference) with markers
    fig.add_trace(
        go.Scatter(
            x=[index - 0.2, index, index + 0.2],
            y=[row["Y2"], row["Y2"], row["Y2"]],
            mode="lines+markers",
            line=dict(color=current_color),
            marker=dict(color=current_color, size=10),
            hovertext=f"{row['y2_name']}: {row['Y2']}",
            hoverinfo="text",
            legendgroup=row["name"],
            showlegend=show_in_legend,
            name=row["name"],
        )
    )

    # Shaded area between X and Y2
    fig.add_shape(
        type="rect",
        x0=index - 0.25,
        y0=row["Y2"],
        x1=index - 0.15,
        y1=row["X"],
        fillcolor=color_X,
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Shaded area between Y1 and Y2
    fig.add_shape(
        type="rect",
        x0=index + 0.15,
        y0=row["Y2"],
        x1=index + 0.25,
        y1=row["Y1"],
        fillcolor=color_Y1,
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    color_X = "red" if diff_X > 0 else "green"
    color_Y1 = "red" if diff_Y1 > 0 else "green"
    y_position_X = y_end_X + 1 if diff_X > 0 else y_end_X - 1
    y_position_Y1 = y_end_Y1 + 1 if diff_Y1 > 0 else y_end_Y1 - 1

    # Shaded area between X and Y2
    fig.add_shape(
        type="rect",
        x0=index - 0.25,
        y0=y_start_X,
        x1=index - 0.15,
        y1=y_end_X,
        fillcolor=color_X,
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Shaded area between Y1 and Y2
    fig.add_shape(
        type="rect",
        x0=index + 0.15,
        y0=y_start_Y1,
        x1=index + 0.25,
        y1=y_end_Y1,
        fillcolor=color_Y1,
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Annotations for significant differences
    fig.add_annotation(
        x=index - 0.2,
        y=y_position_X,
        xref="x",
        yref="y",
        text=f"{diff_X:.2f}%",
        showarrow=False,
        ax=0,
        ay=0,
        align="center",
        bgcolor="rgba(255,255,255,0.6)",
    )
    fig.add_annotation(
        x=index + 0.2,
        y=y_position_Y1,
        xref="x",
        yref="y",
        text=f"{diff_Y1:.2f}%",
        showarrow=False,
        ax=0,
        ay=0,
        align="center",
        bgcolor="rgba(255,255,255,0.6)",
    )
# Adjust the layout for clarity
fig.update_layout(
    showlegend=True,
    xaxis=dict(tickvals=list(range(len(df))), ticktext=df["name"].tolist()),
)

fig.show()
