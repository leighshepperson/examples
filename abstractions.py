import abc

import pandas as pd
import plotly.graph_objs as go
from pandas import Series
from plotly.subplots import make_subplots

from utils.utils import create_color_map


class BasePlot:
    def __init__(self, data: pd.DataFrame, color: str = None, facet_row: str = None):
        self.data = data
        self.color = color
        self.facet_row = facet_row
        self.color_map = create_color_map(self.data, color)
        self._configure_faceting()
        self.added_legend_items = {}

    def show(self):
        for index, row in self.data.iterrows():
            self._add_traces(index, row)

        if self.facet_row:
            for row_num, title in self.facet_titles.items():
                self.fig.update_yaxes(title_text=title, row=row_num, col=1)

        self.fig.show()

    def _get_color_index(self, row: pd.Series) -> float:
        if self.facet_row:
            unique_names_for_facet = (
                self.data[self.data[self.facet_row] == row[self.facet_row]][self.color]
                .unique()
                .tolist()
            )
        else:
            unique_names_for_facet = self.data[self.color].unique().tolist()

        return unique_names_for_facet.index(row[self.color])

    @abc.abstractmethod
    def _add_traces(self, index: float, row: Series):
        ...

    def _add_trace_to_figure(self, trace, row: pd.Series):
        row_num = (
            self.facet_values.get(row[self.facet_row], 1) if self.facet_row else None
        )

        legend_key = f"{trace['legendgroup']}_{trace['name']}"

        if trace["showlegend"]:
            if legend_key in self.added_legend_items:
                trace["showlegend"] = False
            else:
                self.added_legend_items[legend_key] = True

        if self.facet_row:
            self.fig.add_trace(trace, row=row_num, col=1)
        else:
            self.fig.add_trace(trace)

    def _configure_faceting(self):
        if self.facet_row:
            facet_values = self.data[self.facet_row].unique()
            self.facet_values = {
                value: idx + 1 for idx, value in enumerate(facet_values)
            }
            self.facet_titles = {
                idx + 1: value for idx, value in enumerate(facet_values)
            }
            self.fig = make_subplots(rows=len(facet_values), cols=1)
        else:
            self.fig = go.Figure()
