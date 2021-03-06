"""
Some simple functions to generate colours.
"""
import numpy as np
from matplotlib.colors import colorConverter
def pastel(colour, weight=2.4):
    """ Convert colour into a nice pastel shade"""
    rgb = np.asarray(colorConverter.to_rgb(colour))
    maxc = max(rgb)
    if maxc < 1.0 and maxc > 0:
        scale = 1.0 / maxc
        rgb = rgb * scale
    total = rgb.sum()
    slack = 0
    for x in rgb:
        slack += 1.0 - x
    x = (weight - total) / slack
    rgb = [c + (x * (1.0-c)) for c in rgb]
    return rgb
def get_colours(n):
    """ Return n pastel colours. """
    base = np.asarray([[1,0,0], [0,1,0], [0,0,1]])
    if n <= 3:
        return base[0:n]
    needed = (((n - 3) + 1) / 2, (n - 3) / 2)
    colours = []
    for start in (0, 1):
        for x in np.linspace(0, 1, needed[start]+2):
            colours.append((base[start] * (1.0 - x)) +
                           (base[start+1] * x))
    return [pastel(c) for c in colours[0:n]]
