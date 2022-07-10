from typing import List

import plotly.express as px
import plotly.graph_objects as go

from ruins.core import Config, DataManager


def pdsi_plot(dataManager: DataManager, group_by: str = None, filter: List[str] = None, colorscale: str = 'RdBu') -> go.Figure:
    """Heatmap plot for Palmer drought severity index"""
    # load the data
    pdsi = dataManager.read('pdsi')

    # create the figure
    fig = px.imshow(pdsi, color_continuous_scale=colorscale, origin='lower', template='none')
    
    fig.update_layout(
        yaxis=dict(title='year')
    )
    # return
    return fig
