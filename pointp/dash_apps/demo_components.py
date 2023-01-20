from collections import namedtuple
import dash_bootstrap_components as dbc
import dash_helper as dh
from dash import callback, Input, Output, dcc, ctx
from typing import List, Callable
import plotly.graph_objs as go
import pointp.simulate as ps
from pointp.plot import point_process_figure
import numpy as np

ModelParameter = namedtuple("ModelParameter", ["name", "min", "max"])


def pp_example_row(
    name: str, parameters: List[ModelParameter],
        intensity_factory: Callable[[List[float]], Callable[[float], float]],
        t_min=0, t_max=1
) -> dbc.Row:
    example_tk = None
    fig_id = dh.component_id(name, "fig")
    button_id = dh.component_id(name, "button")
    bin_slider_id = dh.component_id(name + "_bins", "slider")

    slider_ids = {
        p.name: dh.component_id(f"{name}_{p.name}", "slider") for p in parameters
    }
    sliders = [
        dh.labeled_slider(
            p.min, p.max, p.name, id=slider_ids[p.name]) for p in parameters
    ]
    slider_rows = [dh.my_row(slider) for slider in sliders]

    button_row = dh.my_row([dh.my_col(dbc.Button("Generate", id=button_id))])
    nbins_row = dh.my_row(
        dh.labeled_slider(1, 20, "# of bins", step=1, id=bin_slider_id)
    )
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id)], width=9),
            dh.my_col(
                slider_rows + [button_row, nbins_row],
                width=3,
                align="center",
            ),
        ]
    )

    standard_for_callback = [Output(fig_id, "figure"),
                             Input(button_id, "n_clicks"),
                             Input(bin_slider_id, "value")
                             ]
    model_parameter_inputs = [
        Input(slider_ids[p.name], "value") for p in parameters
    ]
    # Create callbacks
    @callback(
        *(standard_for_callback + model_parameter_inputs)
    )
    def update_fig(n_clicks: int, n_bins: int, *mparams) -> go.Figure:
        if ctx.triggered_id != bin_slider_id:
            rate = intensity_factory(mparams)
            example_tk = ps.h_poisson_1d(rate(1), [t_min, t_max])

        fig = point_process_figure(example_tk, rate(1), t_max, n_bins=n_bins)
        fig.update_layout(
            title={
                "text": "Homogeneous Poisson Process",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            }
        )
        return fig

        return go.Figure()

    return example_row
