from abc import ABC
from collections import namedtuple
from typing import Callable, List, Union

import numpy as np
import plotly.graph_objs as go
from scipy import integrate, optimize
from scipy.stats import expon, poisson

import pointp.plot as plt


def poisson_process(
    rate: Callable[[float], float],
    t_min: float,
    t_max: float,
    f_max: float = None,
    draw: Callable[[int], np.ndarray] = None,
) -> np.ndarray:
    avg_num_pts = integrate.quad(rate, t_min, t_max)[0]
    num_pts = poisson(avg_num_pts).rvs()
    if draw:
        result = draw(num_pts)
    else:
        result = rejection_sampling(rate, t_min, t_max, n_pts=num_pts, f_max=f_max)

    return np.sort(result)


def rejection_sampling(
    f: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    n_pts: int = 1,
    f_max: float = None,
) -> np.ndarray:
    if f_max is None:
        f_max = -optimize.minimize_scalar(lambda t: -f(t), bounds=[a, b])["fun"]

    result = np.array([])

    while result.size < n_pts:
        n_draw = n_pts - result.size
        tentative_x = a + b * np.random.rand(n_draw)
        tentative_y = f_max * np.random.rand(n_draw)
        result = np.append(result, tentative_x[tentative_y < f(tentative_x)])

    return result


def rate_xy(xy: np.ndarray, a: float = 1, b: float = 1) -> np.ndarray:
    # assume size 2 * n for n points
    return np.squeeze(a + b * xy[0, :])


def rate_xy_2(xy: np.ndarray, a: float = 1, b: float = 1) -> np.ndarray:
    # assume size 2 * n for n points
    result = (
        a * np.cos(2 * np.pi * xy[0, :]) ** 2 + b * np.sin(2 * np.pi * xy[0, :]) ** 2
    )
    return np.squeeze(result)


def h_poisson_1d(rate: float, range: [float, float] = [0, 1]) -> np.ndarray:
    num_pts = poisson(rate * (range[1] - range[0])).rvs()
    pts = range[0] + (range[1] - range[0]) * np.random.rand(num_pts)
    return np.sort(pts)


def rate_func(x: float) -> float:
    return x


ModelParameter = namedtuple("ModelParameter", ["name", "min", "max"])


class Process(ABC):

    model_parameters = List[ModelParameter]
    latex_string = ""

    def __init__(self, *parameters):
        assert len(parameters) == len(self.model_parameters)

    def intensity(self, *args) -> Union[float, np.ndarray]:
        """Intensity function that can apply to float or array."""

    def simulate(self, *args) -> np.ndarray:
        """Return points generated by a simulation of the process on [t_min, t_max]."""

    def plot_func(self, *args, **kwargs) -> go.Figure:
        """Returns Plotly Figure."""



class Process1D(Process, ABC):

    model_parameters = List[ModelParameter]

    def __init__(self, *parameters):
        assert len(parameters) == len(self.model_parameters)

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Intensity function that can apply to float or array."""

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points generated by a simulation of the process on [t_min, t_max]."""

    def plot_func(
        self, tk: np.ndarray, t_bounds: tuple[float, float], **kwargs
    ) -> go.Figure:
        return plt.point_process_figure(tk, self.intensity, t_bounds, **kwargs)


class Homogeneous1D(Process1D):
    model_parameters = [ModelParameter("\u03BB", 0, 5)]
    latex_string = r"$\lambda (t) = \lambda$"
    def __init__(self, rate: float):
        self.rate = rate

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        if np.isscalar(t):
            return self.rate
        else:
            return self.rate * np.ones_like(t)

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points generated by a homogeneous poisson process."""
        return h_poisson_1d(self.rate, [t_min, t_max])


class InHomEx1(Process1D):
    model_parameters = [ModelParameter("\u03B1", 0, 10), ModelParameter("\u03C9", 0, 5)]
    latex_string = r"$\lambda (t) = \alpha \cos^2{(2\omega \pi t)}$"

    def __init__(self, amplitude: float, omega: float):
        self.amplitude = amplitude
        self.omega = omega

    def intensity(self, t: np.ndarray) -> np.ndarray:
        return self.amplitude * np.cos(self.omega * 2 * np.pi * t) ** 2

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points for inhomogeneous point process."""
        return poisson_process(self.intensity, t_min, t_max, f_max=self.amplitude)


