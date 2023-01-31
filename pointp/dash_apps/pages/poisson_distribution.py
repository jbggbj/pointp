import plotly.io as pio
import plotly.graph_objs as go
from pointp import simulate
import dash_bootstrap_components as dbc
import math
import numpy as np
import dash
import plotly
import plotly.express as px
from dash import Input, Output, dcc, html, callback
from scipy.stats import poisson
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
        p_dist = poisson(mean)

        x_bins = np.arange(p_dist.ppf(0.995) + 1)
        fig = go.Figure(
            data=go.Bar(name="Poisson", x=x_bins, y=p_dist.pmf(x_bins)),
        )
        fig.update_yaxes(range=[0, 1])
        fig.add_vline(
            x=mean,
            annotation_text="mean",
            line_color="black",
            annotation_position="top",
            opacity=1,
            line_width=2.0,
        )
        fig.update_layout(title="Poisson Distribution")
        return fig

    return example_row


example = p_dist_ex_row()

layout = html.Div([dbc.Container([example])])
