from typing import Callable, Union

import numpy as np
from scipy import integrate, optimize
from scipy.stats import poisson


def poisson_process(
    rate: Callable[[float], float],
    a: float,
    b: float,
    f_max: float = None,
    draw: Callable[[int], np.ndarray] = None,
) -> np.ndarray:
    avg_num_pts = integrate.quad(rate, a, b)[0]
    num_pts = poisson(avg_num_pts).rvs()
    if draw:
        result = draw(num_pts)
    else:
        result = rejection_sampling(rate, a, b, n_pts=num_pts, f_max=f_max)

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


def rate(
    t: Union[float, np.ndarray], a: float = 1.0, b: float = 1.0
) -> Union[float, np.ndarray]:
    scaler_input = np.isscalar(t)
    if scaler_input:
        t = np.array([t])

    result = a * np.cos(b * 2 * np.pi * t) ** 2
    if scaler_input:
        result = result[0]

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


def test_rate(t: np.ndarray) -> np.ndarray:
    a = 2
    b = 5
    return rate(t, a=a, b=b)


draw = rejection_sampling(test_rate, 0, 1, n_pts=1000)
pts = poisson_process(lambda t: rate(t, a=20, b=1), 0, 1)

n_pts = np.zeros(100)
for k in range(100):
    n_pts[k] = len(poisson_process(lambda t: rate(t, a=20, b=1), 0, 1))


def h_poisson_1d(rate: float, range: "listlike" = [0, 1]) -> np.ndarray:
    num_pts = poisson(rate * (range[1] - range[0])).rvs()
    pts = range[0] + (range[1] - range[0]) * np.random.rand(num_pts)
    return np.sort(pts)


print(h_poisson_1d(4, [0, 1]))
print(h_poisson_1d(4, [2, 8]))


def rate_func(x: float) -> float:
    return x
