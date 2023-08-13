from random import uniform

import pandas as pd
import plotly.graph_objs as go
from pandas import Series

from abstractions import BasePlot
from utils.utils import format_currency, compute_difference


class DivergencePlot(BasePlot):
    COLOR_RED = "red"
    COLOR_GREEN = "green"

    def __init__(
            self,
            data,
            facet_row=None,
            color="name",
            left="left",
            right="right",
            reference="reference",
            hoverinfo: str = None,
    ):
        super().__init__(data, color, facet_row)
        self.left = left
        self.right = right
        self.reference = reference
        self.hoverinfo = hoverinfo

    def show(self):
        for _, row in self.data.iterrows():
            name_idx = self._get_color_index(row)
            self._add_traces(name_idx, row)

        if self.facet_row:
            for row_num, title in self.facet_titles.items():
                unique_names_for_facet = (
                    self.data[self.data[self.facet_row] == title][self.color]
                        .unique()
                        .tolist()
                )

                self.fig.update_yaxes(title_text=title, row=row_num, col=1)
                self.fig.update_xaxes(
                    tickvals=list(range(len(unique_names_for_facet))),
                    ticktext=unique_names_for_facet,
                    row=row_num,
                    col=1,
                )
        else:
            unique_names = self.data[self.color].unique().tolist()
            self.fig.update_layout(
                showlegend=True,
                xaxis=dict(
                    tickvals=list(range(len(unique_names))),
                    ticktext=unique_names,
                ),
            )

        self.fig.show()

    def _add_traces(self, index: float, row: Series):
        diff_left, diff_value_left = compute_difference(
            row[self.left], row[self.reference]
        )
        diff_right, diff_value_right = compute_difference(
            row[self.right], row[self.reference]
        )

        color_left = self._determine_color(diff_left)
        color_right = self._determine_color(diff_right)

        hoverinfo = self.hoverinfo or self._construct_hoverinfo(
            row, diff_left, diff_value_left, diff_right, diff_value_right
        )

        current_color = self.color_map[row[self.color]]

        self._add_trace(
            row,
            index,
            diff_left,
            color_left,
            hoverinfo,
            current_color,
            "left",
        )
        self._add_trace(
            row,
            index,
            diff_right,
            color_right,
            hoverinfo,
            current_color,
            "right",
        )
        self._add_horizontal_line(row, index, hoverinfo, current_color)

    def _add_trace(
            self,
            row,
            index,
            diff,
            color,
            hoverinfo,
            current_color,
            position,
    ):
        x_start, x_end = self._compute_x_positions(index, position)
        y_start = row[self.reference]
        y_end = row[self.left] if position == "left" else row[self.right]

        self._add_trace_to_figure(
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
            ),
            row,
        )

        text_position = "top" if diff < 0 else "bottom"
        text_position += " left" if position == "left" else " right"

        self._add_trace_to_figure(
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
            ),
            row,
        )

    def _add_horizontal_line(self, row, index, hoverinfo, current_color):
        self._add_trace_to_figure(
            go.Scatter(
                x=[index],
                y=[row[self.reference]],
                mode="lines+markers",
                line=dict(color=current_color),
                marker=dict(color=current_color, size=10),
                hovertext=hoverinfo,
                hoverinfo="text",
                legendgroup=row[self.color],
                showlegend=True,
                name=row[self.color],
            ),
            row,
        )

    def _determine_color(self, difference):
        return self.COLOR_GREEN if difference > 0 else self.COLOR_RED

    @staticmethod
    def _compute_x_positions(index: float, position):
        if position == "left":
            return index - 0.1, index
        return index, index + 0.1

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
            "name": [f"foo0", "foo1", "foo3", "foo4", "foo5", "foo6"],
            "region": [f"bar0", "bar0", "bar0", "bar1", "bar1", "bar2"],
        }

        return pd.DataFrame(data)


    # Test the function
    df = generate_data(6, scale="billions")
    plot = DivergencePlot(df, color="name", left="Foo", right="Bar", reference="Baz")
    plot.show()
