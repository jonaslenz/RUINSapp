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
        fig.add_hline(y=knock_level, name="0 mNHN - average sea level before sea level rise", line=dict(color='grey', dash='dash'), opacity=0.5)
        fig.add_annotation(x=0.5, y=0.95, xref="x domain", yref="y domain", text="0 mNHN - average sea level before sea level rise", showarrow=False, font=dict(color='grey', size=16))

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


def absolute_water_level(hg_model_runs: list, 
                         EVEx5_lw_pegel_timesliced: pd.Series,
                         fig: go.Figure = None, 
                         row: int = 1, col: int = 1) -> go.Figure:
    
    # build a figure, if there is None
    if fig is None:
        fig = make_subplots(1, 1)
    
    for run in hg_model_runs:  
        fig.add_trace(
            go.Scatter(x=run[0].index, y=run[0]/1000, 
                       line=dict(color='grey'), showlegend=False), row=row, col=col)
        fig.update_traces(opacity=.3)
        
    fig.add_trace(
        go.Scatter(x=[-1], y=[-1], visible='legendonly', 
                   name='$H_G in catchment (simulated)$', 
                   line=dict(color='grey')), row=row, col=col) # Nur für die Legende
    
    fig.add_trace(
        go.Scatter(x=EVEx5_lw_pegel_timesliced.index, y=EVEx5_lw_pegel_timesliced, 
                   name=r'$H_G [m] \text{(observed)}$', 
                   line=dict(color='green')), row=row, col=col)

    # add canal crest
    fig.add_hline(y=-0.9, name=r'$Canal water level with first damages$', 
                  line=dict(color='red', dash='dash'), opacity=0.5, row=row, col=col)

    # update layout
    fig.update_layout(**{
        f'yaxis{row}': dict(title='Absolute Water Level $H_G$'),
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        #'legend': dict(orientation='h')
    })
    
    return fig


def pump_capacity(hg_model_runs: list, 
                  pump_capacity_observed: pd.Series,
                cumsum: bool = False, 
                fig: go.Figure = None, 
                row: int = 1, col: int = 1) -> go.Figure:
    
    if fig is None:
        fig = make_subplots(1, 1)

    # build the plot
    for run in hg_model_runs:
        if cumsum:
            fig.add_trace(
                go.Scatter(x=run[0].index, y=np.cumsum(run[1]), 
                           line=dict(color='grey'), showlegend=False), row=row, col=col)
        else:
            fig.add_trace(
                go.Scatter(x=run[0].index, y=run[1] * 100, 
                           line=dict(color='grey'), showlegend=False), row=row, col=col)
    
    fig.update_traces(opacity=.3)
    
    
    if cumsum:
        fig.add_trace(
            go.Scatter(x=[0], y=[0], visible='legendonly', 
                       name='Cumulative pump capacity at Knock [-]', 
                       line=dict(color='grey')), row=row, col=col) # Nur für die Legende
    else:
        fig.add_trace(
            go.Scatter(x=[0], y=[0], visible='legendonly', 
                       name='Used pump capacity (simulated)', 
                       line=dict(color='grey')), row=row, col=col) # Nur für die Legende
        
        fig.add_trace(
            go.Scatter(x=pump_capacity_observed.index, y=pump_capacity_observed, 
                       name='Used pump capacity (observed)', 
                       line=dict(color='lightblue')), row=row, col=col)
        if row == 2:  # AAaaaaAAAaaarghh
            fig.update_layout(yaxis2=dict(range=[-2,102]))

    # update layout
    fig.update_layout(**{
        f'yaxis{row}': dict(title='[%]'),
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        #'legend': dict(orientation='h')
    })
    
    return fig

