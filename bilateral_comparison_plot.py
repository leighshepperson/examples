from random import uniform

import pandas as pd
import plotly.graph_objs as go
from pandas import Series

from abstractions import BasePlot
from utils.utils import format_currency, compute_difference


class BilateralComparisonPlot(BasePlot):
    COLOR_RED = "red"
    COLOR_GREEN = "green"
    PADDING_PERCENTAGE = 0.05

    def __init__(
            self,
            data: pd.DataFrame,
            facet_row: str = None,
            color: str = "name",
            left: str = "left",
            right: str = "right",
            reference: str = "reference",
            hoverinfo: str = None,
    ):
        super().__init__(data, color, facet_row)
        self.color = color
        self.left = left
        self.right = right
        self.reference = reference
        self.reference_line_added = False
        self.hoverinfo = hoverinfo

    def _add_traces(self, index: float, row: Series):
        (
            diff_left,
            diff_value_left,
            diff_right,
            diff_value_right,
        ) = self._compute_differences(row)
        hoverinfo = self.hoverinfo or self._construct_hoverinfo(
            row, diff_left, diff_value_left, diff_right, diff_value_right
        )
        current_color = self.color_map[row[self.color]]
        show_in_legend = row[self.color] not in [t["name"] for t in self.fig.data]

        self._add_identity_line(row)
        self._add_line_trace(row, diff_right, show_in_legend)
        self._add_marker_traces(row, hoverinfo, current_color)

    def _add_identity_line(self, row: pd.Series):
        min_val, max_val = self._compute_data_range()
        trace = go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="x=y",
            hoverinfo="none",
            legendgroup="x=y",
            showlegend=not self.reference_line_added,  # Only show legend for the first trace
        )

        self._add_trace_to_figure(trace, row)

    def _compute_data_range(self):
        columns = [self.data[col] for col in [self.left, self.right, self.reference]]

        data_min = min(col.min() for col in columns)
        data_max = max(col.max() for col in columns)

        data_range = data_max - data_min

        min_val = data_min - self.PADDING_PERCENTAGE * data_range
        max_val = data_max + self.PADDING_PERCENTAGE * data_range

        return min_val, max_val

    def _compute_differences(self, row: pd.Series):
        diff_left, diff_value_left = compute_difference(
            row[self.left], row[self.reference]
        )
        diff_right, diff_value_right = compute_difference(
            row[self.right], row[self.reference]
        )
        return diff_left, diff_value_left, diff_right, diff_value_right

    def _add_line_trace(self, row: pd.Series, diff_right, show_in_legend):
        color = self.COLOR_GREEN if diff_right > 0 else self.COLOR_RED
        x = row[self.left]
        y_start = row[self.reference]
        y_end = row[self.right]

        arrow_symbol = "arrow-up" if diff_right > 0 else "arrow-down"
        arrow_position = (y_start + y_end) / 2

        trace = go.Scatter(
            x=[x, x],
            y=[y_start, y_end],
            mode="lines",
            marker=dict(color=color, size=10),
            hoverinfo="none",
            legendgroup=row[self.color],
            showlegend=False,
            name=row[self.color] if show_in_legend else "",
        )

        self._add_trace_to_figure(trace, row)

        arrow_trace = go.Scatter(
            x=[x],
            y=[arrow_position],
            mode="markers",
            marker=dict(symbol=arrow_symbol, size=12, color=color),
            hoverinfo="none",
            showlegend=False,
        )

        self._add_trace_to_figure(arrow_trace, row)

    def _add_marker_traces(self, row, hoverinfo, current_color):
        x = row[self.left]
        for y_value, text_pos, col_name, legend in [
            (row[self.reference], "top left", self.reference, True),
            (row[self.right], "bottom left", self.right, False),
        ]:
            marker_label = f"{row[self.color]}_{col_name}"

            trace = go.Scatter(
                x=[x],
                y=[y_value],
                mode="markers+text",
                marker=dict(
                    size=10,
                    color=current_color,
                ),
                text=marker_label,
                textposition=text_pos,
                textfont=dict(size=10),
                legendgroup=row[self.color],
                hoverinfo="text",
                hovertext=hoverinfo,
                showlegend=legend,
                name=row[self.color] if legend else "",
            )
            self._add_trace_to_figure(trace, row)

    def _construct_hoverinfo(
            self, row, diff_left, diff_value_left, diff_right, diff_value_right
    ):
        return (
            f"<b>{row[self.color]}</b><br><br>"
            f"{self.left}: {format_currency(row[self.left])}<br>"
            f"{self.right}: {format_currency(row[self.right])}<br>"
            f"{self.reference}: {format_currency(row[self.reference])}<br>"
            f"Diff {self.left} to {self.reference} (%): {diff_left:.2f}% (Value): {format_currency(diff_value_left)}<br>"
            f"Diff {self.right} to {self.reference} (%): {diff_right:.2f}% (Value): {format_currency(diff_value_right)}<br>"
        )


if __name__ == "__main__":
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
            "Foo": X,
            "Bar": Y1,
            "Baz": Y2,
            "name": [f"foo{i % 3}" for i in range(n)],
            "region": [f"bar{i % 5}" for i in range(n)],
        }

        return pd.DataFrame(data)


    # Test the function
    df = generate_data(10, scale="billions")
    plot = BilateralComparisonPlot(
        df, color="name", left="Foo", right="Bar", reference="Baz"
    )
    plot.show()
