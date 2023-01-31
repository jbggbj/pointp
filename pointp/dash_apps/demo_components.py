from collections import namedtuple
from typing import Callable, List

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, callback, ctx, dcc
import plotly.express as px
import pointp.dash_apps.dash_helper as dh
import pointp.simulate as ps
from pointp.plot import point_process_figure
from pointp.simulate import ModelParameter
from scipy.stats import poisson

def pp_example_row(
    name: str, process: "simulate.Process1D", bounds: list, plot_title: str = None
) -> dbc.Row:
    """

    :param name: Used for creating component IDs. Used as plot title by default.
    :param process:
    :param t_min:
    :param t_max:
    :param plot_title: Use this if you want to have plot title include latex formula
    that uses '{'
    :return:
    """
    if not plot_title:
        plot_title = name
    pts = np.ndarray([])
    example_process = None
    parameters = process.model_parameters
    fig_id = dh.component_id(name, "fig")
    button_id = dh.component_id(name, "button")
    bin_slider_id = dh.component_id(name + "_bins", "slider")

    slider_ids = {
        p.name: dh.component_id(f"{name}_{p.name}", "slider") for p in parameters
    }
    sliders = [
        dh.labeled_slider(p.min, p.max, p.name, id=slider_ids[p.name])
        for p in parameters
    ]
    slider_rows = [dh.my_row(slider) for slider in sliders]

    button_row = dh.my_row([dh.my_col(dbc.Button("Generate", id=button_id))])
    nbins_row = dh.my_row(
        dh.labeled_slider(1, 20, "# of bins", step=1, id=bin_slider_id)
    )
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id, mathjax=True)], width=9),
            dh.my_col(
                slider_rows + [button_row, nbins_row],
                width=3,
                align="center",
            ),
        ]
    )

    standard_for_callback = [
        Output(fig_id, "figure"),
        Input(button_id, "n_clicks"),
        Input(bin_slider_id, "value"),
    ]
    model_parameter_inputs = [Input(slider_ids[p.name], "value") for p in parameters]
    # Create callbacks
    @callback(*(standard_for_callback + model_parameter_inputs))
    def update_fig(n_clicks: int, n_bins: int, *mparams) -> go.Figure:
        nonlocal pts
        nonlocal example_process
        if ctx.triggered_id != bin_slider_id:
            example_process = process(*mparams)
            pts = example_process.simulate(*bounds)
        # fig = example_process.plot_func(
        #     pts, example_process.intensity, t_max, n_bins=n_bins
        # )
        fig = example_process.plot_func(pts, bounds, n_bins=n_bins)
        fig.update_layout(
            title={
                "text": plot_title,
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
        )
        return fig

        # return go.Figure()

    return example_row


