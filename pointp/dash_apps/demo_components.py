import math
from collections import namedtuple
from typing import Callable, List

import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, callback, ctx, dcc, html
from scipy import integrate
from scipy.stats import poisson

import pointp.dash_apps.dash_helper as dh
import pointp.simulate as ps
from pointp import simulate
from pointp.plot import point_process_figure


def pp_example_row(
    name: str,
    process: "simulate.Process1D",
    bounds: list,
    plot_title: str = None,
    show_bins: bool = True,
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
    standard_controls = [button_row]

    if show_bins:
        nbins_row = dh.my_row(
            dh.labeled_slider(1, 20, "# of bins", step=1, id=bin_slider_id)
        )
        standard_controls.append(nbins_row)
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id, mathjax=True)], width=9),
            dh.my_col(
                slider_rows + standard_controls,
                width=3,
                align="center",
            ),
        ]
    )

    if show_bins:
        standard_for_callback = [
            Output(fig_id, "figure"),
            Input(button_id, "n_clicks"),
            Input(bin_slider_id, "value"),
        ]
        model_parameter_inputs = [
            Input(slider_ids[p.name], "value") for p in parameters
        ]
        # Create callbacks
        @callback(*(standard_for_callback + model_parameter_inputs))
        def update_fig(n_clicks: int, n_bins: int, *mparams) -> go.Figure:
            nonlocal pts
            nonlocal example_process
            if ctx.triggered_id != bin_slider_id:
                example_process = process(*mparams)
                pts = example_process.simulate(*bounds)
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

    else:
        standard_for_callback = [
            Output(fig_id, "figure"),
            Input(button_id, "n_clicks"),
        ]
        model_parameter_inputs = [
            Input(slider_ids[p.name], "value") for p in parameters
        ]

        # Create callbacks
        @callback(*(standard_for_callback + model_parameter_inputs))
        def update_fig(n_clicks: int, *mparams) -> go.Figure:
            nonlocal pts
            nonlocal example_process
            example_process = process(*mparams)
            pts = example_process.simulate(*bounds)
            fig = example_process.plot_func(pts, bounds)
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

    return example_row


def poisson_dist_fig(
    mean: float, min_x_max: int = None, annotation: str = "mean"
) -> go.Figure:
    p_dist = poisson(mean)

    x_max = p_dist.ppf(0.999)
    if min_x_max:
        x_max = max(min_x_max, x_max)
    x_bins = np.arange(x_max + 1)
    fig = go.Figure(
        data=go.Bar(name="Poisson", x=x_bins, y=p_dist.pmf(x_bins)),
    )
    fig.update_yaxes(range=[0, 1])
    fig.add_vline(
        x=mean,
        annotation_text=annotation,
        line_color="black",
        annotation_position="top",
        opacity=1,
        line_width=2.0,
    )
    fig.update_layout(title="Poisson Distribution")
    fig.update_yaxes(title={"text": "Probability"})
    return fig


def pp_definition_row(
    name: str,
    process: "simulate.Process1D",
    bounds: list,
    plot_title: str = None,
    y_max: float = None,
) -> dbc.Row:

    example_process = None
    parameters = process.model_parameters
    slider_ids = {
        p.name: dh.component_id(f"{name}_{p.name}", "slider") for p in parameters
    }
    n_intensity_plot_points = 100
    dist_fig_id = dh.component_id(f"{name} definition distribution", "figure")
    interval_fig_id = dh.component_id(f"{name} interval select", "figure")
    interval_start_id = dh.component_id(f"{name} interval start", "slider")
    interval_length_id = dh.component_id(f"{name} interval length", "slider")
    interval_start_slider = dh.labeled_slider(
        bounds[0], bounds[1], "interval start", id=interval_start_id, value=0
    )
    interval_length_slider = dh.labeled_slider(
        0, bounds[1], "interval length", id=interval_length_id
    )

    @callback(Output(interval_length_id, "max"), Input(interval_start_id, "value"))
    def update_interval_length_max(start: float) -> float:
        return bounds[1] - start

    standard_for_callback = [
        Output(interval_fig_id, "figure"),
        Output(dist_fig_id, "figure"),
        Input(interval_start_id, "value"),
        Input(interval_length_id, "value"),
    ]
    model_parameter_inputs = [Input(slider_ids[p.name], "value") for p in parameters]
    # Create callbacks
    @callback(*(standard_for_callback + model_parameter_inputs))
    def update_interval_figure(
        start: float, length: float, *mparams
    ) -> tuple[go.Figure, go.Figure]:
        nonlocal example_process
        example_process = process(*mparams)
        x = np.linspace(bounds[0], bounds[1], n_intensity_plot_points)
        y = example_process.intensity(x)
        fig = go.Figure(data=go.Scatter(x=x, y=y, mode="lines"))

        n_pts_in_interval = math.ceil(
            length / (bounds[1] - bounds[0]) * n_intensity_plot_points
        )
        x2 = np.linspace(start, start + length, n_pts_in_interval)
        y2 = example_process.intensity(x2)
        x2 = np.concatenate([np.array([start]), x2, [start + length, start]])
        y2 = np.concatenate([np.array([0]), y2, np.array([0, 0])])
        fig.add_trace(
            go.Scatter(x=x2, y=y2, fill="toself", line={"width": 0}, mode="lines")
        )
        if y_max:
            fig.update_yaxes(range=[0, y_max], title={"text": "Intensity"})
        else:
            fig.update_yaxes(range=[0, 1.05 * y.max()], title={"text": "Intensity"})
        fig.update_xaxes(range=bounds, title={"text": "Time"})
        fig.update_layout(showlegend=False)
        if plot_title:
            fig.update_layout(
                title={
                    "text": plot_title,
                    "y": 0.9,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                },
            )
        interval_fig = fig

        area = integrate.quad(example_process.intensity, start, start + length)[0]
        fig = poisson_dist_fig(area, min_x_max=20)
        fig.update_xaxes(title={"text": "Number of Events"})
        fig.update_layout(showlegend=False)
        return interval_fig, fig

    intensity_sliders = [
        dh.labeled_slider(p.min, p.max, p.name, id=slider_ids[p.name])
        for p in parameters
    ]
    slider_col = dh.my_col(
        [dh.my_row(slider) for slider in intensity_sliders]
        + [html.Hr(style={"height": "6px"})]
        + [dh.my_row(interval_start_slider), dh.my_row(interval_length_slider)],
        width=3,
        align="center",
    )

    example_row = dh.my_row(
        [
            dh.my_col(
                [
                    dh.my_row(dcc.Graph(id=interval_fig_id, mathjax=True)),
                    dh.my_row(dcc.Graph(id=dist_fig_id, mathjax=True)),
                ],
                width=9,
            ),
            slider_col,
        ]
    )
    return example_row
