import plotly.io as pio


def plot_bar(x, y, title="A Figure Specified By Python Dictionary"):

    fig = dict(
        {
            "data": [{"type": "bar", "x": [1, 2, 3], "y": [1, 3, 2]}],
            "layout": {"title": {"text": "A Figure Specified By Python Dictionary"}},
        }
    )

    # To display the figure defined by this dict, use the low-level plotly.io.show function

    pio.show(fig, renderer="browser")
