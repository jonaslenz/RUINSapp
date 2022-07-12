from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def pdsi_plot(data: pd.DataFrame, colorscale: str = 'RdBu', fig: go.Figure = None, row: int = 1, col: int = 1, **kwargs) -> go.Figure:
    """Heatmap plot for Palmer drought severity index"""
    # check if the data has been grouped
    is_grouped = isinstance(data.columns, pd.MultiIndex)


    # create the figure
    if fig is None:
        fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Heatmap(y=data.index, z=data.values, colorscale=colorscale), row=row, col=col)
    
    if is_grouped:
        # extract the level
        lvl0 = data.columns.get_level_values(0)
        labels = lvl0.unique().tolist()
        n_cols = len(data.columns)
        positions = [*[lvl0.tolist().index(l) for l in labels], n_cols - 1]

        # add the annotations
        for l, u, lab in zip(positions[:-1], positions[1:], labels):
            fig.add_annotation(x=u, ax=l, y=-.03, ay=-.03, xref='x', axref='x', yref='paper', arrowside='start+end', arrowhead=2, showarrow=True)
            fig.add_annotation(x=int(l + (u - l) / 2), y=-.1, xref='x', yref='paper', text=lab.upper(), showarrow=False)

        # remove the x-axis
        fig.update_layout(**{
            f'xaxis{row}': dict(showticklabels=False, showline=False)
        })
         
    # general layout
    fig.update_layout(**{
        f'yaxis{row}': dict(title='Jahr' if kwargs.get('lang', 'de')=='de' else 'Year', range=[data.index.min(), data.index.max()]),
    })

    # return
    return fig
