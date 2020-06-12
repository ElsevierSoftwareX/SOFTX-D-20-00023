import cairo
import numpy as np


def draw(ctx, color_bar_pos, color_bar_dims, low, high, **kwargs):
    """Draws the color bar together with its labels.

    Parameters
    ----------
    ctx : cairo.Context
        Context.
    color_bar_pos : tuple of float
        Coordinates of the top left point of the color bar.
    color_bar_dims : tuple of float
        Width and height of the color bar.
    low : float
        Lower limit of the linear range.
    high : float
        Upper limit of the linear range.
    **kwargs
        axis_label : str
            Axis label of the color bar.
    """
    middle = rectangle(ctx, color_bar_pos, color_bar_dims, low, high, **kwargs)
    tick_labels(ctx, middle, low, high, color_bar_pos, color_bar_dims)
    axis_label(ctx, color_bar_pos, color_bar_dims,
               label=kwargs.get('axis_label'))


def dimensions(surface_dims, color_bar_fraction, border_fraction):
    """Extracts dimensions of the color bar.

    Parameters
    ----------
    surface_dims : tuple of float
        Dimensions of the surface.
    color_bar_fraction : tuple of float
        The fraction of the surface that the color bar region will take on
        the right (vertically and horizontally.
    border_fraction : float
        Fraction of the max_dim that will be blank on all sides of the surface.

    Returns
    -------
    color_bar_pos : tuple of float
        Coordinates of the top left point of the color bar.
    color_bar_dims : tuple of float
        Width and height of the color bar.
    """
    height = np.max(surface_dims) * color_bar_fraction[0]
    width = np.max(surface_dims) * color_bar_fraction[1]/4
    x_start = surface_dims[0] * (1 - border_fraction) - 3*width
    y_start = 0.5*surface_dims[1] - height/2
    color_bar_dims = (width, height)
    color_bar_pos = (x_start, y_start)
    return color_bar_pos, color_bar_dims


def rgb(low, high, low_rgb, zero_rgb, high_rgb):
    """Extracts RGB values for the color bar gradient.

    Parameters
    ----------
    low : float
        Lower limit of the linear range.
    high : float
        Upper limit of the linear range.
    low_rgb : tuple of int
        Colour (in RGB) associated with the lower limit.
    zero_rgb : tuple of int
        Colour (in RGB) associated with value of zero.
    high_rgb : tuple of int
        Colour (in RGB) associated with the upper limit.

    Returns
    -------
    tuple of int
        RGB values for the bottom, middle and top parts of the color map
        gradient. If only two colors are used, middle_rgb is returned as None.
    """
    if low < 0 < high:
        top_rgb = high_rgb
        middle_rgb = zero_rgb
        bottom_rgb = low_rgb
    else:
        middle_rgb = None

    if high > low >= 0:
        top_rgb = high_rgb
        bottom_rgb = zero_rgb
    if low < high <= 0:
        top_rgb = zero_rgb
        bottom_rgb = low_rgb
    if low == high > 0:
        top_rgb = bottom_rgb = high_rgb
    if low == high < 0:
        top_rgb = bottom_rgb = low_rgb
    if low == high == 0:
        top_rgb = bottom_rgb = zero_rgb

    return bottom_rgb, middle_rgb, top_rgb


def rectangle(ctx, color_bar_pos, color_bar_dims, low, high, **kwargs):
    """Draws rectangle with color gradient.

    Parameters
    ----------
    ctx : cairo.Context
        Context.
    color_bar_pos : tuple of float
        Coordinates of the top left point of the color bar.
    color_bar_dims : tuple of float
        Width and height of the color bar.
    low : float
        Lower limit of the linear range.
    high : float
        Upper limit of the linear range.
    **kwargs
        low_rgb : tuple of int
            Colour (in RGB) associated with the lower limit.
        zero_rgb : tuple of int
            Colour (in RGB) associated with value of zero.
        high_rgb : tuple of int
            Colour (in RGB) associated with the upper limit.

    Returns
    -------
    bool
        If False, only two colors were used for the gradient.
    """
    ctx.rectangle(*color_bar_pos, *color_bar_dims)
    x_start = color_bar_pos[0] + color_bar_dims[0]
    y_start = color_bar_pos[1] + color_bar_dims[1]
    x_end = color_bar_pos[0]
    y_end = color_bar_pos[1]
    pattern = cairo.LinearGradient(x_start, y_start, x_end, y_end)

    bottom_rgb, middle_rgb, top_rgb = rgb(
        low, high, low_rgb=kwargs.get('low_rgb'),
        zero_rgb=kwargs.get('zero_rgb'), high_rgb=kwargs.get('high_rgb'))
    pattern.add_color_stop_rgb(0, *bottom_rgb)
    pattern.add_color_stop_rgb(1, *top_rgb)
    if middle_rgb is not None:
        pattern.add_color_stop_rgb(0.5, *middle_rgb)
        middle = True
    else:
        middle = False

    ctx.set_source(pattern)
    ctx.fill()

    return middle


def tick_labels(ctx, middle, low, high, color_bar_pos, color_bar_dims):
    """Draws tick labels of the color bar.

    Parameters
    ----------
    ctx : cairo.Context
        Context.
    middle : bool
        If False, only two colors were used for the gradient.
    low : float
        Lower limit of the linear range.
    high : float
        Upper limit of the linear range.
    color_bar_pos : tuple of float
        Coordinates of the top left point of the color bar.
    color_bar_dims : tuple of float
        Width and height of the color bar.
    """
    ctx.set_source_rgb(0, 0, 0)
    font_size = color_bar_dims[0]/2.5
    ctx.set_font_size(font_size)
    _, _, _, text_height, _, _ = ctx.text_extents(str(0))

    x = color_bar_pos[0] + color_bar_dims[0]*1.2
    y = color_bar_pos[1] + 0.5*text_height
    ctx.move_to(x, y)
    if high > 0 or middle:
        ctx.show_text(str(high))
    else:
        ctx.show_text('0')

    if middle:
        x = color_bar_pos[0] + color_bar_dims[0]*1.2
        y = color_bar_pos[1] + 0.5*color_bar_dims[1] + 0.5*text_height
        ctx.move_to(x, y)
        ctx.show_text('0')

    x = color_bar_pos[0] + color_bar_dims[0]*1.2
    y = color_bar_pos[1] + color_bar_dims[1] + 0.5*text_height
    ctx.move_to(x, y)
    if low < 0 or middle:
        ctx.show_text(str(low))
    else:
        ctx.show_text('0')


def axis_label(ctx, color_bar_pos, color_bar_dims, label='Current (A)'):
    """Draws axis label of a color bar.

    Parameters
    ----------
    ctx : cairo.Context
        Context.
    color_bar_pos : tuple of float
        Coordinates of the top left point of the color bar.
    color_bar_dims : tuple of float
        Width and height of the color bar.
    label : str
        Axis label of the color bar.
    """
    ctx.set_source_rgb(0, 0, 0)
    font_size = 0.6*color_bar_dims[0]
    ctx.set_font_size(font_size)

    _, _, width, height, _, _ = ctx.text_extents(str(label))
    x = color_bar_pos[0] + 2*color_bar_dims[0] + height
    y = color_bar_pos[1] + 0.5*color_bar_dims[1] + 0.5*width
    ctx.move_to(x, y)

    ctx.rotate(-np.pi/2)
    ctx.show_text(str(label))
    ctx.rotate(np.pi/2)
