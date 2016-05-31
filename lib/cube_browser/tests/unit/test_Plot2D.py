from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Plot2D` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from weakref import WeakValueDictionary
import warnings

from iris.coords import AuxCoord
from iris.tests.stock import realistic_3d
import numpy as np

from cube_browser import Plot2D, _AxisAlias, _AxisDefn


class Test__default_coords(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes
        self.patcher = self.patch('cube_browser.Plot2D._check_coords')

    def test_default_coords(self):
        plot = Plot2D(self.cube, self.axes)
        glat = self.cube.coord('grid_latitude')
        glon = self.cube.coord('grid_longitude')
        expected = (glon, glat)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_grid_longitude(self):
        self.cube.remove_coord('grid_longitude')
        plot = Plot2D(self.cube, self.axes)
        glat = self.cube.coord('grid_latitude')
        expected = (2, glat)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_grid_latitude(self):
        self.cube.remove_coord('grid_latitude')
        plot = Plot2D(self.cube, self.axes)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 1)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_all(self):
        self.cube.remove_coord('grid_latitude')
        self.cube.remove_coord('grid_longitude')
        plot = Plot2D(self.cube, self.axes)
        expected = (2, 1)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)


class Test__check_coords(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_coords_over_specified(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = ('time', 'grid_latitude', 'grid_longitude')
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_iterable(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = ('time',)
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_name(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = 'time'
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_dimension(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = 'time'
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_dimension_out_of_range_above(self):
        emsg = 'y-axis plot dimension for 3d cube out of range'
        coords = ('grid_longitude', 3)
        with self.assertRaisesRegexp(IndexError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_dimension_out_of_range_under(self):
        emsg = 'x-axis plot dimension for 3d cube out of range'
        coords = (-4, 'grid_latitude')
        with self.assertRaisesRegexp(IndexError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coordinate_unknown(self):
        emsg = "x-axis plot coordinate 'wibble' not found"
        coords = ('wibble', 'grid_latitude')
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coordinate_scalar(self):
        emsg = ("y-axis plot coordinate 'air_pressure' cannot be a "
                "scalar coordinate")
        coords = ('grid_longitude', 'air_pressure')
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coordinate_multi(self):
        coord = AuxCoord(np.ones(self.cube.shape[1:]), long_name='wibble')
        self.cube.add_aux_coord(coord, (1, 2))
        emsg = "x-axis plot coordinate 'wibble' must be a dimension coordinate"
        coords = ('wibble', 'grid_latitude')
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_same_dimension(self):
        emsg = 'x-axis and y-axis reference the same cube dimension'
        coords = ('time', 0)
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(self.cube, self.axes, coords=coords)

    def test_coordinates(self):
        coords = ('grid_longitude', 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        glon = self.cube.coord('grid_longitude')
        expected = (glon, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_less_than_coord(self):
        coords = (1, 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (0, glon)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_greater_than_coord(self):
        coords = (2, 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (1, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_x_dim_less_than_coord(self):
        coords = (-2, 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (0, glon)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_x_dim_greater_than_coord(self):
        coords = (-1, 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (1, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_y_dim_less_than_coord(self):
        coords = ('grid_longitude', 1)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_y_dim_greater_than_coord(self):
        coords = ('grid_latitude', 2)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (glat, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_y_dim_less_than_coord(self):
        coords = ('grid_longitude', -2)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_y_dim_greater_than_coord(self):
        coords = ('grid_latitude', -1)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (glat, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_less_than_y_dim(self):
        coords = (1, 2)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = (0, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_greater_than_y_dim(self):
        coords = (2, 1)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = (1, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)


class Test_alias(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_bad_dim_type(self):
        emsg = "Alias 'wibble' requires an integer dimension value"
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(TypeError, emsg):
            plot.alias(wibble='wobble')

    def test_bad_dim_under(self):
        emsg = "alias 'wibble' value for 3d cube out of range"
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(IndexError, emsg):
            plot.alias(wibble=-4)

    def test_bad_dim_over(self):
        emsg = "alias 'wibble' value for 3d cube out of range"
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(IndexError, emsg):
            plot.alias(wibble=3)

    def test_bad_cover_scalar(self):
        emsg = "alias 'air_pressure' cannot cover a scalar coordinate"
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.alias(air_pressure=1)

    def test_bad_cover_multi(self):
        emsg = "alias 'wibble' cannot cover a 2d coordinate"
        coord = AuxCoord(np.ones(self.cube.shape[1:]), long_name='wibble')
        self.cube.add_aux_coord(coord, (1, 2))
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.alias(wibble=1)

    def test_bad_dim_cover(self):
        emsg = ("alias 'time' must cover the same dimension as existing "
                'cube coordinate')
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.alias(time=2)

    def test_cover_dim_existing(self):
        plot = Plot2D(self.cube, self.axes)
        plot.alias(time=0)
        self.assertEqual(len(plot._dim_by_alias), 1)
        self.assertIn('time', plot._dim_by_alias)
        self.assertEqual(plot._dim_by_alias['time'], 0)

    def test_cover_dim_existing_negative(self):
        plot = Plot2D(self.cube, self.axes)
        plot.alias(time=-3)
        self.assertEqual(len(plot._dim_by_alias), 1)
        self.assertIn('time', plot._dim_by_alias)
        self.assertEqual(plot._dim_by_alias['time'], 0)

    def test_cover_anonymous(self):
        self.cube.remove_coord('grid_longitude')
        plot = Plot2D(self.cube, self.axes)
        plot.alias(longitude=2)
        self.assertEqual(len(plot._dim_by_alias), 1)
        self.assertIn('longitude', plot._dim_by_alias)
        self.assertEqual(plot._dim_by_alias['longitude'], 2)

    def test_cover_anonymous_negative(self):
        self.cube.remove_coord('grid_latitude')
        plot = Plot2D(self.cube, self.axes)
        plot.alias(latitude=-2)
        self.assertEqual(len(plot._dim_by_alias), 1)
        self.assertIn('latitude', plot._dim_by_alias)
        self.assertEqual(plot._dim_by_alias['latitude'], 1)

    def test_duplicate_alias_cover(self):
        plot = Plot2D(self.cube, self.axes)
        plot.alias(wibble=0)
        emsg = "alias 'wobble' covers the same dimension as alias 'wibble'"
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.alias(wobble=0)


class Test_remove_alias(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_alias_unknown(self):
        emsg = "Unknown dimension alias 'wibble'"
        plot = Plot2D(self.cube, self.axes)
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.remove_alias('wibble')

    def test_alias_known(self):
        plot = Plot2D(self.cube, self.axes)
        self.assertEqual(len(plot._dim_by_alias), 0)
        plot.alias(wibble=0)
        self.assertEqual(len(plot._dim_by_alias), 1)
        self.assertIn('wibble', plot._dim_by_alias)
        self.assertEqual(plot._dim_by_alias['wibble'], 0)
        plot.remove_alias('wibble')
        self.assertNotIn('wibble', plot._dim_by_alias)
        self.assertEqual(len(plot._dim_by_alias), 0)


class Test_aliases(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_no_aliases(self):
        plot = Plot2D(self.cube, self.axes)
        self.assertIsNone(plot.aliases)

    def test_aliases(self):
        plot = Plot2D(self.cube, self.axes)
        expected = {}
        aliases = [('wibble', 0), ('wobble', 1), ('bibble', 2)]
        for (name, dim) in aliases:
            expected[name] = dim
            plot.alias(**{name: dim})
        self.assertEqual(plot.aliases, expected)
        self.assertIsNot(plot.aliases, plot._dim_by_alias)


class Test_cache(tests.IrisTest):
    def setUp(self):
        cube = realistic_3d()
        axes = tests.mock.sentinel.axes
        self.draw = tests.mock.sentinel.draw
        self.patcher = self.patch('cube_browser.Plot2D.draw',
                                  return_value=self.draw)
        self.plot = Plot2D(cube, axes)

    def test_cache_create(self):
        self.assertIsNone(self.plot._cache)
        cache = self.plot.cache
        self.assertIsInstance(cache, WeakValueDictionary)
        self.assertEqual(cache, {})

    def test_bad_cache_setter(self):
        emsg = ("Require cache to be a 'WeakValueDictionary', "
                "got 'dict'")
        with self.assertRaisesRegexp(TypeError, emsg):
            self.plot.cache = dict()

    def test_cache_lookup(self):
        index = 0
        kwargs = dict(time=index)
        result = self.plot(**kwargs)
        self.assertEqual(result, self.draw)
        args, _ = self.patcher.call_args
        expected = self.plot.cube[index]
        self.assertEqual(args, (expected,))
        self.assertEqual(self.plot.subcube, expected)
        cache = self.plot.cache
        key = tuple(sorted(kwargs.items()))
        self.assertEqual(len(cache.keys()), 1)
        self.assertIn(key, cache)
        self.assertEqual(cache[key], expected)


class Test___init____plot_dims(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_bad_ndim(self):
        cube = self.cube[0, 0]
        emsg = 'requires at least a 2d cube, got 1d'
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D(cube, self.axes)

    def test_time_and_grid_latitude(self):
        coords = ('time', 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = set([0, 1])
        self.assertEqual(plot._plot_dims, expected)

    def test_grid_latitude_and_grid_longitude(self):
        coords = ('grid_latitude', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = set([1, 2])
        self.assertEqual(plot._plot_dims, expected)

    def test_time_and_grid_longitude(self):
        coords = ('time', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = set([0, 2])
        self.assertEqual(plot._plot_dims, expected)


class Test__sliders_dim(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_slider_time(self):
        coords = ('grid_latitude', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = dict(time=0)
        self.assertEqual(plot._slider_dim_by_name, expected)

    def test_slider_grid_latitude(self):
        coords = ('time', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = dict(grid_latitude=1)
        self.assertEqual(plot._slider_dim_by_name, expected)

    def test_slider_grid_longitude(self):
        coords = ('time', 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = dict(grid_longitude=2)
        self.assertEqual(plot._slider_dim_by_name, expected)

    def test_slider_aux_forecast_period(self):
        coords = ('grid_longitude', 'grid_latitude')
        self.cube.remove_coord('time')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = dict(forecast_period=0)
        self.assertEqual(plot._slider_dim_by_name, expected)

    def test_slider_aux_sort(self):
        coords = ('grid_longitude', 'grid_latitude')
        self.cube.remove_coord('time')
        coord = self.cube.coord('forecast_period').copy()
        coord.rename('first')
        self.cube.add_aux_coord(coord, 0)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        expected = dict(first=0)
        self.assertEqual(plot._slider_dim_by_name, expected)

    def test_no_slider_from_aux(self):
        coords = ('grid_longitude', 'grid_latitude')
        self.cube.remove_coord('time')
        fp = self.cube.coord('forecast_period')
        self.cube.remove_coord('forecast_period')
        aux = AuxCoord.from_coord(fp)
        self.cube.add_aux_coord(aux, 0)
        plot = Plot2D(self.cube, self.axes, coords=coords)
        self.assertEqual(plot._slider_dim_by_name, {})


class Test__invert_mapping(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_bad_mapping(self):
        mapping = dict(one=1, two=2, three=3, four=1)
        emsg = 'Cannot invert non 1-to-1 mapping'
        with self.assertRaisesRegexp(ValueError, emsg):
            Plot2D._invert_mapping(mapping)

    def test_invert_mapping(self):
        mapping = dict(one=1, two=2, three=3, four=4)
        expected = {1: 'one', 2: 'two', 3: 'three', 4: 'four'}
        actual = Plot2D._invert_mapping(mapping)
        self.assertEqual(actual, expected)


class Test_sliders_axis(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def _tidy(self, coord):
        coord = coord.copy()
        coord.bounds = None
        coord.var_name = None
        coord.attributes = None
        return coord

    def test_slider_time(self):
        coords = ('grid_latitude', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        original = self.cube.coord('time')
        coord = self._tidy(original)
        expected = _AxisDefn(dim=0, name='time', size=7, coord=coord)
        actual = plot.sliders_axis
        self.assertEqual(actual, [expected])
        self.assertIsNot(actual[0].coord, original)

    def test_slider_grid_latitude(self):
        coords = ('time', 'grid_longitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        original = self.cube.coord('grid_latitude')
        coord = self._tidy(original)
        expected = _AxisDefn(dim=1, name='grid_latitude', size=9, coord=coord)
        actual = plot.sliders_axis
        self.assertEqual(actual, [expected])
        self.assertIsNot(actual[0].coord, original)

    def test_slider_grid_longitude(self):
        coords = ('time', 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        original = self.cube.coord('grid_longitude')
        coord = self._tidy(original)
        expected = _AxisDefn(dim=2, name='grid_longitude', size=11,
                             coord=coord)
        actual = plot.sliders_axis
        self.assertEqual(actual, [expected])
        self.assertIsNot(actual[0].coord, original)

    def test_slider_alias(self):
        plot = Plot2D(self.cube, self.axes)
        plot.alias(time=0)
        expected = _AxisAlias(dim=0, name='time', size=7)
        self.assertEqual(plot.sliders_axis, [expected])

    def test_bad_slider_anonymous(self):
        self.cube.remove_coord('time')
        self.cube.remove_coord('forecast_period')
        plot = Plot2D(self.cube, self.axes)
        emsg = ("cube 'air_potential_temperature' has no meta-data "
                'for dimension 0')
        with self.assertRaisesRegexp(ValueError, emsg):
            plot.sliders_axis


class Test___call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes
        self.draw = tests.mock.sentinel.draw
        self.patcher = self.patch('cube_browser.Plot2D.draw',
                                  return_value=self.draw)

    def test_bad_slider(self):
        plot = Plot2D(self.cube, self.axes)
        emsg = "called with unknown name 'wibble'"
        with self.assertRaisesRegexp(ValueError, emsg):
            plot(wibble=0)

    def test_slider_slice(self):
        index = 5
        kwargs = dict(time=index)
        plot = Plot2D(self.cube, self.axes)
        result = plot(**kwargs)
        self.assertEqual(result, self.draw)
        args, _ = self.patcher.call_args
        expected = plot.cube[index]
        self.assertEqual(args, (expected,))
        self.assertEqual(plot.subcube, expected)
        cache = plot.cache
        key = tuple(sorted(kwargs.items()))
        self.assertEqual(len(cache.keys()), 1)
        self.assertIn(key, cache)
        self.assertEqual(cache[key], expected)

    def test_slider_slice_warning(self):
        index = 3
        kwargs = dict(grid_longitude=index)
        coords = ('time', 'grid_latitude')
        plot = Plot2D(self.cube, self.axes, coords=coords)
        plot.alias(wibble=2)
        wmsg = ("expected to be called with alias 'wibble' for dimension 2, "
                "rather than with 'grid_longitude'")
        with warnings.catch_warnings():
            # Cause all warnings to raise an exception.
            warnings.simplefilter('error')
            with self.assertRaisesRegexp(UserWarning, wmsg):
                plot(**kwargs)

    def test_slider_alias(self):
        index = 7
        kwargs = dict(wibble=index)
        plot = Plot2D(self.cube, self.axes)
        plot.alias(wibble=1)
        result = plot(**kwargs)
        self.assertEqual(result, self.draw)
        args, _ = self.patcher.call_args
        expected = plot.cube[:, index]
        self.assertEqual(args, (expected,))
        self.assertEqual(plot.subcube, expected)
        cache = plot.cache
        key = tuple(sorted(kwargs.items()))
        self.assertEqual(len(cache.keys()), 1)
        self.assertIn(key, cache)
        self.assertEqual(cache[key], expected)


class Test_draw(tests.IrisTest):
    def test(self):
        cube = realistic_3d()
        axes = tests.mock.sentinel.axes
        plot = Plot2D(cube, axes)
        emsg = 'requires a draw method for rendering'
        with self.assertRaisesRegexp(NotImplementedError, emsg):
            plot(time=0)


if __name__ == '__main__':
    tests.main()
