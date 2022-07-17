import xarray as xr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def variable_plot(climate: xr.Dataset, variable: str, rcp: str = 'rcp85', color='green', bgcolor='lightgreen', fig: go.Figure = None, col: int = 1, row: int = 1) -> go.Figure:
    """
    Plot one of the climate model predicted variables, grouped by RCP scenario.
    If rcp is None, the grouping will not be applied.
    """
    # get the aggregated data
    df = climate.sel(vars=variable).to_dataframe().groupby(pd.Grouper(freq='a')).mean()
    
    # select by RCP scenario
    if rcp is not None:
        data = df[[c for c in df.columns if c.endswith(rcp)]]
    else:
        data = df
        rcp = 'all data'

    # get the figure
    if fig is None:
        fig = make_subplots(1, 1)

    # build the basic figure
    fig.add_trace(
        go.Scatter(x=data.mean(axis=1).index, y=np.nanquantile(data.values, 0.95, axis=1), mode='lines', line=dict(color=bgcolor), fill='none', showlegend=False),
        col=col, row=row
    )
    fig.add_trace(
        go.Scatter(x=data.mean(axis=1).index, y=np.nanquantile(data.values, 0.05, axis=1), mode='lines', line=dict(color=bgcolor), fill='tonexty', showlegend=False),
        col=col, row=row
    )
    fig.add_trace(
        go.Scatter(x=data.mean(axis=1).index, y=data.mean(axis=1), mode='lines', line=dict(color=color, width=2), name=f'{rcp.upper()} mean'),
        col=col, row=row
    )

    # layout
    fig.update_layout(
        **{f'yaxis{row}': dict(title=f'{rcp.upper()}<br>Windspeed [m/s]')}
    )

    return fig
