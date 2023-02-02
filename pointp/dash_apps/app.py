import dash
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html

from pointp.dash_apps.dash_helper import quit_button

# __________________________________________________________________
# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings
# -------------------------------------------------------------------

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


def Navbar():

    layout = html.Div(
        [
            dbc.NavbarSimple(
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
        Navbar(),
        dash.page_container,
    ]
)


def debug():
    app.run_server(host="127.0.0.1", port=8050, debug=True)


def main():
    # webbrowser.open_new_tab("http://127.0.0.1:8050/")
    app.run_server(host="0.0.0.0", port=8050, debug=False)


if __name__ == "__main__":
    debug()

"""Steps used to kill process if port is left running.
sudo lsof -i -P -n | grep LISTEN

Look in above line for port 8050. Pick process id = <pid> from that and use 
the following:
kill -15 <pid>
"""
