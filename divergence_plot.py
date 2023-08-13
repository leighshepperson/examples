from random import uniform

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


class DivergencePlot:
    def __init__(
            self, data, color="name", left="left", right="right", reference="reference"
    ):
        self.data = data
        self.color = color
        self.left = left
        self.right = right
        self.reference = reference
        self.unique_names = data[self.color].unique()
        self.colors = px.colors.qualitative.Plotly[: len(self.unique_names)]
        self.color_map = dict(zip(self.unique_names, self.colors))
        self.fig = go.Figure()

    def show(self):
        for index, row in self.data.iterrows():
            self._add_traces(row, index)

        self.fig.update_layout(
            showlegend=True,
            xaxis=dict(
                tickvals=list(range(len(self.data))),
                ticktext=self.data[self.color].tolist(),
            ),
        )
        self.fig.show()

    def _add_traces(self, row, index):
        diff_left, diff_value_left = self._compute_difference(
            row[self.left], row[self.reference]
        )
        diff_right, diff_value_right = self._compute_difference(
            row[self.right], row[self.reference]
        )

        color_left = self._determine_color(diff_left)
        color_right = self._determine_color(diff_right)

        hoverinfo = self._construct_hoverinfo(
            row, diff_left, diff_value_left, diff_right, diff_value_right
        )

        current_color = self.color_map[row[self.color]]
        show_in_legend = row[self.color] not in [t["name"] for t in self.fig.data]

        self._add_trace(
            row,
            index,
            diff_left,
            color_left,
            hoverinfo,
            current_color,
            show_in_legend,
            "left",
        )
        self._add_trace(
            row,
            index,
            diff_right,
            color_right,
            hoverinfo,
            current_color,
            show_in_legend,
            "right",
        )
        self._add_horizontal_line(row, index, hoverinfo, current_color, show_in_legend)

    def _construct_hoverinfo(
            self, row, diff_left, diff_value_left, diff_right, diff_value_right
    ):
        return (
            f"<b>{row[self.color]}</b><br><br>"
            f"{self.left}: {self._format_currency(row[self.left])}<br>"
            f"{self.right}: {self._format_currency(row[self.right])}<br>"
            f"{self.reference}: {self._format_currency(row[self.reference])}<br>"
            f"Diff {self.left} to {self.reference} (%): {diff_left:.2f}% (Value): {self._format_currency(diff_value_left)}<br>"
            f"Diff {self.right} to {self.reference} (%): {diff_right:.2f}% (Value): {self._format_currency(diff_value_right)}<br>"
        )

    def _add_trace(
            self,
            row,
            index,
            diff,
            color,
            hoverinfo,
            current_color,
            show_in_legend,
            position,
    ):
        x_start, x_end = self._compute_x_positions(index, position)
        y_start = row[self.reference]
        y_end = row[self.left] if position == "left" else row[self.right]

        self.fig.add_trace(
            go.Scatter(
                x=[x_start, x_end, x_end, x_start],
                y=[y_start, y_start, y_end, y_end],
                fill="toself",
                fillcolor=color,
                opacity=0.3,
                mode="none",
                legendgroup=row[self.color],
                text=hoverinfo,
                hoverlabel=dict(bgcolor=current_color),
                hoverinfo="text",
                showlegend=False,
                name=row[self.color],
            )
        )

        text_position = "top" if diff < 0 else "bottom"
        text_position += " left" if position == "left" else " right"

        self.fig.add_trace(
            go.Scatter(
                x=[x_end],
                y=[y_end],
                text=[rf"{diff:.2f}%"],
                mode="text",
                textposition=text_position,
                legendgroup=row[self.color],
                showlegend=False,
                name=row[self.color],
                hoverinfo="none",
            )
        )

    def _add_horizontal_line(
            self, row, index, hoverinfo, current_color, show_in_legend
    ):
        self.fig.add_trace(
            go.Scatter(
                x=[index],
                y=[row[self.reference]],
                mode="lines+markers",
                line=dict(color=current_color),
                marker=dict(color=current_color, size=10),
                hovertext=hoverinfo,
                hoverinfo="text",
                legendgroup=row[self.color],
                showlegend=show_in_legend,
                name=row[self.color],
            )
        )

    @staticmethod
    def _format_currency(value):
        if abs(value) < 1_000:
            return f"{value:.2f}"
        elif abs(value) < 1_000_000:
            return f"{value / 1_000:.2f}K"
        elif abs(value) < 1_000_000_000:
            return f"{value / 1_000_000:.2f}M"
        else:
            return f"{value / 1_000_000_000:.2f}B"

    @staticmethod
    def _compute_difference(value1, value2):
        diff_percentage = -((value1 - value2) / value2) * 100
        diff_value = -(value1 - value2)
        return diff_percentage, diff_value

    @staticmethod
    def _determine_color(difference):
        return "green" if difference > 0 else "red"

    @staticmethod
    def _compute_x_positions(index, position):
        if position == "left":
            return index - 0.1, index
        return index, index + 0.1


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
        "Expected": X,
        "Planned": Y1,
        "Realised": Y2,
        "name": [f"foo{i + 1}" for i in range(n)],
    }

    return pd.DataFrame(data)


# Test the function
df = generate_data(10, scale="billions")
plot = DivergencePlot(
    df, color="name", left="Expected", right="Planned", reference="Realised"
)
plot.show()
