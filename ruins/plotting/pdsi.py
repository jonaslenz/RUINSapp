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


def tree_plot(data: pd.DataFrame, heights=[1, 0.3, 0], fig: go.Figure = None, row: int = 1, col: int = 1) -> go.Figure:
    """"""
    LEVELS = len(data.columns.levels) - 1
    RY, CY, LY = heights

    if fig is None:
        #fig = make_subplots(2, 1, shared_xaxes=True, row_heights=[0.35, 0.65])
        fig = make_subplots(1, 1)

    # get the root nodes
    roots = data.columns.get_level_values(0).unique().tolist()
    rootpos = [data.columns.get_level_values(0).tolist().index(r) for r in roots] + [len(data.columns)]

    # main crazy root

    # go for each root node with upper and lower limit on the x-axis
    for l, u , lab in zip(rootpos[:-1], rootpos[1:], roots):
        fig.add_annotation(x=int(l + (u - l) / 2), y=RY * 1.05, xref='x', yref='y', showarrow=False, text=lab.upper(), row=row, col=col)  

        # go for children 
        ch = data[lab].columns.get_level_values(0)
        childs = ch.unique().tolist()
        cpos = [l + ch.tolist().index(c) for c in childs] + [l + len(ch)]

        # get the plotting positions
        c_x = [int(cl + (cu - cl) / 2) for cl, cu in zip(cpos[:-1], cpos[1:])]
        c_y = [CY for _ in range(len(c_x))]
        fig.add_trace(go.Scatter(x=c_x, y=c_y, mode='markers', marker=dict(color='black', size=8), text=childs, showlegend=False, hovertemplate='%{text}<extra></extra>'), row=row, col=col)
    
    
        # go for each child node and add the traces
        for (cl, cu, clab) in zip(cpos[:-1], cpos[1:], childs):
            #fig.add_annotation(x=int(cl + (cu - cl) / 2), y=CY, xref='x', yref='y', ax=int(l + (u - l) / 2), ay=RY, axref='x', ayref='y', showarrow=True, arrowwidth=0.5)
            fig.add_trace(
                go.Scattergl(x=[int(cl + (cu - cl) / 2), int(l + (u - l) / 2)], y=[CY, RY], mode='lines', line=dict(color='black', width=0.9), showlegend=False),
                row=row, col=col
            )

            # break this iteration if the childs are actually the leaves
            if LEVELS == 1:
                continue

            # go for each leaf in this child
            for child in childs:
                leafs = data[(lab, clab)].columns.get_level_values(0).tolist()
                l_x = [cl + _ for _ in range(len(leafs))]
                l_y = [LY for _ in range(len(l_x))]

                # markers
                fig.add_trace(
                    go.Scatter(x=l_x, y=l_y, mode='markers', marker=dict(color='black', size=2), text=leafs, showlegend=False, hovertemplate="%{text}<extra></extra>"), 
                    row=row, col=col
                )

                for _x, _y in zip(l_x, l_y):
                    #fig.add_annotation(x=_x, y=_y, xref='x', yref='y', ax=int(cl + (cu - cl) / 2), ay=1., axref='x', ayref='y', showarrow=True, arrowwidth=0.5)
                    fig.add_trace(
                        go.Scattergl(x=[_x, int(cl + (cu - cl) / 2)], y=[LY, CY], mode='lines', line=dict(color='black', width=0.5), showlegend=False),
                        row=row, col=col
                    )
    
    # general layout
    fig.update_layout(
        template='none',
        xaxis=dict(range=[-2, len(data.columns) + 2], showticklabels=False, showline=False, zeroline=False, showgrid=False),
        yaxis=dict(showticklabels=False, showline=False, zeroline=False, showgrid=False),
    )

    # return 
    return fig
