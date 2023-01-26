import webbrowser
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import numpy as np

import pointp.simulate as ps
from pointp import simulate
from pointp.plot import point_process_figure

import plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html, ctx
import pointp.dash_apps.dash_helper as dh
from typing import Tuple, Union, Callable
import pointp.dash_apps.demo_components as dc

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings

pio.templates.default = "simple_white"

# app = Dash(__name__)
app = None

def example_1_row() -> dbc.Row:
    return dc.pp_example_row(
        "Homogeneous Poisson Process",
        simulate.Homogeneous1D,
        [0, 10],
    )


def example_2_row() -> dbc.Row:
    return dc.pp_example_row(
        "Inhomogeneous_Example_1",
        simulate.InHomEx1,
        [0, 4],
        plot_title=r"$\lambda (t) = a \cos{(2b\pi t)}$",
    )


def example_3_row() -> dbc.Row:
    return dc.pp_example_row(
        "Inhomogeneous_Exponential",
        simulate.InHomEx2,
        [0, 10],
        plot_title=r"$\lambda (t) = \frac{a}{w}e^{-t/w}$",
    )


def sepp_example_row() -> dbc.Row:
    return dc.pp_example_row(
        "SEPP",
        simulate.SelfExciting1D,
        [0, 10],
        plot_title=r"$\lambda (t) = a + \sum_{k}\frac{b}{w} e^{-(t - t_{k})/w}$",
    )


def hom_2d() -> dbc.Row:
    return dc.pp_example_row("Homogeneous", simulate.Homogeneous2D, [0, 2, 0, 1])


def inhom_2d_a() -> dbc.Row:
    return dc.pp_example_row("Inhom_2d_a", simulate.Inhomogeneous2DA, [0, 2, 0, 1],
                             plot_title=r"$\lambda (x, y) = a \cos^2 (2b\pi x) + c \sin^2 (2d\pi y)$",)

examples = [
    example_1_row(),
    html.Hr(style={"height": "3px"}),
    example_2_row(),
    html.Hr(style={"height": "3px"}),
    example_3_row(),
    html.Hr(style={"height": "3px"}),
]
def layout() -> html.Div:

    return html.Div(
        [
            dbc.Container(
                [
                    dh.header("Point Processes"),
                    dh.my_row([dh.my_col(dcc.RadioItems(
                        options=['New York City', 'Montreal', 'San Francisco'],
                        value='Montreal',
                        inline=True
                    ))]),
                    *examples
                    # example_1_row(),
                    # html.Hr(style={"height": "3px"}),
                    # example_2_row(),
                    # html.Hr(style={"height": "3px"}),
                    # example_3_row(),
                    # html.Hr(style={"height": "3px"}),
                    # sepp_example_row(),
                    # html.Hr(style={"height": "3px"}),
                    # hom_2d(),
                    # html.Hr(style={"height": "3px"}),
                    # inhom_2d_a(),
                ],
                style={"height": "100vh"},
            )
        ]
    )


def j_main(port=8050):
    global app
    app = JupyterDash(__name__)
    app.layout = layout()
    app.run_server(mode="jupyterlab", host="127.0.0.1", port=port)


def main():
    global app
    app = Dash(__name__)
    app.layout = layout()
    webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="0.0.0.0", port=8050, debug=False)


def debug():
    global app
    app = Dash(__name__)
    app.layout = layout()
    webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="127.0.0.1", port=8050, debug=True)


if __name__ == "__main__":
    debug()

"""Steps used to kill process if port is left running.
sudo lsof -i -P -n | grep LISTEN

Look in above line for port 8050. Pick process id = <pid> from that and use 
the following:
kill -15 <pid>
"""
