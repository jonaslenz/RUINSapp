from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ruins.core import Config, DataManager
from ruins.processing.pdsi import multiindex_pdsi_data


def pdsi_plot(dataManager: DataManager, config: Config, group_by: List[str] = None, filters: List[str] = None, colorscale: str = 'RdBu', fig: go.Figure = None, row: int = 1, col: int = 1) -> go.Figure:
    """Heatmap plot for Palmer drought severity index"""
    # load the data
    pdsi = dataManager.read('pdsi')

    # apply grouping
    if group_by is not None:
        data = multiindex_pdsi_data(pdsi, grouping=group_by, inplace=False)
    else:
        data = pdsi


    # create the figure
    if fig is None:
        fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Heatmap(y=data.index, z=data.values, colorscale=colorscale), row=row, col=col)
    
    if group_by is not None:
        # extract the level
        lvl0 = data.columns.get_level_values(0)
        labels = lvl0.unique().tolist()
        n_cols = len(data.columns)
        positions = [*[lvl0.tolist().index(l) for l in labels], n_cols - 1]

        # add the annotations
        for l, u, lab in zip(positions[:-1], positions[1:], labels):
            fig.add_annotation(x=u, ax=l, y=-.03, ay=-.03, xref='x', axref='x', yref='paper', arrowside='start+end', arrowhead=2, showarrow=True, row=row, col=col)
            fig.add_annotation(x=int(l + (u - l) / 2), y=-.1, xref='x', yref='paper', text=lab.upper(), showarrow=False, row=row, col=col)

        # remove the x-axis
        fig.update_layout(
            xaxis=dict(showticklabels=False, showline=False)
        )
         
    # general layout
    fig.update_layout(
        yaxis=dict(title='Jahr' if config.lang=='de' else 'Year')
    )

    # return
    return fig
