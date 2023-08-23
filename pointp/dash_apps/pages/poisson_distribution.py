import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html
import math

import pointp.dash_apps.demo_components as dc
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=0, path="/")

page_title = "Poisson Distribution"


class PoissonDefaults:
    mu_min = 0
    mu_max = 10
    rate_mult = 3.5


class BinomDefaults:
    n_min = 1
    n_max = 20
    lim_mult = 20


def p_dist_ex_row() -> dbc.Row:
    slider_id = dh.component_id("poisson_mu", "slider")
    slider = dh.labeled_slider(
        PoissonDefaults.mu_min, PoissonDefaults.mu_max, "\u03BC", id=slider_id
    )
    fig_id = dh.component_id("Poisson_dist", "figure")
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id, mathjax=True)], width=9),
            dh.my_col(
                dh.my_row(slider),
                width=3,
                align="center",
            ),
        ]
    )

    @callback(Output(fig_id, "figure"), Input(slider_id, "value"))
    def update_fig(mean: float) -> go.Figure:
        fig = dc.poisson_dist_fig(mean, min_x_max=15, annotation="mean = \u03BC")
        fig.update_layout(
            title={
                "text": r"$k \sim \frac{\mu^k e^{-\mu}}{k!}$",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 30},
            }
        )
        fig.update_xaxes(title=r"k")
        return fig

    return example_row


def b_dist_ex_row() -> dbc.Row:
    n_slider_id = dh.component_id("binom_n", "slider")
    n_slider = dh.labeled_slider(
        BinomDefaults.n_min, BinomDefaults.n_max, "n", step=1, id=n_slider_id
    )

    p_slider_id = dh.component_id("binom_p", "slider")
    p_slider = dh.labeled_slider(0, 1, "p", id=p_slider_id)

    fig_id = dh.component_id("binom_dist", "figure")
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id, mathjax=True)], width=9),
            dh.my_col(
                [dh.my_row(s) for s in [n_slider, p_slider]],
                width=3,
                align="center",
            ),
        ]
    )

    @callback(
        Output(fig_id, "figure"),
        Input(n_slider_id, "value"),
        Input(p_slider_id, "value"),
    )
    def update_fig(n: int, p: float) -> go.Figure:
        fig = dc.binom_dist_fig(n, p, annotation="mean = np")
        fig.update_layout(
            title={
                "text": r"$nk\sim Binom(n, p)$",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 30},
            }
        )
        fig.update_xaxes(title=r"k")
        return fig

    return example_row


def bp_lim_ex_row() -> dbc.Row:
    n_slider_id = dh.component_id("bp_n", "slider")
    n_slider = dh.labeled_slider(2, 10, "n", step=1, id=n_slider_id, value=2)

    rate_slider_id = dh.component_id("rate", "slider")
    rate_slider = dh.labeled_slider(0.01, 10, "rate", id=rate_slider_id, value=1)

    fig_id = dh.component_id("binom_dist", "figure")
    example_row = dh.my_row(
        [
            dh.my_col([dcc.Graph(id=fig_id, mathjax=True)], width=9),
            dh.my_col(
                [dh.my_row(s) for s in [rate_slider, n_slider]],
                width=3,
                align="center",
            ),
        ]
    )

    @callback(
        Output(component_id=n_slider_id, component_property="min"),
        Output(component_id=n_slider_id, component_property="max"),
        Output(component_id=n_slider_id, component_property="value"),
        Output(component_id=n_slider_id, component_property="marks"),
        Input(component_id=rate_slider_id, component_property="value"),
    )
    def update_n_slider(rate: float) -> tuple[int, int, int]:
        n_min, n_max = (
            math.ceil(rate),
            BinomDefaults.lim_mult * math.ceil(rate),
        )
        return n_min, n_max, n_min, {x: str(x) for x in [n_min, n_max]}

    @callback(
        Output(fig_id, "figure"),
        Input(n_slider_id, "value"),
        Input(rate_slider_id, "value"),
    )
    def update_fig(n: int, rate: float) -> go.Figure:
        fig = dc.bp_limit_fig(rate, n)
        fig.update_layout(
            title={
                "text": r"$\text{Binom } \longrightarrow \text{ Poisson}$",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 30},
            }
        )
        fig.update_xaxes(title=r"$k$", range=[-0.5, PoissonDefaults.rate_mult * rate])
        return fig

    return example_row


def n_marks(v_min, v_max) -> dict:
    return {v_min: str(v_min), v_max: str(v_max)}


class ExampleIDs:
    ex1 = "Poisson"
    ex2 = "Binom"
    ex3 = "BP"


example_list = [
    (ExampleIDs.ex1, p_dist_ex_row()),
    (ExampleIDs.ex2, b_dist_ex_row()),
    (ExampleIDs.ex3, bp_lim_ex_row()),
]

layout = html.Div(
    [
        dbc.Container([dh.title_row(page_title)]),
        dh.page_depending_on_checklist(example_list),
    ]
)
