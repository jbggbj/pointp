import dash
from dash import html

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings

dash.register_page(__name__)

layout = html.Div([html.P("You have quit the server. You may close this window.")])
