import dash
from dash import dcc, html

# Only use for testing! Will crash after any runtime warning.
# np.seterr(all="raise")  # Raise exception for runtime warnings


dash.register_page(__name__, path="/")

layout = html.Div(
    [
        # html.P("Home page")
        dcc.Markdown(
            """For example, maybe the algorithm identified a shed as a car.
We'll model the algorithm's number of false alarms with a Poisson distribution 
determined by a rate parameter that depends linearly on $n:$
$$z \sim \text{Poisson}(\lambda_{0} + \lambda_{1} n).$$""",
            mathjax=True,
        )
    ]
)
