import webbrowser

import dash_bootstrap_components as dbc
import numpy as np

import pointp.simulate as ps
from pointp.plot import point_process_figure

import plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html, ctx
import dash_helper as dh
from typing import Tuple, Union, Callable
import demo_components as dc

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings

pio.templates.default = "simple_white"

app = Dash(__name__)


class Defaults:
    h_rate_max = 5
    h_x_max = 5
    bin_opacity = 0.7


class ComponentIDs:
    h_fig = dh.component_id("homogeneous", "figure")
    h_rate = dh.component_id("homogeneous_rate", "slider")
    h_button = dh.component_id("homogeneous", "button")
    h_bins = dh.component_id("homogeneous", "n_bins")


h_example_tk = None


def homogeneous_example() -> dbc.Row:
    return dh.my_row(
        [
            dh.my_col([dcc.Graph(id=ComponentIDs.h_fig)], width=9),
            dh.my_col(
                [
                    dh.my_row(
                        dbc.Col(
                            [
                                dh.labeled_slider(
                                    0,
                                    Defaults.h_rate_max,
                                    "rate",
                                    id=ComponentIDs.h_rate,
                                )
                            ]
                        )
                    ),
                    dh.my_row(
                        [dh.my_col(dbc.Button("Generate", id=ComponentIDs.h_button))]
                        # dbc.Button("Generate", id=ComponentIDs.h_button)
                    ),
                    dh.my_row(
                        dh.labeled_slider(
                            1, 20, "# of bins", step=1, id=ComponentIDs.h_bins
                        )
                    ),
                ],
                width=3,
                align="center",
            ),
        ]
    )


@app.callback(
    Output(ComponentIDs.h_fig, "figure"),
    Input(ComponentIDs.h_button, "n_clicks"),
    Input(ComponentIDs.h_rate, "value"),
    Input(ComponentIDs.h_bins, "value"),
)
def update_hom_figure(n_clicks: int, rate: float, n_bins: int) -> go.Figure:
    global h_example_tk
    if ctx.triggered_id != ComponentIDs.h_bins:
        h_example_tk = ps.h_poisson_1d(rate, [0, Defaults.h_x_max])

    fig = point_process_figure(h_example_tk, rate, Defaults.h_x_max, n_bins=n_bins)
    fig.update_layout(
        title={
            "text": "Homogeneous Poisson Process",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )
    return fig


def ex_2_intensity_func(*args) -> Callable[[float], float]:
    def intensity(x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        rate = np.array(args).sum()
        if np.isscalar(x):
            return rate
        else:
            return rate * np.ones_like(x)

    return intensity


def ex_2_draw_func(t_min, t_max, *args) -> np.ndarray:
    return ps.h_poisson_1d(np.array(args).sum(), [t_min, t_max])





def example_2_row() -> dbc.Row:
    model_parameters = [
        dc.ModelParameter("a", 0, 4),
        dc.ModelParameter("b", -1, 2)
    ]

    return dc.pp_example_row("Example 2", model_parameters,
                             ex_2_intensity_func,
                             ex_2_draw_func,
                             t_min=0, t_max=10)


app.layout = html.Div(
    [
        dbc.Container(
            [dh.header("Point Processes"),
             homogeneous_example(),
             example_2_row()
             ],
            style={"height": "100vh"},
        )
    ]
)

if __name__ == "__main__":
    webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="127.0.0.1", port=8050, debug=True)

"""Steps used to kill process if port is left running.
sudo lsof -i -P -n | grep LISTEN

Look in above line for port 8050. Pick process id = <pid> from that and use 
the following:
kill -15 <pid>
"""
