import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html


import pointp.dash_apps.demo_components as dc
from pointp import simulate
from pointp.sepp import sepp_class_1d, ExponentialTrigger, GammaTrigger
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=4)


class ExampleIDs:
    ex1 = "Homogeneous Poisson"
    ex2 = "Inhomogeneous Poisson"


hom_def = dc.pp_definition_row(
    ExampleIDs.ex1,
    simulate.Homogeneous1D,
    [0, 10],
    plot_title="Homogeneous Poisson depends on interval length only.",
)


inhom_def_row = dc.pp_definition_row(
    ExampleIDs.ex2,
    simulate.InHomEx2,
    [0, 10],
    plot_title=r"Inhomogeneous Poisson depends on interval length and location only.",
)

example_list = [
    (ExampleIDs.ex1, hom_def),
    (ExampleIDs.ex2, inhom_def_row),
]

title_row = dh.my_row(
    [
        html.Div(
            [
                html.H1(
                    "Self-Exciting Point Process in 1D",
                    style={"textAlign": "center", "margin-top": "25px"},
                )
            ]
        )
    ]
)
layout = html.Div(
    [dbc.Container([title_row]), dh.page_depending_on_checklist(example_list)]
)
