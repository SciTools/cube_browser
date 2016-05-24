from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

import IPython
import ipywidgets
from iris.coords import Coord
import iris.plot as iplt
import matplotlib.pyplot as plt


# Cube-browser version.
__version__ = '0.1.0-dev'

# Set default IPython magics if a notebook is called the import
ipynb = IPython.get_ipython()
if ipynb is not None:
    ipynb.magic(u"%matplotlib notebook")
    ipynb.magic(u"%autosave 0")


class Pyplot(object):
    def __init__(self, cube, axes, **kwargs):
        """
        Args:

        * cube
            The :class:`~iris.cube.Cube` instance to plot.

        * axes
            Matplotlib axes for plotting.

        Kwargs:

        * coords
            The cube coordinates, coordinate names or dimension indices
            to plot in the order (x-axis, y-axis).

        * kwargs
            Matplotlib kwargs for plot customization.

        """
        self.cube = cube
        if cube.ndim < 2:
            emsg = '{} requires at least a 2d cube, got {}d.'
            raise ValueError(emsg.format(type(self).__name__, cube.ndim))
        self.axes = axes
        # Coordinates/dimensions to use for the plot x-axis, y-axis.
        coords = kwargs.pop('coords', None)
        if coords is None:
            coords = self._default_coords()
        self.coords = self._check_coords(coords)
        self.kwargs = kwargs
        # A mapping of 1d-coord name to dimension
        self.coord_dim = self.coord_dims()
        # The data element of the plot. 
        self.element = None

    def _default_coords(self):
        """
        Determines the default coordinates or cube dimensions to use
        for the plot x-axis and y-axis.

        Firstly, will attempt to default to the 'X' and 'Y' dimension
        coordinates, but only if both exist on the cube.

        Otherwise, default to the last two cube dimensions, assuming
        the last two cube dimensions are in y-axis, x-axis order i.e.
        the x-axis is the last cube dimension.

        Returns a tuple of the chosen coordinates/dimensions.

        """
        xcoord = self.cube.coords(axis='x', dim_coords=True)
        ycoord = self.cube.coords(axis='y', dim_coords=True)
        if xcoord and ycoord:
            # Default to the cube X and Y dimension coordinates.
            coords = (xcoord[0], ycoord[0])
        else:
            # Default to the last two cube dimensions in ydim, xdim order.
            ndim = self.cube.ndim
            xdim, ydim = ndim - 1, ndim - 2
            xcoord = self.cube.coords(dimensions=(xdim,), dim_coords=True)
            xcoord = xcoord[0] if xcoord else xdim
            ycoord = self.cube.coords(dimensions=(ydim,), dim_coords=True)
            ycoord = ycoord[0] if ycoord else ydim
            coords = (xcoord, ycoord)
        return coords

    def _check_coords(self, coords):
        """
        Verify the two coordinates/dimensions specified to use for the plot
        x-axis and y-axis.

        Ensures that explicit cube dimension values are suitably translated
        for use with the target 2d cube.

        Returns a list of the verified coordinates/dimensions.

        """
        result = []
        dims = []
        translate = False
        if isinstance(coords, (six.string_types, int)):
            coords = (coords,)
        if len(coords) != 2:
            emsg = '{} requires 2 coordinates, one for each plot axis, got {}.'
            raise ValueError(emsg.format(type(self).__name__, len(coords)))
        ndim = self.cube.ndim
        for i, (coord, axis) in enumerate(zip(coords, ['x', 'y'])):
            if isinstance(coord, int):
                if coord < 0:
                    coord = ndim + coord
                if coord < 0 or coord >= ndim:
                    emsg = 'Nominated {}-axis plot dimension for {}d cube ' \
                        'out of range, got {}.'
                    raise IndexError(emsg.format(axis, ndim, coords[i]))
                result.append(coord)
                dims.append(coord)
                translate = True
            else:
                cube_coord = self.cube.coords(coord)
                if len(cube_coord) == 0:
                    name = coord.name() if isinstance(coord, Coord) else coord
                    emsg = 'Nominated {}-axis plot coordinate {!r} not ' \
                        'found on cube.'
                    raise ValueError(emsg.format(axis, name))
                [coord] = cube_coord
                dim = self.cube.coord_dims(coord)
                if len(dim) != 1:
                    emsg = 'Nominated {}-axis plot coordinate {!r} must be ' \
                        '1d, got {}d.'
                    raise ValueError(emsg.format(axis, coord.name(), len(dim)))
                result.append(coord)
                dims.append(dim[0])
        if dims[0] == dims[1]:
            emsg = 'Nominated x-axis and y-axis reference the same cube ' \
                'dimension, got {}.'
            raise ValueError(emsg.format(dims[0]))
        if translate:
            # Ensure explicit dimension values are suitably translated
            # for use with the target 2d cube.
            dims = [0, 1] if dims[0] < dims[1] else [1, 0]
            for i, (r, d) in enumerate(zip(result, dims)):
                if isinstance(r, int):
                    result[i] = d
        return tuple(result)

    def _get_slice(self, coord_values):
        index = [slice(None)] * self.cube.ndim
        for name, value in coord_values.items():
            if name in self.coord_dim:
                index[self.coord_dim[name]] = value
        cube = self.cube[tuple(index)]
        plt.sca(self.axes)
        return cube

    def coord_dims(self):
        """
        Compiles a mapping dictionary of dimension coordinates.

        """
        mapping = {}
        for dim in range(self.cube.ndim):
            coords = self.cube.coords(dimensions=(dim,))
            mapping.update([(c.name(), dim) for c in coords])
        return mapping

    def slider_coords(self):
        """
        Compiles a list of the dim coords not used on the plot axes, to be
        used as slider coordinates.

        """
        available = []
        for coord in self.cube.dim_coords:
            if coord not in self.coords:
                available.append(coord)
        return available


