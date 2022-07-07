import plotly.graph_objects as go
from scipy import stats
import numpy as np


BORDERS_COLORS = { # contains LOWER edges
    4: '#00A4B4',  # peacock blue
    7: '#00B5E2',  # sky blue
    9: '#C8E9E9',  # ice blue
    13: '#ffd7cb', # light salmon
    17: '#C63A4F', # watermelon
    20: '#800080'  # purple
}

BORDER_NAMES = ['extreme frost', 'frost', 'cold', 'warm', 'hot', 'tropic']


def plot_extreme_pdf(mus: float, stds: float, fig: go.Figure = None, border_colors=BORDERS_COLORS, border_names=BORDER_NAMES, x_range=(0, 25), x_res: int = 100, y_res: int = 25, label_margin_scale=1.1) -> go.Figure:
    """
    Temperature PDF shift plot.
    This function returns a plotly figure containing a heavily styled plotly PDF plot.
    It is controlled by passing the PDF moment(s) to the plot. If called with only one
    location and scale, the styled PDF is returned.
    If two locations and scales are passed, but both scales are the same, the PDF is
    only shifted by location and the original PDF is sketched. In case the scales differ,
    the new PDF will be correctly annotated.
    """
    # check input data
    if isinstance(mus, float):
        mu = mus
    else:
        mu = mus[1]

    if isinstance(stds, float):
        std = stds
    else:
        std = stds[1]

    # base data
    x = np.arange(*x_range, step=(x_range[1] - x_range[0]) / x_res)

    # get the distributions
    y = stats.norm.pdf(x, mu, std)
    y_max = y.max()
    if not isinstance(mus, float):
         # get the old PDF as well
        y_orig = stats.norm.pdf(x, mus[0], stds[0])
        
        # get the new Y max
        y_axis_max = max(y_orig.max(), y_max)
    else:
        y_axis_max = y_max
    
    # build the container for circles and circle colors
    c_x = []
    c_y = []
    colors = []

    # main, ugly loop
    for _x, _y in zip(x, y):
        # do not plot circles if they overlap with one of the mean markers
        if abs(_x - mu) < 1e-5:
            continue 
        if not isinstance(mus, float) and abs(_x - mus[0]) < 1e-5:
            continue

        # ratio of current prob.
        if _y / y_max < 0.01:
            continue
    
        # add circles - with y_res circles at max
        for t in np.arange(0, y_axis_max, y_axis_max / y_res):
            if t < _y * 0.95:
                c_x.append(_x)
                c_y.append(t)

                # check color
                # this is super ugly...
                c = border_colors[min(border_colors.keys())]
                for b, col in border_colors.items():
                    if _x > b:
                        c = col
                colors.append(c)
    
    # ugly part finished, do the plot
    if fig is None:
        fig = go.Figure()

    # handle if the shift already happend
    if not isinstance(mus, float):
        # plot the PDF and annotation
        fig.add_trace(
            go.Scatter(x=x, y=y_orig, mode='lines', line=dict(color='rgba(0,0,0,0.5)', dash='dash', width=2))
        )
        fig.add_trace(
            go.Scatter(x=[mus[0], mus[0]], y=[0, label_margin_scale * y_axis_max * 0.95], mode='lines', line=dict(color='rgba(0,0,0,0.5)', dash='dash'))
        )
        arr = dict(showarrow=True, arrowhead=3, arrowwidth=1.5, xref='x', yref='y', axref='x', ayref='y', standoff=8, startstandoff=6)
        fig.add_annotation(x=mus[0], y=label_margin_scale * y_axis_max, text='T<sub>0</sub>', showarrow=False, font=dict(size=20))
        fig.add_annotation(x=mus[1], y=label_margin_scale * y_axis_max, ax=mus[0], ay=label_margin_scale * y_axis_max, **arr)

        # check if the PDF changed the size
        if abs(stds[0] - stds[1] ) > 1e-5:
            fig.add_annotation(x=mu, y=y_max, ax=mu, ay=label_margin_scale * y_axis_max, **arr)
            pass
    else:
        # use current y_max as there is no second PDF
        y_axis_max = y_max

    # plot the color borders
    #for border, color in color_borders.items():
    #    fig.add_trace(
    #        go.Scatter(x=[border, border], y=[0, y_max], mode='lines', line=dict(dash='dash', color=color))
    #    )

    # main PDF
    fig.add_trace(
        go.Scatter(x=x, y=y, mode='lines', line=dict(color='black', width=3))
    )

    # colored circles
    fig.add_trace(
        go.Scatter(x=c_x, y=c_y, mode='markers', marker=dict(size=5, color=colors))
    )

    # handle temperature markers
    if not isinstance(stds, float) and stds[0] != stds[1]:
        mark_y = y_max
    else:
        mark_y = label_margin_scale * y_axis_max * 0.95
    fig.add_trace(
        go.Scatter(x=[mu, mu], y=[0, mark_y], mode='lines', line=dict(color='black', dash='dash'))
    )
    txt = f'T<sub>{0 if isinstance(mus, float) else 1}</sub>'
    fig.add_annotation(x=mu, y=label_margin_scale * y_axis_max, text=txt, showarrow=False, font=dict(size=20))
    
    # y axis annotations
    dom = dict(xref='x domain', yref='y domain', axref='x domain', ayref='y domain')
    fig.add_annotation(x=-0.01, y=0.95,ax=-0.01, ay=0.1, showarrow=True, arrowhead=2, arrowwidth=3, arrowcolor='rgba(0,0,0,0.5)', **dom)
    fig.add_annotation(x= -0.01, y=0.5, text='frequency', showarrow=False, textangle=270, font=dict(size=18, color='rgba(0,0,0,0.5)'), **dom)

    # x axis annotations
    for i, (low, up)  in enumerate(zip(list(border_colors.keys()), list(border_colors.keys())[1:] + [x_range[1]])):
        ref = dict(xref='x', yref='y', axref='x', ayref='y', startstandoff=1, standoff=1)
        ax = low if low != min(border_colors.keys()) else 0
        fig.add_annotation(x=up, y=-0.02, ax=ax, ay=-0.02, showarrow=True, arrowside='start+end', arrowhead=2, startarrowhead=2, arrowwidth=2, arrowcolor=border_colors[low], **ref)
        fig.add_annotation(x=ax + (up - ax) / 2, y=-0.035, showarrow=False, text=border_names[i], font=dict(size=16, color=border_colors[low]), xref='x', yref='y')

    # some layout fixes
    fig.update_layout(
        template='plotly_white',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        showlegend=False
    )
    
    # return
    return fig
