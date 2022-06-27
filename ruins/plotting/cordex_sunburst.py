import plotly.graph_objects as go
import pandas as pd


def sunburst(df: pd.DataFrame, maxdepth: int = 4, fig: go.Figure = None, width: int = 700, height: int = 700) -> go.Figure:
    """
    Create a sunburst plot of all climate models included in the current
    dataset used in RUINS. It will group them by GCM -> RCM -> RCP.
    The size of the sun can be restricted by the maxdepth argument.
    """
    # extract the data
    ids = df.ids.values
    labels = df.labels.values
    parents = df.parents.values
    values = df['values'].values
    customdata = list(zip(df.customdata1.values, df.customdata2.values))

    # handle figure
    if fig is None:
        fig = go.Figure()

    # build the sunburst
    fig.add_trace(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        insidetextorientation='radial',
        #hoverinfo='label+percent root+percent parent+value',
        maxdepth=maxdepth,
        customdata=customdata,
        hovertemplate='<b>Name</b>: %{label}<br><b>Total</b>: %{value}<br><br>%{customdata[0]}<br>%{customdata[1]}',
        name=''
    ))

    # figure config
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0),  width=width, height=height)
    
    return fig