class InHomEx2(Process1D):
    model_parameters = [ModelParameter("a", 0, 10), ModelParameter("w", 0.01, 10)]
    latex_string = r"$\lambda (t) = \frac{a}{w}e^{-t/w}$"

    def __init__(self, a: float, w: float):
        self.a = a
        self.w = w

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        return (self.a / self.w) * np.exp(-t / self.w)

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points for inhomogeneous point process."""
        num_pts = poisson(self.a).rvs()
        all_tk = expon(scale=self.w).rvs(size=num_pts)
        return np.sort(all_tk[all_tk <= t_max])

# def sepp_intensity(background: Callable[
#     [Union[float, np.ndarray]], Union[float, np.ndarray]], trigger: Callable[
#     [Union[float, np.ndarray]], Union[float, np.ndarray]]) -> Union[float, np.ndarray]:
#     p


class SelfExciting1D(Process1D):
    model_parameters = [
        ModelParameter("a", 0, 5),
        ModelParameter("b", 0, 1.3),
        ModelParameter("w", 0, 5),
    ]

    event_times = None
    generation = None

    def __init__(self, a: float, b: float, w: float):
        self.background = Homogeneous1D(a)
        self.trigger = InHomEx2(b, w)

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:

        result = self.background.intensity(t)
        for tk in self.event_times:
            delay = t - tk
            result[delay >= 0] += self.trigger.intensity(delay[delay >= 0])
        return result

    def simulate(
        self, t_min: float, t_max: float, return_generation: bool = False
    ) -> np.ndarray:
        self.event_times = self.background.simulate(t_min, t_max)
        to_trigger = self.event_times.tolist()
        self.generation = [1] * len(to_trigger)
        to_trigger_gen = self.generation.copy()
        while len(to_trigger) > 0:
            parent_time = to_trigger.pop()
            parent_gen = to_trigger_gen.pop()
            children_times = parent_time + self.trigger.simulate(0, t_max - parent_time)
            children_gen = [parent_gen + 1] * len(children_times)
            self.event_times = np.append(self.event_times, children_times)
            self.generation = self.generation + children_gen
            to_trigger = to_trigger + children_times.tolist()
            to_trigger_gen = to_trigger_gen + children_gen

        order_in_time = np.argsort(self.event_times)
        self.event_times = self.event_times[order_in_time]
        self.generation = np.array(self.generation)[order_in_time]
        if return_generation:
            return self.event_times, self.generation
        else:
            return self.event_times

        return self.event_times


class Process2D(Process):

    model_parameters = List[ModelParameter]

    def __init__(self, *parameters):
        assert len(parameters) == len(self.model_parameters)

    def intensity(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Intensity function that can apply to float or array."""

    def simulate(
        self, x_min: float, x_max: float, y_min: float, y_max: float
    ) -> np.ndarray:
        """Return points generated by a simulation of the process on [t_min, t_max]."""

    def plot_func(self, xyk: np.ndarray, bounds: list[float], **kwargs) -> go.Figure:
        return plt.point_process_fig_2D(
            xyk[0, :], xyk[1, :], self.intensity, bounds, **kwargs
        )


class Homogeneous2D(Process2D):
    model_parameters = [ModelParameter("rate", 0, 20)]

    def __init__(self, rate: float):
        self.rate = rate

    def intensity(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.rate * np.ones_like(x)

    def simulate(
        self, x_min: float, x_max: float, y_min: float, y_max: float
    ) -> np.ndarray:
        area = (x_max - x_min) * (y_max - y_min)
        num_pts = poisson.rvs(self.rate * area)
        xk = x_min + x_max * np.random.rand(num_pts)
        yk = y_min + y_max * np.random.rand(num_pts)

        return np.array([xk, yk])

    def plot_func(self, xyk: np.ndarray, bounds: list[float], **kwargs) -> go.Figure:
        kwargs.setdefault("plot_intensity", False)
        return super().plot_func(xyk, bounds, **kwargs)


class Inhomogeneous2DA(Process2D):
    model_parameters = [
        ModelParameter("a", 0, 20),
        ModelParameter("b", 0, 4),
        ModelParameter("c", 0, 20),
        ModelParameter("d", 0, 4),
    ]

    def __init__(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def intensity(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return (
            self.a * np.cos(self.b * 2 * np.pi * x) ** 2
            + self.c * np.sin(self.d * 2 * np.pi * y) ** 2
        )

    def simulate(
        self, x_min: float, x_max: float, y_min: float, y_max: float
    ) -> np.ndarray:

        num_pts = poisson.rvs(
            integrate.dblquad(self.intensity, x_min, x_max, y_min, y_max)[0]
        )
        return rejection_sampling_2D(
            self.intensity,
            (x_min, x_max),
            (y_min, y_max),
            self.a + self.c,
            n_pts=num_pts,
        )


def rejection_sampling_2D(
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
