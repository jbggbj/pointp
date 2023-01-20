import webbrowser

import dash_bootstrap_components as dbc

import plotly
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
import dash_helper as dh
# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings


app = Dash(__name__)

class Defaults:
    h_rate_max = 5
    h_x_max = 5


class ComponentIDs:
    h_fig = dh.component_id("homogeneous", "figure")
    h_rate = dh.component_id("homogeneous_rate", "slider")
    h_button = dh.component_id("homogeneous", "button")


def homogeneous_example() -> dbc.Row:
    return dh.my_row(
        [
            dh.my_col([dcc.Graph(id=ComponentIDs.h_fig)], width=9),
            dh.my_col(
                [
                    dh.my_row(
                        dh.labeled_slider(0, Defaults.h_rate_max, "rate",
                                          id=ComponentIDs.h_rate)),
                    dh.my_row([dh.my_col(
                        dbc.Button("Generate", id=ComponentIDs.h_button)
                    )])
                ],
                width=3
            )
        ]
    )


app.layout = html.Div(
    [
        dbc.Container(
            [
                homogeneous_example()
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
