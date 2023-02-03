from pointp.simulate import Homogeneous1D, InHomEx2
from pointp.sepp import sepp_class_1d

import numpy as np

# sepp = SelfExciting1D(1.0, 0.8, 2.0)
# tst = sepp.simulate(0, 10, return_generation=True)
np.random.seed(7)
# background = Homogeneous1D(1.5)
# trigger = InHomEx2(0.8, 2.0)
# tk, gen = simulate_1d_sepp(background, trigger, 0, 10, return_generation=True)
new_class = sepp_class_1d(Homogeneous1D, InHomEx2)
sepp_instance = new_class(1.5, 0.8, 2.0)
tk, gen = sepp_instance.simulate(0, 10, return_generation=True)

print(sepp_instance.intensity(np.linspace(0, 10, 20)))
