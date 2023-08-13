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


fig = go.Figure()

# Loop through each data point
for index, row in df.iterrows():
    # Calculate percentage differences
    diff_X = ((row["X"] - row["Y2"]) / row["Y2"]) * 100
    diff_Y1 = ((row["Y1"] - row["Y2"]) / row["Y2"]) * 100

    color_X = calculate_color(diff_X)
    color_Y1 = calculate_color(diff_Y1)

    current_color = color_map[row["name"]]

    # Determine if this trace should show in legend
    show_in_legend = row["name"] not in [t["name"] for t in fig.data]

    # Shaded area between X and Y2
    fig.add_shape(
        type="rect",
        x0=index - 0.1,
        y0=row["Y2"],
        x1=index,
        y1=row["X"],
        fillcolor=color_X,
        opacity=0.3,
        layer="below",
        line_width=0,
        legendgroup=row["name"],
    )

    # Shaded area between Y1 and Y2
    fig.add_shape(
        type="rect",
        x0=index,
        y0=row["Y2"],
        x1=index + 0.1,
        y1=row["Y1"],
        fillcolor=color_Y1,
        opacity=0.3,
        layer="below",
        line_width=0,
        legendgroup=row["name"],
    )

    # Annotations for significant differences
    fig.add_annotation(
        x=index - 0.05,
        y=(row["X"] + row["Y2"]) / 2,
        xref="x",
        yref="y",
        text=f"{diff_X:.2f}%",
        showarrow=False,
        ax=0,
        ay=0,
        align="center",
        bgcolor="rgba(255,255,255,0.6)",
        legendgroup=row["name"],
    )
    fig.add_annotation(
        x=index + 0.05,
        y=(row["Y1"] + row["Y2"]) / 2,
        xref="x",
        yref="y",
        text=f"{diff_Y1:.2f}%",
        showarrow=False,
        ax=0,
        ay=0,
        align="center",
        bgcolor="rgba(255,255,255,0.6)",
        legendgroup=row["name"],
    )

# Adjust the layout for clarity
fig.update_layout(
    showlegend=True,
    xaxis=dict(tickvals=list(range(len(df))), ticktext=df["name"].tolist()),
)

fig.show()
