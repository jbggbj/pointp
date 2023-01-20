import numpy as np
from typing import Tuple

def pp_to_counts(tk: np.ndarray, t_max: float) -> Tuple[np.ndarray, np.ndarray]:
    cts_t = np.concatenate([np.zeros(1), tk, np.array([t_max])])
    cts_y = np.concatenate(
        [np.zeros(1), np.ones_like(tk).cumsum(), np.array([len(tk)])]
    )
    return cts_t, cts_y
