import matplotlib.pyplot as plt
from demo_image import get_demo_image
def demo_simple_image(ax):
    Z, extent = get_demo_image()
    im = ax.imshow(Z, extent=extent, interpolation="nearest")
    cb = plt.colorbar(im)
    plt.setp(cb.ax.get_yticklabels(), visible=False)
def demo_locatable_axes_hard(fig1):
    from mpl_toolkits.axes_grid \
         import SubplotDivider, LocatableAxes, Size
    divider = SubplotDivider(fig1, 2, 2, 2, aspect=True)
    ax = LocatableAxes(fig1, divider.get_position())
    ax_cb = LocatableAxes(fig1, divider.get_position())
    h = [Size.AxesX(ax), # main axes
         Size.Fixed(0.05), # padding, 0.1 inch
         Size.Fixed(0.2), # colorbar, 0.3 inch
         ]
    v = [Size.AxesY(ax)]
    divider.set_horizontal(h)
    divider.set_vertical(v)
    ax.set_axes_locator(divider.new_locator(nx=0, ny=0))
    ax_cb.set_axes_locator(divider.new_locator(nx=2, ny=0))
    fig1.add_axes(ax)
    fig1.add_axes(ax_cb)
    ax_cb.axis["left"].toggle(all=False)
    ax_cb.axis["right"].toggle(ticks=True)
    Z, extent = get_demo_image()
    im = ax.imshow(Z, extent=extent, interpolation="nearest")
    plt.colorbar(im, cax=ax_cb)
    plt.setp(ax_cb.get_yticklabels(), visible=False)
def demo_locatable_axes_easy(ax):
    from mpl_toolkits.axes_grid import make_axes_locatable
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.05)
    fig1 = ax.get_figure()
    fig1.add_axes(ax_cb)
    Z, extent = get_demo_image()
    im = ax.imshow(Z, extent=extent, interpolation="nearest")
    plt.colorbar(im, cax=ax_cb)
    ax_cb.yaxis.tick_right()
    for tl in ax_cb.get_yticklabels():
        tl.set_visible(False)
    ax_cb.yaxis.tick_right()
def demo_images_side_by_sied(ax):
    from mpl_toolkits.axes_grid import make_axes_locatable
    divider = make_axes_locatable(ax)
    Z, extent = get_demo_image()
    ax2 = divider.new_horizontal(size="100%", pad=0.05)
    fig1 = ax.get_figure()
    fig1.add_axes(ax2)
    ax.imshow(Z, extent=extent, interpolation="nearest")
    ax2.imshow(Z, extent=extent, interpolation="nearest")
    for tl in ax2.get_yticklabels():
        tl.set_visible(False)
def demo():
    fig1 = plt.figure(1, (6, 6))
    fig1.clf()
    ax = fig1.add_subplot(2, 2, 1)
    demo_simple_image(ax)
    demo_locatable_axes_hard(fig1)
    ax = fig1.add_subplot(2, 2, 3)
    demo_locatable_axes_easy(ax)
    ax = fig1.add_subplot(2, 2, 4)
    demo_images_side_by_sied(ax)
    plt.draw()
    plt.show()
if __name__ == "__main__":
   demo()