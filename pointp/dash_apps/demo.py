import webbrowser

import dash_bootstrap_components as dbc
import numpy as np

import pointp.simulate as ps
import plotly
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html, ctx
import dash_helper as dh
from typing import Tuple, Union, Callable

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings

pio.templates.default = "simple_white"

app = Dash(__name__)


class Defaults:
    h_rate_max = 5
    h_x_max = 5
    bin_opacity = 0.7


colors = dh.categoricalColorScheme


class DefaultColors:
    points = colors[0]
    counts = colors[2]
    intensity = colors[4]
    bins = colors[6]


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
                        dh.labeled_slider(
                            0, Defaults.h_rate_max, "rate", id=ComponentIDs.h_rate
                        )
                    ),
                    dh.my_row(
                        [dh.my_col(dbc.Button("Generate", id=ComponentIDs.h_button))]
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


def pp_to_counts(tk: np.ndarray, t_max: float) -> Tuple[np.ndarray, np.ndarray]:
    cts_t = np.concatenate([np.zeros(1), tk, np.array([t_max])])
    cts_y = np.concatenate(
        [np.zeros(1), np.ones_like(tk).cumsum(), np.array([len(tk)])]
    )
    return cts_t, cts_y


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


def intensity_function_scatter(
    intensity: Union[float, Callable[[float], float]],
    t_min: float,
    t_max: float,
    n_pts: int = 200,
) -> go.Scatter:
    x = np.linspace(t_min, t_max, n_pts)
    if np.isscalar(intensity):
        y = intensity * np.ones_like(x)
    else:
        y = intensity(x)

    return go.Scatter(x=x, y=y, mode="lines", name="intensity")


def counts_function_scatter(tk: np.ndarray, t_max: float) -> go.Scatter:
    counts_x, counts_y = pp_to_counts(tk, t_max)
    return go.Scatter(
        x=counts_x,
        y=counts_y,
        mode="lines",
        line={"shape": "hv"},
        name="Counts",
        line_color=DefaultColors.counts,
    )


def point_process_figure(
    tk: np.ndarray,
    intensity: Union[float, Callable[[float], float]],
    t_max: float,
    n_bins: int = 10,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=tk,
            y=np.ones_like(tk),
            mode="markers",
            name="points",
            marker_size=15,
            marker_color=DefaultColors.points,
        )
    )

    fig.add_trace(intensity_function_scatter(intensity, 0, t_max))

    fig.add_trace(counts_function_scatter(tk, t_max))
    bin_width = t_max / n_bins
    fig.add_trace(
        go.Histogram(
            x=tk,
            name="binned",
            xbins={"size": bin_width},
            autobinx=False,
            marker_color=DefaultColors.bins,
            opacity=Defaults.bin_opacity,
        )
    )

    fig.update_xaxes(range=[0, t_max])
    return fig


app.layout = html.Div(
    [
        dbc.Container(
            [dh.header("Point Processes"), homogeneous_example()],
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
