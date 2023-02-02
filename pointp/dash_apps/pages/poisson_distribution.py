import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=0, path="/")

page_title = "Poisson Distribution"


class PoissonDefaults:
    mu_min = 0
    mu_max = 10


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
                "text": r"$n \sim \frac{\mu^n e^{-\mu}}{n!}$",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 30},
            }
        )
        fig.update_xaxes(title=r"n")
        return fig

    return example_row


layout = html.Div([dbc.Container([dh.title_row(page_title), p_dist_ex_row()])])
