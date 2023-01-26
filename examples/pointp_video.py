from pointp import simulate, plot
import plotly.io as pio
import plotly.graph_objs as go
import numpy as np
import math

pio.templates.default = "simple_white"
t_min, t_max = 0, 10
process = simulate.Homogeneous1D(2)

tk = process.simulate(t_min, t_max)
min_frames = 20
max_frames = 40
min_dt = (tk[1:] - tk[0:-1]).min()
n_frames = max(min_frames, math.ceil(t_max / min_dt))
n_frames = min(n_frames, max_frames)
# fig = process.plot_func(tk, (t_min, t_max))
t_frame = np.linspace(t_min, t_max, n_frames)

frames = [
    go.Frame(data=process.plot_func(tk[tk <= t], (t_min, t), plot_bins=False).data)
    for t in t_frame[1:]
]

fig = go.Figure(
    # data=[plot.points_plot(tk[tk <= t_frame[0]])],
    data=process.plot_func(
        tk[tk <= t_frame[0]], (t_min, t_frame[0]), plot_bins=False
    ).data,
    layout=go.Layout(
        xaxis=dict(range=[t_min, t_max], autorange=False),
        yaxis=dict(range=[0, len(tk)], autorange=False),
        # title="Start Title",
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        args=[
                            None,
                            {
                                "frame": {"duration": 50, "redraw": False},
                                "transition": {"duration": 1},
                            },
                        ],
                        label="Play",
                        method="animate",
                    )
                ],
                type="buttons",
                showactive=False,
                y=1,
                x=1.12,
                xanchor="right",
                yanchor="top",
            )
        ],
    ),
    frames=frames,
    # frames=[go.Frame(data=[plot.points_plot(tk[tk <= t])]) for t in t_frame[1:]]
)

fig.write_html("test.html")
