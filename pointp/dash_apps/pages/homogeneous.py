import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp import simulate
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=1)

page_title = "Homogeneous Poisson Process in 1D"

hom_def_row = dc.pp_definition_row(
    "Homogeneous Poisson Process", simulate.Homogeneous1D, [0, 10], y_max=5
)

hom_simulate_row = dc.pp_example_row(
    "Homogeneous Poisson Process",
    simulate.Homogeneous1D,
    [0, 10],
)


class ExampleIDs:
    ex1 = "Homogeneous Definition"
    ex2 = "Homogeneous Simulation"


example_list = [
    (ExampleIDs.ex1, hom_def_row),
    (ExampleIDs.ex2, hom_simulate_row),
]
# inhom_ex_row = dc.pp_definition_row(
#     "Inhomogeneous Poisson Process",
#     simulate.InHomEx2,
#     [0, 10],
#     plot_title=r"$\lambda (t) = a + \sum_{k}\frac{b}{w} e^{-(t - t_{k})/w}$",
# )
# title_row = dh.my_row(
#     [html.Div([html.H1("Homogeneous Poisson Process in 1D",
#                        style={"textAlign": "center", "margin-top": "25px"})])]
# )
layout = html.Div(
    [
        dbc.Container([dh.title_row(page_title)]),
        dh.page_depending_on_checklist(example_list),
    ]
)
