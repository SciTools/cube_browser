from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

from collections import Iterable, namedtuple
import warnings
from weakref import WeakValueDictionary

import IPython
import ipywidgets
from iris.coords import Coord, DimCoord
import iris.plot as iplt
import matplotlib.pyplot as plt


# Cube-browser version.
__version__ = '0.1.0-dev'


# Set default IPython magics if an IPython session has invoked the import.
ipynb = IPython.get_ipython()

if ipynb is not None:  # pragma: no cover
    ipynb.magic(u"%matplotlib notebook")
    ipynb.magic(u"%autosave 0")


class _AxisAlias(namedtuple('_AxisAlias', 'dim, name, size')):
    def __eq__(self, other):
        result = NotImplemented
        if isinstance(other, _AxisAlias):
            left = (self.name, self.size)
            right = (other.name, other.size)
            result = left == right
        elif isinstance(other, _AxisDefn):
            result = False
        return result

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is not NotImplemented:
            result = not result
        return result


class _AxisDefn(namedtuple('_AxisDefn', 'dim, name, size, coord')):
    def __eq__(self, other):
        result = NotImplemented
        if isinstance(other, _AxisDefn):
            left = (self.name, self.size, self.coord)
            right = (other.name, other.size, other.coord)
            result = left == right
        elif isinstance(other, _AxisAlias):
            result = False
        return result

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is not NotImplemented:
            result = not result
        return result


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
        #: The latest rendered cube slice.
        self.subcube = None
        #: The associated rendered matplotlib element.
        self.element = None
        if cube.ndim < 2:
            emsg = '{} requires at least a 2d cube, got {}d.'
            raise ValueError(emsg.format(type(self).__name__, cube.ndim))
        self.axes = axes
        coords = kwargs.pop('coords', None)
        if coords is None:
            coords = self._default_coords()
        #: Coordinates/dimensions to use for the plot x-axis and y-axis.
        self.coords = self._check_coords(coords)
        self.kwargs = kwargs
        # Set of plot axis dimensions.
        self._plot_dims = {c if isinstance(c, int) else
                           cube.coord_dims(c)[0] for c in self.coords}
        # Mapping of slider dimension coordinate name to dimension.
        self._slider_dim_by_name = self._sliders_dim()
        # A mapping of dimension alias name to dimension.
        self._dim_by_alias = {}
        # A weak reference value cache for plot sub-cube sharing.
        self._cache = None

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
            xcoord = self.cube.coords(dimensions=xdim, dim_coords=True)
            xcoord = xcoord[0] if xcoord else xdim
            ycoord = self.cube.coords(dimensions=ydim, dim_coords=True)
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
                    emsg = ('Nominated {}-axis plot dimension for {}d cube '
                            'out of range, got {}.')
                    raise IndexError(emsg.format(axis, ndim, coords[i]))
                result.append(coord)
                dims.append(coord)
                translate = True
            else:
                cube_coord = self.cube.coords(coord)
                if len(cube_coord) == 0:
                    name = coord.name() if isinstance(coord, Coord) else coord
                    emsg = ('Nominated {}-axis plot coordinate {!r} not '
                            'found on cube.')
                    raise ValueError(emsg.format(axis, name))
                [coord] = cube_coord
                if not isinstance(coord, DimCoord):
                    emsg = ('Nominated {}-axis plot coordinate {!r} must be '
                            'a dimension coordinate.')
                    raise ValueError(emsg.format(axis, coord.name()))
                dim = self.cube.coord_dims(coord)
                if not dim:
                    emsg = ('Nominated {}-axis plot coordinate {!r} cannot be '
                            'a scalar coordinate.')
                    raise ValueError(emsg.format(axis, coord.name()))
                result.append(coord)
                dims.append(dim[0])
        if dims[0] == dims[1]:
            emsg = ('Nominated x-axis and y-axis reference the same cube '
                    'dimension, got {}.')
            raise ValueError(emsg.format(dims[0]))
        if translate:
            # Ensure explicit dimension values are suitably translated
            # for use with the target 2d cube.
            dims = [0, 1] if dims[0] < dims[1] else [1, 0]
            for i, (r, d) in enumerate(zip(result, dims)):
                if isinstance(r, int):
                    result[i] = d
        return tuple(result)

    @property
    def aliases(self):
        """
        Returns the known dimension aliases for the plot's cube.

        """
        result = None
        if self._dim_by_alias:
            result = self._dim_by_alias.copy()
        return result

    def remove_alias(self, name):
        """
        Remove the named dimension alias associated with the plot's cube.

        """
        if name not in self._dim_by_alias:
            emsg = 'Unknown dimension alias {!r}.'
            raise ValueError(emsg.format(name))
        self._dim_by_alias.pop(name)

    def alias(self, **kwargs):
        """
        Associate the named alias to the specified cube dimension of the plot.

        Kwargs:

            The alias name and associated cube dimension.
            E.g. ::

                plot.alias(time=0, latitude=2)

            This associates the 'time' alias to cube dimension 0, and the
            'latitude' alias to cube dimension 2.

        """
        ndim = self.cube.ndim
        for name, dim in kwargs.items():
            if not isinstance(dim, int):
                emsg = ('Alias {!r} requires an integer dimension value, '
                        'got {!r}.')
                raise TypeError(emsg.format(name, type(dim).__name__))
            original = dim
            if dim < 0:
                dim = ndim + dim
            if dim < 0 or dim >= ndim:
                emsg = ('Dimension alias {!r} value for {}d cube out of '
                        'range, got {}.')
                raise IndexError(emsg.format(name, ndim, original))
            coords = self.cube.coords(name)
            if coords:
                dims = self.cube.coord_dims(name)
                dcount = len(dims)
                if dcount != 1:
                    dtype = 'scalar' if dcount == 0 else '{}d'.format(dcount)
                    emsg = ('Dimension alias {!r} cannot cover a {} '
                            'coordinate.')
                    raise ValueError(emsg.format(name, dtype))
                if dim != dims[0]:
                    emsg = ('Dimension alias {!r} must cover the same '
                            'dimension as existing cube coordinate, got '
                            'dimension {} expected {}.')
                    raise ValueError(emsg.format(name, dim, dims[0]))
            # Check there are no alias covering the same dimension.
            if dim in self._dim_by_alias.values():
                emsg = ('Dimension alias {!r} covers the same dimension '
                        'as alias {!r}.')
                alias_by_dim = self._invert_mapping(self._dim_by_alias)
                raise ValueError(emsg.format(name, alias_by_dim[dim]))
            self._dim_by_alias[name] = dim

    @property
    def cache(self):
        if self._cache is None:
            self._cache = WeakValueDictionary()
        return self._cache

    @cache.setter
    def cache(self, value):
        if not isinstance(value, WeakValueDictionary):
            emsg = "Require cache to be a {!r}, got {!r}."
            raise TypeError(emsg.format(WeakValueDictionary.__name__,
                                        type(value).__name__))
        self._cache = value

    def _sliders_dim(self):
        """
        Determines the dimension coordinate and associated dimension for each
        cube slider dimension i.e. not plot dimensions.

        Returns a dictionary of slider dimension by coordinate name.

        """
        mapping = {}
        dims = set(range(self.cube.ndim)) - self._plot_dims
        for dim in dims:
            coord = self.cube.coords(dimensions=dim, dim_coords=True)
            if coord:
                mapping[coord[0].name()] = dim
            else:
                # Fill with an appropriate dimension coordinate from the
                # auxiliary coordinates.
                coords = self.cube.coords(dimensions=dim, dim_coords=False)
                coords = [coord for coord in coords
                          if isinstance(coord, DimCoord)]
                if coords:
                    func = lambda coord: coord._as_defn()
                    coords.sort(key=func)
                    mapping[coords[0].name()] = dim
        return mapping

    @staticmethod
    def _invert_mapping(mapping):
        """
        Reverse the dictionary mapping from (key, value) to (value, key).

        Returns the inverted dictionary.

        """
        keys = set(mapping.keys())
        values = set(mapping.values())
        if len(keys) != len(values):
            emsg = 'Cannot invert non 1-to-1 mapping, got {!r}.'
            raise ValueError(emsg.format(mapping))
        result = dict(map(lambda (k, v): (v, k), mapping.items()))
        return result

    @property
    def sliders_axis(self):
        """
        Returns a list containing either an :class:`~cube_browser._AxisAlias`
        or :class:`~cube_browser._AxisDefn` for each cube slider dimension.

        """
        shape = self.cube.shape
        dims = set(range(self.cube.ndim)) - self._plot_dims
        slider_name_by_dim = self._invert_mapping(self._slider_dim_by_name)
        alias_by_dim = self._invert_mapping(self._dim_by_alias)
        result = []
        for dim in dims:
            name = alias_by_dim.get(dim)
            if name is not None:
                axis = _AxisAlias(dim=dim, name=name, size=shape[dim])
            else:
                name = slider_name_by_dim.get(dim)
                if name is None:
                    emsg = '{!r} cube {!r} has no meta-data for dimension {}.'
                    raise ValueError(emsg.format(type(self).__name__,
                                                 self.cube.name(), dim))
                # Prepare the coordinate for lenient equality.
                coord = self.cube.coord(name).copy()
                coord.bounds = None
                coord.var_name = None
                coord.attributes = {}
                axis = _AxisDefn(dim=dim, name=name,
                                 size=coord.points.size, coord=coord)
            result.append(axis)
        return result

    # XXX: Issue #24
    def __call__(self, **kwargs):
        """
        Renders the plot for the given named slider values.

        Kwargs:

            The slider name and associated dimension index value.
            E.g. ::

                plot(time=5, model_level_number=23)

            The plot cube will be sliced on the associated 'time' and
            'model_level_number' dimensions at the specified index values
            before being rendered on its axes.

        """
        index = [slice(None)] * self.cube.ndim
        alias_by_dim = self._invert_mapping(self._dim_by_alias)
        for name, value in kwargs.items():
            # The alias has priority, so check this first.
            dim = self._dim_by_alias.get(name)
            if dim is None:
                dim = self._slider_dim_by_name.get(name)
                if dim is None:
                    emsg = '{!r} called with unknown name {!r}.'
                    raise ValueError(emsg.format(type(self).__name__, name))
                else:
                    if dim in alias_by_dim:
                        wmsg = ('{!r} expected to be called with alias {!r} '
                                'for dimension {}, rather than with {!r}.')
                        warnings.warn(wmsg.format(type(self).__name__,
                                                  alias_by_dim[dim], dim,
                                                  name))
            index[dim] = value
        index = tuple(index)
        key = tuple(sorted(kwargs.items()))
        # A primative weak reference cache.
        self.subcube = self.cache.setdefault(key, self.cube[index])
        return self.draw(self.subcube)

    def draw(self, cube):
        """Abstract method."""
        emsg = '{!r} requires a draw method for rendering.'
        raise NotImplementedError(emsg.format(type(self).__name__))


