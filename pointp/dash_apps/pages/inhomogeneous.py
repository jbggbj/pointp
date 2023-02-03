import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp import simulate
from pointp.dash_apps import dash_helper as dh

dash.register_page(__name__, order=2)

inhom_def_row = dc.pp_definition_row(
    "Inhomogeneous Poisson Process",
    simulate.InHomEx2,
    [0, 10],
    plot_title=r"$\lambda (t) = a + \sum_{k}\frac{b}{w} e^{-(t - t_{k})/w}$",
)

inhom_periodic_row = dc.pp_example_row(
    "Inhomogeneous Example: Periodic",
    simulate.InHomEx1,
    [0, 4],
    plot_title=r"$\lambda (t) = \alpha \cos{(2\omega \pi t)}$",
)


inhom_exponential_row = dc.pp_example_row(
    "Inhomogeneous Example: Exponential",
    simulate.InHomEx2,
    [0, 10],
    plot_title=r"$\lambda (t) = \frac{a}{w}e^{-t/w}$",
)


hom_simulate_row = dc.pp_example_row(
    "Homogeneous Poisson Process",
    simulate.Homogeneous1D,
    [0, 10],
)


class ExampleIDs:
    ex1 = "Inhomogeneous Definition"
    ex2 = "Inhomogeneous Simulation 1"
    ex3 = "Inhomogeneous Simulation 2"


example_list = [
    (ExampleIDs.ex1, inhom_def_row),
    (ExampleIDs.ex2, inhom_exponential_row),
    (ExampleIDs.ex3, inhom_periodic_row),
]

title_row = dh.my_row(
    [
        html.Div(
            [
                html.H1(
                    "Inhomogeneous Poisson Process in 1D",
                    style={"textAlign": "center", "margin-top": "25px"},
                )
            ]
        )
    ]
)
layout = html.Div(
    [dbc.Container([title_row]), dh.page_depending_on_checklist(example_list)]
)
