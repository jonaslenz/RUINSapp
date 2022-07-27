from typing import List, Union

import numpy as np
from numpy.linalg import LinAlgError
import pandas as pd
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from itertools import product

from ruins.core import DataManager
from ruins.processing.windpower import windpower_actions_projection


def windpower_distplot(
    actions: List[pd.DataFrame],
    names: List[str] = None,
    fig: go.Figure = None,
    fill: str = None,
    showlegend: Union[bool, List[bool]] = False,
    colors: Union[str, List[str]] = None,
    col: int = 1,
    row: int = 1
) -> go.Figure:
    """Plot the actions projected to climate models """    
    if fig is None:
        fig = make_subplots(1, 1)
    
    # align showlegend
    if isinstance(showlegend, bool):
        showlegend = [showlegend] * len(actions)
    
    # align names
    if names is None:
        names = [None] * len(actions)
    
    # align colors
    if colors is None:
        n = len(actions)
        colors = [f'rgba(32, 42, 68, {(i + n / 2) / (n + n / 2)})' for i in range(n)]

    # add all actions
    for i, (action, show, name, color) in enumerate(zip(actions, showlegend, names, colors)):
        y = action.sum(axis=1).values
        x = np.linspace(y.min(), y.max(), 100)

        # make sure there is no singular matrix (possibly only zeros passed)
        try:
            kde = gaussian_kde(y)(x)

            fig.add_trace(
                go.Scatter(x=x, y=kde, mode='lines', line=dict(color=color, width=0. if fill is not None else 1), name=name, fill=fill, showlegend=show),
                col=col, row=row
            )
        except LinAlgError as e:
            # do nothing?  Warning?
            pass


    return fig


def ternary_provision_plot(dataManager: DataManager, filter_: dict = {}, turbines: List[str] = ['e53', 'e115', 'e126'], colorscale: str = 'Cividis', showscale: bool = True) -> go.Figure:
    """Make a ternary plot of the three turbines shares on the axes and the provisioned Windpower as contours"""
    # get amount of turbines what to to if n_turbines != 3
    n_turbines = len(turbines)
    
    # get all combinations
    gen = [np.arange(0.0, 1.0, 0.1) for _ in range(n_turbines)]
    scenarios = [t for t in product(*gen) if abs(sum(t) - 1.0) < 1e-5][1:]

    # get all the actions based on the built scenario 
    actions, _ = windpower_actions_projection(dataManager, scenarios, site=396.0, filter_=filter_)

    # align data and axis
    data = np.fromiter((action.sum(axis=1).mean() for action in actions), dtype=float)
    axes = np.array([[int(s[i] * 100) for s in scenarios]  for i in range(n_turbines)])

    # build the figure
    fig = ff.create_ternary_contour(axes, data, pole_labels=turbines, ncontours=20, colorscale=colorscale, showscale=showscale)
    return fig
