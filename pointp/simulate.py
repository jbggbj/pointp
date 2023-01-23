from typing import Callable, Union, List
from collections import namedtuple
from abc import ABC

import numpy as np
from scipy import integrate, optimize
from scipy.stats import poisson, expon
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


print(h_poisson_1d(4, [0, 1]))
print(h_poisson_1d(4, [2, 8]))


def rate_func(x: float) -> float:
    return x


ModelParameter = namedtuple("ModelParameter", ["name", "min", "max"])


class Process1D(ABC):

    model_parameters = List[ModelParameter]

    def __init__(self, *parameters):
        assert len(parameters) == len(self.model_parameters)

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Intensity function that can apply to float or array."""

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points generated by a simulation of the process on [t_min, t_max]."""

    def plot_func(self, tk: np.ndarray, t_max: float, **kwargs):
        return plt.point_process_figure(tk, self.intensity, t_max, **kwargs)




class Homogeneous1D(Process1D):
    model_parameters = [ModelParameter("rate", 0, 5)]

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
    model_parameters = [ModelParameter("a", 0, 10), ModelParameter("b", 0, 5)]

    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def intensity(self, t: np.ndarray) -> np.ndarray:
        return self.a * np.cos(self.b * 2 * np.pi * t) ** 2

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points for inhomogeneous point process."""
        return poisson_process(self.intensity, t_min, t_max, f_max=self.a)


class InHomEx2(Process1D):
    model_parameters = [ModelParameter("a", 0, 10), ModelParameter("w", 0.01, 10)]

    def __init__(self, a: float, w: float):
        self.a = a
        self.w = w

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        return (self.a / self.w) * np.exp(-t/self.w)

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points for inhomogeneous point process."""
        num_pts = poisson(self.a).rvs()
        all_tk = expon(scale=self.w).rvs(size=num_pts)
        return np.sort(all_tk[all_tk <= t_max])


class SelfExciting1D(Process1D):
    model_parameters = [
        ModelParameter("a", 0, 5),
        ModelParameter("b", 0, 1.2),
        ModelParameter("w", 0, 5),
    ]

    event_times = None

    def __init__(self, a: float, b: float, w: float):
        self.background = Homogeneous1D(a)
        self.trigger = InHomEx2(b, w)

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:

        result = self.background.intensity(t)
        for tk in self.event_times:
            delay = t - tk
            result[delay >= 0] += self.trigger.intensity(delay[delay >= 0])
        return result

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        self.event_times = self.background.simulate(t_min, t_max)
        to_trigger = self.event_times.tolist()
        while len(to_trigger) > 0:
            parent_time = to_trigger.pop()
            children_times = parent_time + self.trigger.simulate(0, t_max-parent_time)
            self.event_times = np.append(self.event_times, children_times)
            to_trigger = to_trigger + children_times.tolist()

        self.event_times = np.sort(self.event_times)
        return self.event_times