class Contourf(Pyplot):
    """
    Constructs a filled contour plot instance of a cube.

    An :func:`iris.plot.contourf` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.contourf` and :func:`iris.plot.contourf`
    for details of other valid keyword arguments

    """
    def draw(self, cube):
        self.element = iplt.contourf(cube, axes=self.axes, coords=self.coords,
                                     **self.kwargs)
        return self.element

    # XXX: Not sure this should live here!
    #      Need test coverage!
    def clear(self):
        if self.element is not None:
            for collection in self.element.collections:
                collection.remove()


class Contour(Pyplot):
    """
    Constructs a line contour plot instance of a cube.

    An :func:`iris.plot.contour` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.contour` and :func:`iris.plot.contour`
    for details of other valid keyword arguments.

    """
    def draw(self, cube):
        self.element = iplt.contour(cube, axes=self.axes, coords=self.coords,
                                    **self.kwargs)
        return self.element

    def clear(self):
        if self.element is not None:
            for collection in self.element.collections:
                collection.remove()


class Pcolormesh(Pyplot):
    """
    Constructs a pseduocolour plot instance of a cube on a quadrilateral mesh.

    An :func:`iris.plot.pcolormesh` instance is created using coordinates
    specified in the input arguments as axes coordinates.

    See :func:`matplotlib.pyplot.pcolormesh` and :func:`iris.plot.pcolormesh`
    for details of other valid keyword arguments.

    """
    def draw(self, cube):
        for name in self.coords:
            if not isinstance(name, int):
                coord = cube.coord(name)
                if not coord.has_bounds():
                    coord.guess_bounds()

        self.element = iplt.pcolormesh(cube, axes=self.axes,
                                       coords=self.coords, **self.kwargs)
        return self.element

    def clear(self):
        if self.element is not None:
            self.element.remove()


