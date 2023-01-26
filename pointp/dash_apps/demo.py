import webbrowser

import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, Input, Output, ctx, dcc, html, callback
from jupyter_dash import JupyterDash

import pointp.dash_apps.dash_helper as dh
import pointp.dash_apps.demo_components as dc
from pointp import simulate

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
    return dc.pp_example_row(
        "Inhom_2d_a",
        simulate.Inhomogeneous2DA,
        [0, 2, 0, 1],
        plot_title=r"$\lambda (x, y) = a \cos^2 (2b\pi x) + c \sin^2 (2d\pi y)$",
    )


class ExampleIDs:
    ex1 = "Homogeneous"
    ex2 = "Inhomogeneous 1"
    ex3 = "Inhomogeneous 2"
    ex4 = "Homogeneous 2D"
    ex5 = "Inhomogeneous 2D"
    ex6 = "SEPP"


example_list = [
    (ExampleIDs.ex1, example_1_row()),
    (ExampleIDs.ex2, example_2_row()),
    (ExampleIDs.ex3, example_3_row()),
    (ExampleIDs.ex4, hom_2d()),
    (ExampleIDs.ex5, inhom_2d_a()),
    (ExampleIDs.ex6, sepp_example_row())

]
line_break = html.Hr(style={"height": "3px"})

example_dict = {item[0]: [item[1], line_break] for item in example_list}

to_show_checklist = dcc.Dropdown(
    [item[0] for item in example_list],
    [example_list[0][0]],
    multi=True,
    id="example_select",
)


@callback(Output("basic_container", "children"), Input("example_select", "value"))
def update_display(items: list) -> list:
    result = []
    for item in items:
        result.extend(example_dict[item])
    return result


def layout() -> html.Div:

    return html.Div(
        [
            dbc.Container(
                [
                    dh.header("Point Processes"),
                    # to_show_checklist
                    dh.my_row([dh.my_col(to_show_checklist)]),
                ]
            ),
            dbc.Container(
                id="basic_container",
                style={"height": "100vh"},
            ),
        ]
    )


def j_main(port=8050):
    global app
    app = JupyterDash(__name__)
    app.layout = layout()
    app.run_server(mode="jupyterlab", host="127.0.0.1", port=port)


def main():
    global app
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = layout()
    webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="0.0.0.0", port=8050, debug=False)


def debug():
    global app
    app = Dash(__name__, suppress_callback_exceptions=True)
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
