"""
pcolormesh uses a QuadMesh, a faster generalization of pcolor, but
with some restrictions.
This demo illustrates a bug in quadmesh with masked data.
"""
import numpy as np
from matplotlib.pyplot import figure, show, savefig
from matplotlib import cm, colors
from numpy import ma
n = 56
x = np.linspace(-1.5,1.5,n)
y = np.linspace(-1.5,1.5,n*2)
X,Y = np.meshgrid(x,y);
Qx = np.cos(Y) - np.cos(X)
Qz = np.sin(Y) + np.sin(X)
Qx = (Qx + 1.1)
Z = np.sqrt(X**2 + Y**2)/5;
Z = (Z - Z.min()) / (Z.max() - Z.min())
Zm = ma.masked_where(np.fabs(Qz) < 0.5*np.amax(Qz), Z)
fig = figure()
ax = fig.add_subplot(121)
ax.set_axis_bgcolor("#bdb76b")
ax.pcolormesh(Qx,Qz,Z)
ax.set_title('Without masked values')
ax = fig.add_subplot(122)
ax.set_axis_bgcolor("#bdb76b")
col = ax.pcolormesh(Qx,Qz,Zm)
ax.set_title('With masked values')
show()