class Browser(object):
    """
    Compiler for cube_browser plots and associated sliders.

    Compiles a single cube_browser plot instance or list of instances into a
    vertical arrangement of axes with shared coordinate sliders, to be
    displayed in a Jupyter notebook.

    """
    def __init__(self, plots):
        """
        Compiles non-axis coordinates into sliders, the values from which are
        used to reconstruct plots upon movement of slider.

        Args:

        * plot
            cube_browser plot instance to display with slider.

        """
        if not isinstance(plots, Iterable):
            plots = [plots]
        self.plots = plots

        # Mapping of coordinate/alias name to axis.
        self._axis_by_name = {}
        # Mapping of cube-id to shared cache.
        self._cache_by_cube_id = {}
        # Mapping of plot-id to coordinate/alias name.
        self._names_by_plot_id = {}
        # Mapping of coordinate/alias name to plots.
        self._plots_by_name = {}
        self._build_mappings()

        self._slider_by_name = {}
        self._name_by_slider_id = {}
        for axis in self._axis_by_name.values():
                slider = ipywidgets.IntSlider(min=0, max=axis.size - 1,
                                              description=axis.name)
                slider.observe(self.on_change, names='value')
                self._slider_by_name[axis.name] = slider
                self._name_by_slider_id[id(slider)] = axis.name

        self._form = ipywidgets.VBox()
        # Layout the sliders in a consitent order.
        slider_names = sorted(self._slider_by_name)
        sliders = [self._slider_by_name[name] for name in slider_names]
        self._form.children = sliders

    def display(self):
        # XXX: Ideally, we might want to register an IPython display hook.
        self.on_change(None)
        IPython.display.display(self._form)

    def _build_mappings(self):
        """
        Create the cross-reference dictionaries required to manage the
        orchestration of the registered plots.

        In summary,
            * _axis_by_name
                The mapping with the meta-data required to define each
                slider dimension.
            * _cache_by_cube_id
                The mapping used to share the weak reference cache between
                plots that reference the same cube.
            * _names_by_plot_id
                The mapping that specifies the exact slider dimensions
                required by each plot.
            * _plots_by_name
                The mapping that specifies all the plots to be updated when
                a specific slider state changes.

        """
        for plot in self.plots:
            names = []
            for axis in plot.sliders_axis:
                if isinstance(axis, _AxisAlias):
                    if axis.name is None:
                        emsg = ('{!r} cube {!r} has no meta-data for '
                                'dimension {}.')
                        raise ValueError(emsg.format(type(plot).__name__,
                                                     plot.cube.name(),
                                                     axis.dim))
                existing = self._axis_by_name.get(axis.name)
                if existing is None:
                    self._axis_by_name[axis.name] = axis
                elif existing != axis:
                    emsg = ('{!r} cube {!r} has an incompatible axis {!r} '
                            'on dimension {}.')
                    raise ValueError(emsg.format(type(plot).__name__,
                                                 plot.cube.name(),
                                                 axis.name, axis.dim))
                plots = self._plots_by_name.setdefault(axis.name, [])
                plots.append(plot)
                names.append(axis.name)
            if names:
                # Only make an entry if the plot has at least one axis
                # to slider over.
                self._names_by_plot_id[id(plot)] = names
            cube_id = id(plot.cube)
            cache = self._cache_by_cube_id.get(cube_id)
            if cache is None:
                self._cache_by_cube_id[cube_id] = plot.cache
            else:
                plot.cache = cache

    def on_change(self, change):
        """
        Common slider widget traitlet event handler that refreshes
        all appropriate plots given a slider state change.

        """
        def _update(plots, force=False):
            for plot in plots:
                plot.clear()
            for plot in plots:
                names = self._names_by_plot_id.get(id(plot))
                # Check whether we need to force an invariant plot
                # to render itself.
                if force and names is None:
                    names = []
                if names is not None:
                    kwargs = {name: slider_by_name[name].value
                              for name in names}
                    plot(**kwargs)

        slider_by_name = self._slider_by_name
        if change is None:
            # Initial render of all the plots.
            _update(self.plots, force=True)
        else:
            # A widget slider state has changed, so only refresh
            # the appropriate plots.
            slider_id = id(change['owner'])
            name = self._name_by_slider_id[slider_id]
            _update(self._plots_by_name[name])
