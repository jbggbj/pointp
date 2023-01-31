import dash
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html

from pointp.dash_apps.dash_helper import quit_button

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings

pio.templates.default = "simple_white"
app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
APP_BRAND = "Point Processes"

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem(f"{page['name']}", href=page["relative_path"])
        for page in dash.page_registry.values()
        if not page["name"] in ["Home", "Quit"]
    ],
    nav=True,
    in_navbar=True,
    label="Explore",
)

# button_unclicked_color = "success"
# button_clicked_color = "danger"
# quit_button_text = "Quit"
# quit_button = dbc.Button(
#     quit_button_text,
#     color=button_unclicked_color,
#     id="shutdown_button",
#     href=dash.page_registry["pages.quit"]["path"],
#     n_clicks=0,
# )
# button_html = html.Div(
#     [quit_button],
#     # className="d-grid gap-2 col-6 mx-auto",
# )


def Navbar():

    layout = html.Div(
        [
            dbc.NavbarSimple(
                # children=[
                #  dbc.NavItem(
                #      dbc.NavLink(f"{page['name']}", href=page["relative_path"])
                #  )for page in dash.page_registry.values()
                # ],
                children=[dropdown, quit_button()],
                brand=APP_BRAND,
                brand_href=dash.page_registry["pages.home"]["path"],
                color="dark",
                dark=True,
            ),
        ]
    )
    return layout


app.layout = html.Div(
    [
        # dcc.Location(id='url', refresh=False),
        Navbar(),
        # html.Div(id='page-content', children=[]),
        # html.Div(id='page-content', children=[]),
        dash.page_container,
    ]
)


# @app.callback(
#     Output(component_id="shutdown_button", component_property="color"),
#     Output(component_id="shutdown_button", component_property="children"),
#     Input(component_id="shutdown_button", component_property="n_clicks"),
# )
# def kill_app_start(button_clicks: int) -> Tuple[str, str]:
#     if button_clicks > 0:
#         return button_clicked_color, "You have quit the server."
#     return button_unclicked_color, quit_button_text

#
# @app.callback(
#     Output(component_id="shutdown_button", component_property="disabled"),
#     Input(component_id="shutdown_button", component_property="color"),
# )
# def kill_app_finish(button_color: str) -> bool:
#     if button_color == button_clicked_color:
#         os.kill(os.getpid(), signal.SIGTERM)
#         return True
#     else:
#         return False


def main():
    # webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="127.0.0.1", port=8050, debug=True)


if __name__ == "__main__":
    main()

"""Steps used to kill process if port is left running.
sudo lsof -i -P -n | grep LISTEN

Look in above line for port 8050. Pick process id = <pid> from that and use 
the following:
kill -15 <pid>
"""
