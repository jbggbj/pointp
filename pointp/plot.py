import numpy as np

import plotly.graph_objs as go
import dash_apps.dash_helper as dh
from typing import Union, Callable
from tools import pp_to_counts


class Defaults:
    bin_opacity = 0.65
    bargap = 0.0


colors = dh.categoricalColorScheme
# colors =["black", "gray", "forestgreen", "#4F94CD"]


class DefaultColors:
    points = "black"
    counts = "#CCCCCC"
    intensity = "#228B22"
    bins = "#4F94CD"


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

    return go.Scatter(
        x=x, y=y, mode="lines", name="intensity", line_color="#228B22", line_width=3
    )


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


def bins_plot(tk: np.ndarray, t_max: float, n_bins: int) -> go.Histogram:
    bin_width = t_max / n_bins
    return go.Histogram(
        x=tk,
        name="binned",
        xbins={"size": bin_width},
        autobinx=False,
        marker_color=DefaultColors.bins,
        opacity=Defaults.bin_opacity,
        # bar_gap=0.1
    )


def points_plot(tk: np.ndarray) -> go.Scatter:
    return go.Scatter(
        x=tk,
        y=np.ones_like(tk),
        mode="markers",
        name="points",
        marker_size=15,
        marker_color=DefaultColors.points,
    )


def point_process_figure(
    tk: np.ndarray,
    intensity: Union[float, Callable[[float], float]],
    t_max: float,
    n_bins: int = 10,
    plot_points=True,
    plot_intensity=True,
    plot_counts=True,
    plot_bins=True,
) -> go.Figure:
    fig = go.Figure()

    if plot_points:
        fig.add_trace(points_plot(tk))
    if plot_intensity:
        fig.add_trace(intensity_function_scatter(intensity, 0, t_max))
    if plot_counts:
        fig.add_trace(counts_function_scatter(tk, t_max))
    if plot_bins:
        fig.add_trace(bins_plot(tk, t_max, n_bins))
        fig.update_layout(bargap=Defaults.bargap)
    fig.update_layout(uirevision="True")
    fig.update_xaxes(range=[0, t_max])
    return fig
