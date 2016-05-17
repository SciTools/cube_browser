import IPython
import ipywidgets
import iris.plot as iplt
import matplotlib.pyplot as plt


# Cube-browser version.
__version__ = '0.1.0-dev'


# XXX: #26: Chunks of this to be moved to somewhere else as they are shared
# with other plots
class Contourf(object):
    """
    Constructs a filled contour plot instance of a cube.

    An iris.plot.contourf instance is created using coordinates
    specified in the input arguments as axes coordinates.

    """
    def __init__(self, cube, coords, **kwargs):
        """
        Args:

        * cube: the iris.cube.Cube instance to plot

        * coords: the cube coordinate names or dimension indices to plot
                       in the order (x-axis, y-axis)

        Kwargs:

        kwargs for plot customization, see :func:`matplotlib.pyplot.contourf`
        and :func:`iris.plot.contourf` for details of other valid keyword
        arguments.
        """

        self.cube = cube
        self.coords = coords  # coords to plot as x, y
        self.kwargs = kwargs
        self.axes = self.new_axes()
        self.qcs = None  # QuadContourSet
        # A mapping of 1d-coord name to dimension
        self.coord_dim = self.coord_dims()

    # XXX: #24: coord_values is under review to be changed to a list or
    # dictionary or something
    # NOTE: Currently, Browser supplies a dictionary here.
    def __call__(self, **coord_values):
        """
        Constructs a static plot of the cube sliced at the coordinates
        specified in coord_values.

        This is called once each time a slider position is moved, at which
        point the new coordinate values are plotted.

        Args:

        * coord_values: mapping dictionary of coordinate name or dimension
        index with value index at which to be sliced
        """
        index = [slice(None)] * self.cube.ndim
        for name, value in kwargs.items():
            if name in self.coord_dim:
                index[self.coord_dim[name]] = value
        cube = self.cube[tuple(index)]
        plt.sca(self.axes)
        self.qcs = iplt.contourf(cube, coords=self.coords,
                                 axes=self.axes, **self.kwargs)
        return plt.gca()

    # XXX: #25: This function is a temporary measure for the one-axis, one-plot
    # scenario.  Multi-axes scenarios need to be handled soon.
    def new_axes(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=cube.coord_system().
                             as_cartopy_projection())
        return ax

    def coord_dims(self):
        """
        Compiles a mapping dictionary of dimension coordinates
        """
        mapping = {}
        for dim in range(self.cube.ndim):
            coords = self.cube.coords(dimensions=(dim,))
            mapping.update([(c.name(), dim) for c in coords])
        return mapping

    def slider_coords(self):
        """
        Compiles a list of the dim coords not used on the plot axes, to be
        used as slider coordinates
        """
        available = []
        for dim in range(len(self.cube.dim_coords)):
            if self.cube.dim_coords[dim].name() not in self.coords:
                available.append(self.cube.dim_coords[dim])
        return available


# XXX: #26: Chunks of this to be moved to somewhere else as they are shared
# with other plots
class Contour(object):
    """
    Constructs a filled contour plot instance of a cube.

    An iris.plot.contourf instance is created using coordinates
    specified in the input arguments as axes coordinates.
    """
    def __init__(self, cube, coords, **kwargs):
        """
        Args:

        * cube: the iris.cube.Cube instance to plot

        * coords: the cube coordinate names or dimension indices to plot
                       in the order (x-axis, y-axis)

        Kwargs:

        kwargs for plot customization, see :func:`matplotlib.pyplot.contourf`
        and :func:`iris.plot.contourf` for details of other valid keyword
        arguments.
        """
        self.cube = cube
        self.coords = coords # coords to plot
        self.kwargs = kwargs
        self.axes = self.new_axes()
        self.qcs = None  # QuadContourSet
        # A mapping of 1d-coord name to dimension
        self.coord_dim = self.coord_dims()

    # XXX: #24: coord_values is under review to be changed to a list or
    # dictionary or something
    # NOTE: Currently, Browser supplies a dictionary here.
    def __call__(self, **coord_values):
        """
        Constructs a static plot of the cube sliced at the coordinates
        specified in coord_values.

        This is called once each time a slider position is moved, at which
        point the new coordinate values are plotted.

        Args:

        * coord_values: mapping dictionary of coordinate name or dimension
        index with value index at which to be sliced
        """
        index = [slice(None)] * self.cube.ndim
        for name, value in kwargs.items():
            if name in self.coord_dim:
                index[self.coord_dim[name]] = value
        cube = self.cube[tuple(index)]
        plt.sca(self.axes)
        self.qcs = iplt.contour(cube, coords=self.coords, axes=self.axes, **self.kwargs)
        return plt.gca()

    # XXX: #25: This function is a temporary measure for the one-axis, one-plot
    # scenario.  Multi-axes scenarios need to be handled soon.
    def new_axes(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=cube.coord_system().
                             as_cartopy_projection())
        return ax

    def coord_dims(self):
       """
        Compiles a mapping dictionary of dimension coordinates
        """
        mapping = {}
        for dim in range(self.cube.ndim):
            coords = self.cube.coords(dimensions=(dim,))
            mapping.update([(c.name(), dim) for c in coords])
        return mapping

    def slider_coords(self):
        """
        Compiles a list of the dim coords not used on the plot axes, to be
        used as slider coordinates
        """
        available = []
        for dim in range(len(self.cube.dim_coords)):
            if self.cube.dim_coords[dim].name() not in self.coords:
                available.append(self.cube.dim_coords[dim])
        return available


class Browser(object):
    """
    Compiler for cube_browser plots and associated sliders.

    Compiles a single cube_browser plot instance or list of instances into a
    vertical arrangement of axes with shared coordinate sliders, to be
    displayed in a Jupyter notebook.

    """
    def __init__(self, plot):
        """
        Compiles non-axis coordinates into sliders, the values from which are
        used to reconstruct plots upon movement of slider.

        Args:

        * plot: cube_browser.Plot instance to display with slider

        """
        self.plot = plot
        self._sliders = {}
        for coord in plot.slider_coords():
                slider = ipywidgets.IntSlider(min=0, max=coord.shape[0] - 1,
                                              description=coord.name())
                slider.observe(self.on_change, names='value')
                self._sliders[coord.name()] = slider
        self.form = ipywidgets.VBox()
        self.form.children = self._sliders.values()
        # This bit displays the slider and the plot.
        self.on_change(None)
        IPython.display.display(self.form)

    def on_change(self, change):
        """
        Compiles mapping dictionary of slider values.

        This dictionary is re-compiled upon each movement of a coordinate
        slider, to be passed to plot call in order to reconstruct the plot.

        """
        slidermap = {}
        for name, slider in self._sliders.items():
            slidermap[name] = slider.value
        self.plot(**slidermap)
