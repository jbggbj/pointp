import math
from collections import namedtuple
from typing import Callable, List

import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, callback, ctx, dcc, html
from scipy import integrate
from scipy.stats import poisson, binom

import pointp.dash_apps.dash_helper as dh
import pointp.plot
import pointp.simulate as ps
from pointp import simulate
from pointp.plot import point_process_figure


def process_sliders(process: ps.Process, name: str) -> tuple[dict, dict]:
    """Return slider_ids, sliders"""
    slider_ids = {
        p.name: dh.component_id(f"{name}_{p.name}", "slider")
        for p in process.model_parameters
    }
    sliders = [
        dh.labeled_slider(p.min, p.max, p.name, id=slider_ids[p.name])
        for p in process.model_parameters
    ]

    return slider_ids, sliders


def styled_plot_title(text: str) -> dict:
    return {
        "text": text,
        "y": 0.9,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    }


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
        plot_title = process.latex_string
    pts = np.ndarray([])
    example_process = None
    parameters = process.model_parameters
    fig_id = dh.component_id(name, "fig")
    button_id = dh.component_id(name, "button")
    bin_slider_id = dh.component_id(name + "_bins", "slider")

    slider_ids, sliders = process_sliders(process, name)
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

            fig.update_layout(title=styled_plot_title(plot_title))
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

            fig.update_layout(title=styled_plot_title(plot_title))

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


def binom_dist_fig(
    n: int, p: float, annotation: str = "mean"
) -> go.Figure:
    dist = binom(n, p)

    x_bins = np.arange(n + 1)
    fig = go.Figure(
        data=go.Bar(name="Binnom", x=x_bins, y=dist.pmf(x_bins)),
    )
    fig.update_yaxes(range=[0, 1])
    fig.add_vline(
        x=dist.mean(),
        annotation_text=annotation,
        line_color="black",
        annotation_position="top",
        opacity=1,
        line_width=2.0,
    )
    fig.update_layout(title="Binomial Distribution")
    fig.update_yaxes(title={"text": "Probability"})
    return fig

def bp_limit_fig(
    rate: float, n: int, annotation: str = "mean"
) -> go.Figure:
    pdist = poisson(rate)
    p = rate / n
    bdist = binom(n, p)
    max_n = rate * 5
    x_bins = np.arange(max_n + 1)
    fig = go.Figure(
        data=go.Bar(name="B(n, rate/n)", x=x_bins, y=bdist.pmf(x_bins)),
    )
    fig.add_trace(go.Bar(name="P(rate)", x=x_bins, y=pdist.pmf(x_bins)))
    # fig.update_yaxes(range=[0, 1])
    fig.add_vline(
        x=pdist.mean(),
        annotation_text=annotation,
        line_color="black",
        annotation_position="top",
        opacity=1,
        line_width=2.0,
    )
    fig.update_layout(title=r"Binomial $\longrightarrow Poisson")
    fig.update_xaxes(title={r"text": "k"})
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
    slider_ids, intensity_sliders = process_sliders(process, name)
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
            fig.update_layout(title=styled_plot_title(plot_title))
        interval_fig = fig

        area = integrate.quad(example_process.intensity, start, start + length)[0]
        fig = poisson_dist_fig(area, min_x_max=20)
        fig.update_xaxes(title={"text": "Number of Events"})
        fig.update_layout(showlegend=False)
        return interval_fig, fig

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


def sepp_example_row(
    name: str,
    process: "simulate.Process1D",
    bounds: list,
    background_plot_title: str = None,
    trigger_plot_title: str = None,
    points_plot_title: str = None,
) -> dbc.Row:
    pts = np.ndarray([])
    generations = np.ndarray([])
    example_process = None
    line_break = html.Hr(style={"height": "3px"})

    class FigName:
        bk = "background"
        tr = "trigger"
        pr = "process"

    background_parameters = process.background.model_parameters
    trigger_parameters = process.trigger.model_parameters
    figures = [FigName.bk, FigName.tr, FigName.pr]
    fig_ids = {f: dh.component_id(f"{name} {f}", "fig") for f in figures}

    slider_ids, sliders = {}, {}
    slider_ids[FigName.bk], sliders[FigName.bk] = process_sliders(
        process.background, name
    )
    slider_ids[FigName.tr], sliders[FigName.tr] = process_sliders(process.trigger, name)

    slider_rows = {
        f: [dh.my_row(slider) for slider in sliders[f]]
        for f in [FigName.bk, FigName.tr]
    }
    outputs = [
        Output(fig_ids[FigName.bk], "figure"),
        Output(fig_ids[FigName.tr], "figure"),
        Output(fig_ids[FigName.pr], "figure"),
    ]
    model_parameter_inputs = [
        Input(slider_ids[FigName.bk][p.name], "value") for p in background_parameters
    ]
    model_parameter_inputs += [
        Input(slider_ids[FigName.tr][p.name], "value") for p in trigger_parameters
    ]
    button_id = dh.component_id(name, "button")
    button_row = dh.my_row([dh.my_col(dbc.Button("Generate", id=button_id))])

    @callback(*(outputs + [Input(button_id, "n_clicks")] + model_parameter_inputs))
    def update_fig(n_clicks, *mparams) -> tuple[go.Figure, go.Figure]:
        nonlocal pts
        nonlocal example_process
        example_process = process(*mparams)
        tk, genk = example_process.simulate(*bounds, return_generation=True)
        figs = {
            FigName.bk: go.Figure(),
            FigName.tr: go.Figure(),
            FigName.pr: pointp.plot.sepp_figure(
                tk, example_process.intensity, bounds, generation=genk
            ),
        }

        figs[FigName.bk].add_trace(
            pointp.plot.intensity_function_scatter(
                example_process.background.intensity, bounds[0], bounds[1]
            )
        ).update_layout(
            title=styled_plot_title(example_process.background.latex_string)
        )
        figs[FigName.tr].add_trace(
            pointp.plot.intensity_function_scatter(
                example_process.trigger.intensity, bounds[0], bounds[1]
            )
        ).update_layout(
            title=styled_plot_title(example_process.trigger.latex_string)
        )

        for figure in figs.values():
            figure.update_xaxes(title="Time")

        return figs[FigName.bk], figs[FigName.tr], figs[FigName.pr]
        # if ctx.triggered_id != bin_slider_id:
        #     example_process = process(*mparams)
        #     pts = example_process.simulate(*bounds)
        # fig = example_process.plot_func(pts, bounds, n_bins=n_bins)
        # fig.update_layout(
        #     title={
        #         "text": plot_title,
        #         "y": 0.9,
        #         "x": 0.5,
        #         "xanchor": "center",
        #         "yanchor": "top",
        #     },
        # )
        # return fig

    example_row = dbc.Container(
        [
            dh.my_row(
                [
                    dh.my_col(
                        [dcc.Graph(id=fig_ids[FigName.bk], mathjax=True)], width=5
                    ),
                    dh.my_col(
                        [dcc.Graph(id=fig_ids[FigName.tr], mathjax=True)], width=5
                    ),
                    dh.my_col(
                        [dh.my_row(html.P("Background:"))]
                        + slider_rows[FigName.bk]
                        + [dh.my_row(line_break), dh.my_row(html.P("Trigger:"))]
                        + slider_rows[FigName.tr],
                        width=2,
                        align="center",
                    ),
                ]
            ),
            dh.my_row(
                [
                    dh.my_col(
                        [dcc.Graph(id=fig_ids[FigName.pr], mathjax=True)], width=10
                    ),
                    dh.my_col(button_row, width=2, align="center"),
                ]
            ),
        ]
    )

    return example_row