# XXX: #26: Chunks of this to be moved to somewhere else as they are shared
# with other plots
class Contourf(Pyplot):
    """
    Constructs a filled contour plot instance of a cube.

    An :func:`iris.plot.contourf` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.contourf` and :func:`iris.plot.contourf`
    for details of other valid keyword arguments

    """

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

        * coord_values
            Mapping dictionary of coordinate name or dimension
            index with value index at which to be sliced.

        """
        cube = self._get_slice(coord_values)
        if self.element is not None:
            for col in self.element.collections:
                col.remove()
        # Add QuadContourSet to self as self.element
        self.element = iplt.contourf(cube, coords=self.coords,
                                     axes=self.axes, **self.kwargs)
        return plt.gca()


# XXX: #26: Chunks of this to be moved to somewhere else as they are shared
# with other plots
class Contour(Pyplot):
    """
    Constructs a line contour plot instance of a cube.

    An :func:`iris.plot.contour` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.contour` and :func:`iris.plot.contour`
    for details of other valid keyword arguments.

    """

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

        * coord_values
            Mapping dictionary of coordinate name or dimension
            index with value index at which to be sliced.

        """
        cube = self._get_slice(coord_values)
        if self.element is not None:
            for col in self.element.collections:
                col.remove()
        # Add QuadContourSet to self as self.element
        self.element = iplt.contour(cube, coords=self.coords,
                                    axes=self.axes, **self.kwargs)
        return plt.gca()


class Pcolormesh(Pyplot):
    """
    Constructs a pseduocolour plot instance of a cube on a quadrilateral mesh.

    An :func:`iris.plot.pcolormesh` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.pcolormesh` and :func:`iris.plot.pcolormesh`
    for details of other valid keyword arguments.

    """

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

        * coord_values
            Mapping dictionary of coordinate name or dimension
            index with value index at which to be sliced.

        """
        cube = self._get_slice(coord_values)
        if self.element is not None:
            self.element.remove()
        # Add QuadMesh to self as self.element
        self.element = iplt.pcolormesh(cube, coords=self.coords,
                                       axes=self.axes, **self.kwargs)
        return plt.gca()


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

        * plot
            cube_browser plot instance to display with slider.

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
