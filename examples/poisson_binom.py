import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import binom, poisson

rate = 1

p_dist = poisson(rate)
x_max = p_dist.ppf(0.995)

n_bins = 3

binom_p = min(rate / n_bins, 1.0)
b_dist = binom(n_bins, binom_p)
x_bins = np.arange(max(x_max, b_dist.ppf(0.995)) + 1)
fig = go.Figure(
    data=[
        go.Bar(name="Poisson", x=x_bins, y=p_dist.pmf(x_bins)),
        go.Bar(name="Binomial", x=x_bins, y=b_dist.pmf(x_bins)),
    ]
)
fig.update_layout(barmode="group")
fig.write_html("test.html")
