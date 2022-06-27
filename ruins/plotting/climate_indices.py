import pandas as pd
import plotly.graph_objects as go


def plot_climate_indices(data: pd.DataFrame, rcps=('rcp26', 'rcp45', 'rcp85'), fig: go.Figure = None) -> go.Figure:
    """
    Generate a climate indices plot. 
    Refer to :func:`ruins.processing.calculate_climate_indices` to learn about the structure
    needed for the DataFrame.
    """
    # create the figure if needed
    if fig is None:
        fig = go.Figure()
    
    # add the weather indices
    fig.add_trace(
        go.Scatter(x=data.index, y=data.iloc[:, 0].values, mode='markers', marker=dict(color='steelblue', size=5), name='Weather', hovertemplate="%{y} days in %{x}<extra></extra>")
    )

    # add the rolling mean
    fig.add_trace(
        go.Scatter(x=data.index, y=data['rolling'], mode='lines', line=dict(color='steelblue', width=3), name='Rolling mean (10 years)', hovertemplate="%{y:.1f} days in %{x}<extra></extra>")
    )

    for i, rcp in enumerate(rcps):        
        # melt down to only this rcp
        df = data.melt(value_vars=data.columns[[c.endswith(rcp) for c in data.columns]], ignore_index=False)
        fig.add_trace(
            go.Scattergl(x=df.index, y=df.value.values, mode='markers', marker=dict(color=f'rgba(127, 127, 127, {0.2 + 0.1 * i / 3})', size=5), name=rcp.upper(), meta=[rcp.upper()], hovertemplate="%{y} days in %{x}<extra>%{meta[0]}</extra>")
        )

        # add the rolling mean
        roll = data[[f'{rcp}.rolling']]
        fig.add_trace(
            go.Scatter(x=roll.index, y=roll.values.flatten(), mode='lines', line=dict(width=5), name=f'Rolling mean of {rcp.upper()}', meta=[rcp.upper()], hovertemplate="%{y:.1f} days in %{x}<extra>%{meta[0]}</extra>")
        )


    fig.update_layout(
        template='plotly_white',
        legend=dict(orientation='h'),
        yaxis=dict(title='Number of days'),
        margin=dict(t=1)
    )
    return fig