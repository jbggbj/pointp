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
    ex3 = "SEPP: Hawkes Process"
    ex4 = "Inhomogeneous: gamma"
    ex5 = "SEPP: gamma trigger"
    ex6 = "SEPP: periodic background"
    # ex7 = "TEST"


hawkes_example = dc.sepp_example_row(
    "SEPP: Hawkes",
    sepp_class_1d(simulate.Homogeneous1D, ExponentialTrigger),
    [0, 10],
    # plot_title=r"$$\lambda (t) = a + \sum_{t_k \leq t}\frac{b}{w} e^{-(t - t_{k})/w}$$",
)

gamma_trigger_example = dc.pp_example_row(
    "Inhomogeneous: gamma",
    GammaTrigger,
    [0, 10]
)


sepp_gamma_example = dc.sepp_example_row(
    ExampleIDs.ex5,
    sepp_class_1d(simulate.Homogeneous1D, GammaTrigger),
    [0, 10],
    # plot_title=r"$$\lambda (t) = a + \sum_{t_k \leq t}\frac{b}{w} e^{-(t - t_{k})/w}$$",
)

sepp_periodic_example = dc.sepp_example_row(
    ExampleIDs.ex6,
    sepp_class_1d(simulate.InHomEx1, ExponentialTrigger),
    [0, 8]

)

# test_new_sepp_row = dc.sepp_example_row(
#     ExampleIDs.ex7,
#     sepp_class_1d(simulate.Homogeneous1D, ExponentialTrigger),
#     [0, 10]
# )

example_list = [
    (ExampleIDs.ex3, hawkes_example),
    (ExampleIDs.ex4, gamma_trigger_example),
    (ExampleIDs.ex5, sepp_gamma_example),
    (ExampleIDs.ex6, sepp_periodic_example),
    # (ExampleIDs.ex7, test_new_sepp_row)
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
