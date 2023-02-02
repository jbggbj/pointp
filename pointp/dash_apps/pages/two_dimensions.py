import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

import pointp.dash_apps.demo_components as dc
from pointp.dash_apps import dash_helper as dh
from pointp import simulate

dash.register_page(__name__, order=3)

hom_2d_row = dc.pp_example_row(
    "Homogeneous 2D", simulate.Homogeneous2D, [0, 2, 0, 1], show_bins=False
)


inhom_2d_row = dc.pp_example_row(
    "Inhomogeneous 2D",
    simulate.Inhomogeneous2DA,
    [0, 2, 0, 1],
    plot_title=r"$\lambda (x, y) = a \cos^2 (2b\pi x) + c \sin^2 (2d\pi y)$",
    show_bins=False,
)


class ExampleIDs:
    ex1 = "Homogeneous 2D"
    ex2 = "Inhomogeneous 2D"


example_list = [
    (ExampleIDs.ex1, hom_2d_row),
    (ExampleIDs.ex2, inhom_2d_row),
]
# inhom_ex_row = dc.pp_definition_row(
#     "Inhomogeneous Poisson Process",
#     simulate.InHomEx2,
#     [0, 10],
#     plot_title=r"$\lambda (t) = a + \sum_{k}\frac{b}{w} e^{-(t - t_{k})/w}$",
# )
title_row = dh.my_row(
    [
        html.Div(
            [
                html.H1(
                    "Poisson Process in 2D",
                    style={"textAlign": "center", "margin-top": "25px"},
                )
            ]
        )
    ]
)
layout = html.Div(
    [dbc.Container([title_row]), dh.page_depending_on_checklist(example_list)]
)
