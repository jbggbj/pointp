import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=1)


class PoissonDefaults:
    mu_min = 0
    mu_max = 10


def p_dist_ex_row() -> dbc.Row:
    slider_id = dh.component_id("poisson_mu", "slider")
    slider = dh.labeled_slider(
        PoissonDefaults.mu_min, PoissonDefaults.mu_max, "mean", id=slider_id
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
        return dc.poisson_dist_fig(mean)

    return example_row


layout = html.Div([dbc.Container([p_dist_ex_row()])])
