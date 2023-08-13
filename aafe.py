import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

data = {
    "X": [11, 23, 33, 49, 50],
    "Y1": [14.5, 20.4, 38.3, 44.2, 53.1],
    "Y2": [15.6, 25.7, 35.8, 45.9, 55.0],
    "x_name": ["A", "A", "A", "A", "A"],
    "y1_name": ["B", "B", "B", "B", "B"],
    "y2_name": ["C", "C", "C", "C", "C"],
    "name": ["foo1", "foo2", "foo3", "foo4", "foo5"],
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
        return (1 - normalized, 1, 1)
    else:
        return (1, 1, 1 + normalized)


# Loop through each data point
for index, row in df.iterrows():
    # Calculate percentage differences
    diff_X = ((row["X"] - row["Y2"]) / row["Y2"]) * 100
    diff_Y1 = ((row["Y1"] - row["Y2"]) / row["Y2"]) * 100

    current_color = color_map[row["name"]]

    # Determine if this trace should show in legend
    show_in_legend = row["name"] not in [t["name"] for t in fig.data]

    # Horizontal line for Y2 (the reference) without markers
    fig.add_trace(
        go.Scatter(
            x=[index - 0.2, index + 0.2],
            y=[row["Y2"], row["Y2"]],
            mode="lines",
            line=dict(color=current_color),
            hoverinfo="none",  # Turn off hover for the line
            legendgroup=row["name"],
            showlegend=show_in_legend,
            name=row["name"],
        )
    )

    # Middle marker for Y2
    fig.add_trace(
        go.Scatter(
            x=[index],
            y=[row["Y2"]],
            mode="markers+text",
            marker=dict(color=current_color, size=10),
            hovertext=f"{row['y2_name']}: {row['Y2']}",
            hoverinfo="text",
            text=row["y2_name"],
            textposition="top center",  # Change here to position the text above the marker
            legendgroup=row["name"],
            showlegend=False,
            name=row["name"],
        )
    )

    # Vertical line from the left end of Y2 to X with marker at intersection
    y_start_X = row["Y2"]
    y_end_X = row["X"]
    color_X = "red" if y_end_X > y_start_X else "green"
    fig.add_trace(
        go.Scatter(
            x=[index - 0.2, index - 0.2],
            y=[y_start_X, y_end_X],
            mode="lines+markers+text",
            line=dict(color=color_X),
            hovertext=f"{row['x_name']}: {row['X']} ({diff_X:.2f}%)",
            hoverinfo="text",
            text=[
                None,
                f"{row['x_name']} ({diff_X:.2f}%)",
            ],  # Display x_name and percentage difference at the end
            textposition="bottom left",
            legendgroup=row["name"],
            showlegend=False,
            name=row["name"],
            marker=dict(color=color_X, size=10),
        )
    )

    # Vertical line from the right end of Y2 to Y1 with marker at intersection
    y_start_Y1 = row["Y2"]
    y_end_Y1 = row["Y1"]
    color_Y1 = "red" if y_end_Y1 > y_start_Y1 else "green"
    fig.add_trace(
        go.Scatter(
            x=[index + 0.2, index + 0.2],
            y=[y_start_Y1, y_end_Y1],
            mode="lines+markers+text",
            line=dict(color=color_Y1),
            hovertext=f"{row['y1_name']}: {row['Y1']} ({diff_Y1:.2f}%)",
            hoverinfo="text",
            text=[
                None,
                f"{row['y1_name']} ({diff_Y1:.2f}%)",
            ],  # Display y1_name and percentage difference at the end
            textposition="bottom right",
            legendgroup=row["name"],
            showlegend=False,
            name=row["name"],
            marker=dict(color=color_Y1, size=10),
        )
    )

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

    color_X = calculate_color(diff_X)
    color_Y1 = calculate_color(diff_Y1)

    # Annotations for significant differences
    if abs(diff_X) > 20:
        fig.add_annotation(
            x=index - 0.2,
            y=y_end_X,
            text=f"{diff_X:.2f}%",
            showarrow=False,
            ax=0,
            ay=-20,
            bgcolor="rgba(255,255,255,0.6)",
        )
    if abs(diff_Y1) > 20:
        fig.add_annotation(
            x=index + 0.2,
            y=y_end_Y1,
            text=f"{diff_Y1:.2f}%",
            showarrow=False,
            ax=0,
            ay=-20,
            bgcolor="rgba(255,255,255,0.6)",
        )


# Adjust the layout for clarity
fig.update_layout(
    showlegend=True,
    xaxis=dict(tickvals=list(range(len(df))), ticktext=df["name"].tolist()),
)

fig.show()
