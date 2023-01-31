import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp.dash_apps import dash_helper as dh
from pointp import simulate

dash.register_page(__name__)

rate = 3.0
# hom_ex_row = dc.pp_definition_row(
#     "Homogeneous Poisson Process", simulate.Homogeneous1D(rate), [0, 10]
# )
#
# inhom_ex_row = dc.pp_definition_row(
#     "Inhomogeneous Poisson Process", simulate.InHomEx2(4, 3), [0, 10]
# )
hom_ex_row = dc.pp_definition_row(
    "Homogeneous Poisson Process", simulate.Homogeneous1D, [0, 10]
)

inhom_ex_row = dc.pp_definition_row(
    "Inhomogeneous Poisson Process",
    simulate.InHomEx2,
    [0, 10],
    plot_title=r"$\lambda (t) = a + \sum_{k}\frac{b}{w} e^{-(t - t_{k})/w}$",
)
layout = html.Div([dbc.Container([hom_ex_row, inhom_ex_row])])
