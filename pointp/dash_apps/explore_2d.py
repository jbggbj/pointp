from typing import Callable
import numpy as np
from scipy import optimize

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd


def rejection_sampling(
    f: Callable[[np.ndarray, np.ndarray], np.ndarray],
    xbounds: tuple,
    ybounds: tuple,
    f_max: float,
    n_pts: int = 1,
) -> np.ndarray:
    # if f_max is None:
    #     f_max = -optimize.minimize_scalar(lambda t: -f(t), bounds=[a, b])["fun"]

    result = np.array([[], []])

    while result.shape[1] < n_pts:

        n_draw = n_pts - result.shape[1]

        tentative_x = xbounds[0] + xbounds[1] * np.random.rand(n_draw)
        tentative_y = ybounds[0] + ybounds[1] * np.random.rand(n_draw)
        tentative_z = f_max * np.random.rand(n_draw)
        accept = tentative_z <= f(tentative_x, tentative_y)
        new_pts = np.array([tentative_x[accept], tentative_y[accept]])

        result = np.append(result, new_pts, axis=1)

    return result


def func(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    if x.shape != y.shape:
        raise ValueError("x and y should have the same shape.")
    return 2 * np.ones_like(x)


answer = rejection_sampling(func, (0, 1), (0, 1), 2, n_pts=20)


def func2(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    a = 1
    b = 2
    c = 2
    d = 1
    return a * np.cos(b * 2 * np.pi * x) ** 2 + c * np.sin(d * 2 * np.pi * y) ** 2


xy = rejection_sampling(func2, (0, 1), (0, 1), 3, n_pts=2000)
df = pd.DataFrame(data={"x": xy[0, :], "y": xy[1, :]})

# fig = px.scatter(df, x="x", y="y")


def points_plot_2D(xk: np.ndarray, yk: np.ndarray) -> go.Scatter:

    return go.Scatter(
        x=xk,
        y=yk,
        mode="markers",
        name="points",
        marker_size=15,
        marker_color="black",
    )


def point_process_fig_2D(
    xk: np.ndarray,
    yk: np.ndarray,
    intensity: Callable[[np.ndarray, np.ndarray], np.ndarray],
    xbounds: tuple,
    ybounds: tuple,
    plot_points=True,
    plot_intensity=True,
) -> go.Figure:
    fig = go.Figure()

    if plot_points:
        fig.add_trace(points_plot_2D(xk, yk))

    if plot_intensity:
        fig.add_trace(plot_contours(intensity, xbounds, ybounds))

    return fig


def plot_contours(
    intensity: Callable[[np.ndarray, np.ndarray], np.ndarray],
    xbounds: tuple,
    ybounds: tuple,
) -> go.Contour:
    x = np.linspace(xbounds[0], xbounds[1], 200)
    y = np.linspace(ybounds[0], ybounds[1], 200)
    X, Y = np.meshgrid(x, y)
    Z = intensity(X, Y)

    return go.Contour(
        z=Z,
        x=x,
        y=y
    )

#
# x = np.linspace(0, 1, 100)
# y = np.linspace(0, 1, 100)
# X, Y = np.meshgrid(x, y)
# Z = func2(X, Y)
# fig = go.Figure(data=go.Contour(z=Z, x=x, y=y))
# fig.add_trace(points_plot_2D(xy[0, :], xy[1, :]))
# fig.show()
fig = point_process_fig_2D(xy[0, :], xy[1, :], func2, (0, 1), (0, 1))
fig.show()

