from typing import Union

import numpy as np

import pointp.simulate as ps
from scipy.stats import poisson, expon, gamma


class ExponentialTrigger(ps.Process1D):

    model_parameters = [ps.ModelParameter("a", 0, 1.5), ps.ModelParameter("w", 0.01, 10)]
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


class GammaTrigger(ps.Process1D):
    model_parameters = [ps.ModelParameter("a", 0, 1.5),
                        ps.ModelParameter("b", 0.01, 10)]

    latex_string = r"$$a \frac{x^{b-1}e^{-x}}{\Gamma (b)}$$"

    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        return self.a * gamma(self.b).pdf(t)

    def simulate(self, t_min: float, t_max: float) -> np.ndarray:
        """Return points for inhomogeneous point process."""
        num_pts = poisson(self.a).rvs()
        all_tk = gamma(self.b).rvs(size=num_pts)
        return np.sort(all_tk[all_tk <= t_max])






def _simulate_1d_sepp(
    background: ps.Process1D,
    trigger: ps.Process1D,
    t_min: float,
    t_max: float,
    return_generation: bool = False,
) -> np.ndarray:
    event_times = background.simulate(t_min, t_max)
    to_trigger = event_times.tolist()
    generation = [1] * len(to_trigger)
    to_trigger_gen = generation.copy()
    while len(to_trigger) > 0:
        parent_time = to_trigger.pop()
        parent_gen = to_trigger_gen.pop()
        children_times = parent_time + trigger.simulate(0, t_max - parent_time)
        children_gen = [parent_gen + 1] * len(children_times)
        event_times = np.append(event_times, children_times)
        generation = generation + children_gen
        to_trigger = to_trigger + children_times.tolist()
        to_trigger_gen = to_trigger_gen + children_gen

    order_in_time = np.argsort(event_times)
    event_times = event_times[order_in_time]
    generation = np.array(generation)[order_in_time]
    if return_generation:
        return event_times, generation
    else:
        return event_times

    return event_times


def sepp_class_1d(
    background_class: "class ps.Process1D", trigger_class: "class ps.Process1D"
) -> "cls":
    class SEPP1D(ps.Process1D):
        model_parameters = (
            background_class.model_parameters + trigger_class.model_parameters
        )
        background = background_class
        trigger = trigger_class

        def __init__(self, *args):
            self.background = background_class(
                *args[: len(background_class.model_parameters)]
            )
            self.trigger = trigger_class(*args[len(background_class.model_parameters) :])
            self.event_times, self.generation = None, None


        def simulate(
            self, t_min: float, t_max: float, return_generation: bool = False
        ) -> Union[np.ndarray, tuple[np.ndarray, np.ndarray]]:
            self.event_times, self.generation = _simulate_1d_sepp(
                self.background,
                self.trigger,
                t_min,
                t_max,
                return_generation=True,
            )
            if return_generation:
                return self.event_times, self.generation
            else:
                return self.event_times

        def intensity(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:

            result = self.background.intensity(t)
            for tk in self.event_times:
                delay = t - tk
                result[delay >= 0] += self.trigger.intensity(delay[delay >= 0])
            return result

    return SEPP1D
