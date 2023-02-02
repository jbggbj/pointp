import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp import simulate
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=4)


class ExampleIDs:
    ex1 = "Homogeneous Poisson"
    ex2 = "Inhomogeneous Poisson"
    ex3 = "SEPP: Hawkes Process"


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

hawkes_example = dc.pp_example_row(
    "SEPP",
    simulate.SelfExciting1D,
    [0, 10],
    plot_title=r"$$\lambda (t) = a + \sum_{t_k \leq t}\frac{b}{w} e^{-(t - t_{k})/w}$$",
)


example_list = [
    (ExampleIDs.ex1, hom_def),
    (ExampleIDs.ex2, inhom_def_row),
    (ExampleIDs.ex3, hawkes_example),
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
