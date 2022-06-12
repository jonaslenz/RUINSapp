import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def sea_level(tide_data: pd.DataFrame, input_scale: float = 1/1000., knock_level: float = None, fig: go.Figure = None, row: int = 1, col: int = 1) -> go.Figure:
    # build a figure, if there is None
    if fig is None:
        fig = make_subplots(1, 1)

    # add tide data
    fig.add_trace(
        go.Scatter(x=tide_data.index, y=tide_data.values * input_scale, name='Sea level', line=dict(color='blue')), row=row, col=col
    )

    # add knock level
    if knock_level is not None:
        fig.add_hline(y=knock_level, name="Knock catastrophic water level", line=dict(color='red', dash='dash'), opacity=0.5)
        fig.add_annotation(x=0.5, y=0.95, xref="x domain", yref="y domain", text="Knock catastrophic water level", showarrow=False, font=dict(color='red', size=16))

    # update layout
    fig.update_layout(**{
        f'yaxis{row}': dict(title='Sea level [mNN]'),
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'legend': dict(orientation='h')
    })
    
    return fig


def canal_recharge(recharge_data: pd.DataFrame, cumsum: bool = False, fig: go.Figure = None, row: int = 1, col: int = 1) -> go.Figure:
    if fig is None:
        fig = make_subplots(1, 1)

    # handle cumsum
    if cumsum:
        recharge_data = np.cumsum(recharge_data)
        label = "Cumulative recharge"
    else:
        label = "Absolute recharge"

    # build the plot
    fig.add_trace(
        go.Scatter(x=recharge_data.index, y=recharge_data.values, name=label, line=dict(color='blue')),
        row=row, col=col
    )

    # update layout
    fig.update_layout(**{
        f'yaxis{row}': dict(title='Recharge [mm]'),
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'legend': dict(orientation='h')
    })
    
    return fig
