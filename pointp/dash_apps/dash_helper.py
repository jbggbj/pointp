import os
import signal
from typing import Tuple, Union

import dash.exceptions
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output, callback, dcc, html

DEFAULT_COLUMN_WIDTH = 5
DEFAULT_CLASS_NAME = "mt-4"

# TODO: Problem if more than one quit button created -- leads to multiple callbacks with
# the same id

categoricalColorScheme = np.array(
    [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]
)


def unique_component_id_factory(first_id: int):
    n = first_id

    def unique_component_id(name: str, component: str) -> str:
        nonlocal n
        result = f"{n}_{name}_{component}"
        n += 1
        return result

    return unique_component_id


component_id = unique_component_id_factory(0)


def my_col(*args, **kwargs) -> dbc.Col:
    kwargs.setdefault("width", DEFAULT_COLUMN_WIDTH)
    kwargs.setdefault("className", DEFAULT_CLASS_NAME)
    return dbc.Col(*args, **kwargs)


def my_row(*args, **kwargs) -> dbc.Row:
    kwargs.setdefault("justify", "evenly")
    return dbc.Row(*args, **kwargs)


def labeled_slider(minimum: float, maximum: float, label: str, **kwargs) -> html.Div:
    return html.Div([label, my_slider(minimum, maximum, **kwargs)])


def my_slider(
    minimum: float, maximum: float, step: float = None, n_steps: int = 50, **kwargs
) -> dcc.Slider:

    if step is None:
        step = (maximum - minimum) / n_steps

    kwargs.setdefault("value", 0.5 * (maximum + minimum))
    kwargs.setdefault(
        "marks",
        {
            _slider_bug_fixer(minimum): str(minimum),
            _slider_bug_fixer(maximum): str(maximum),
        },
    )
    kwargs.setdefault("tooltip", {"placement": "bottom", "always_visible": True})
    kwargs.setdefault("persistence", True)

    slider = dcc.Slider(minimum, maximum, step, **kwargs)
    return slider


def _slider_bug_fixer(x: Union[float, int]) -> Union[float, int]:
    """Deals with weird marker bug for Dash sliders"""
    if int(x) == x:
        return int(x)
    else:
        return x


def quit_button(href: str = None) -> html.Div:
    button_unclicked_color = "success"
    button_clicked_color = "danger"
    quit_button_text = "Quit"
    quit_button = dbc.Button(
        quit_button_text,
        color=button_unclicked_color,
        id="shutdown_button",
        # href=dash.page_registry["pages.quit"]["path"],
        n_clicks=0,
    )

    @callback(
        Output(component_id="shutdown_button", component_property="color"),
        Output(component_id="shutdown_button", component_property="children"),
        Input(component_id="shutdown_button", component_property="n_clicks"),
    )
    def kill_app_start(button_clicks: int) -> Tuple[str, str]:
        if button_clicks > 0:
            return button_clicked_color, "Not running."
        return button_unclicked_color, quit_button_text

    @callback(
        Output(component_id="shutdown_button", component_property="disabled"),
        Input(component_id="shutdown_button", component_property="color"),
    )
    def kill_app_finish(button_color: str) -> bool:
        if button_color == button_clicked_color:
            os.kill(os.getpid(), signal.SIGTERM)
            raise dash.exceptions.PreventUpdate
            return True
        else:
            return False

    return html.Div(
        [quit_button],
        # className="d-grid gap-2 col-6 mx-auto",
    )


def header(title: str) -> dbc.Row:
    """Standard header that includes title and a quit button."""
    return my_row(
        [
            # For info on className, go to:
            # https://getbootstrap.com/docs/5.1/utilities/spacing/
            my_col(
                html.H2(children=title, style={"text-align": "center"}),
                width=11,
            ),
            my_col(quit_button(), width=1),
        ],
        justify="evenly",
        style={"height": "9%"},
    )


def page_depending_on_checklist(example_list) -> html.Div:

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

    return html.Div(
        [
            dbc.Container(
                [
                    my_row([my_col(to_show_checklist)]),
                ]
            ),
            dbc.Container(
                id="basic_container",
                style={"height": "100vh"},
            ),
        ]
    )
