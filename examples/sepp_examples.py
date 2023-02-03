from pointp.simulate import Homogeneous1D, InHomEx2
from pointp.sepp import sepp_class_1d
import pointp.plot as pp
import pointp.dash_apps.demo_components as dc
import numpy as np
import plotly

# sepp = SelfExciting1D(1.0, 0.8, 2.0)
# tst = sepp.simulate(0, 10, return_generation=True)
np.random.seed(7)
# background = Homogeneous1D(1.5)
# trigger = InHomEx2(0.8, 2.0)
# tk, gen = simulate_1d_sepp(background, trigger, 0, 10, return_generation=True)
new_class = sepp_class_1d(Homogeneous1D, InHomEx2)
sepp_instance = new_class(1.5, 0.8, 2.0)
tk, gen = sepp_instance.simulate(0, 10, return_generation=True)
fig = pp.sepp_figure(tk, sepp_instance.intensity, [0, 10], generation=gen)
fig.write_html("test.html")

test = dc.sepp_example_row("SEPP", new_class, [0, 10])