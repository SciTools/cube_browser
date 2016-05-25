from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Pyplot` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

import iris.plot
from iris.coords import AuxCoord
from iris.tests.stock import realistic_3d
import matplotlib.pyplot as plt
import numpy as np

from cube_browser import Pyplot


class Test__default_coords(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes
        self.patcher = self.patch('cube_browser.Pyplot._check_coords')

    def test_default_coords(self):
        plot = Pyplot(self.cube, self.axes)
        glat = self.cube.coord('grid_latitude')
        glon = self.cube.coord('grid_longitude')
        expected = (glon, glat)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_grid_longitude(self):
        self.cube.remove_coord('grid_longitude')
        plot = Pyplot(self.cube, self.axes)
        glat = self.cube.coord('grid_latitude')
        expected = (2, glat)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_grid_latitude(self):
        self.cube.remove_coord('grid_latitude')
        plot = Pyplot(self.cube, self.axes)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 1)
        args, _ = self.patcher.call_args
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], tuple)
        self.assertEqual(args[0], expected)

    def test_remove_all(self):
        self.cube.remove_coord('grid_latitude')
        self.cube.remove_coord('grid_longitude')
        plot = Pyplot(self.cube, self.axes)
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
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_iterable(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = ('time',)
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_name(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = 'time'
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coords_under_specified_dimension(self):
        emsg = 'requires 2 coordinates, one for each plot axis'
        coords = 'time'
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_dimension_out_of_range_above(self):
        emsg = 'y-axis plot dimension for 3d cube out of range'
        coords = ('grid_longitude', 3)
        with self.assertRaisesRegexp(IndexError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_dimension_out_of_range_under(self):
        emsg = 'x-axis plot dimension for 3d cube out of range'
        coords = (-4, 'grid_latitude')
        with self.assertRaisesRegexp(IndexError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coordinate_unknown(self):
        emsg = "x-axis plot coordinate 'wibble' not found"
        coords = ('wibble', 'grid_latitude')
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coordinate_scalar(self):
        emsg = ("y-axis plot coordinate 'air_pressure' cannot be a "
                "scalar coordinate")
        coords = ('grid_longitude', 'air_pressure')
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coordinate_multi(self):
        coord = AuxCoord(np.ones(self.cube.shape[1:]), long_name='wibble')
        self.cube.add_aux_coord(coord, (1, 2))
        emsg = "x-axis plot coordinate 'wibble' must be a dimension coordinate"
        coords = ('wibble', 'grid_latitude')
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_same_dimension(self):
        emsg = 'x-axis and y-axis reference the same cube dimension'
        coords = ('time', 0)
        with self.assertRaisesRegexp(ValueError, emsg):
            Pyplot(self.cube, self.axes, coords=coords)

    def test_coordinates(self):
        coords = ('grid_longitude', 'grid_latitude')
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        glon = self.cube.coord('grid_longitude')
        expected = (glon, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_less_than_coord(self):
        coords = (1, 'grid_longitude')
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (0, glon)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_greater_than_coord(self):
        coords = (2, 'grid_latitude')
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (1, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_x_dim_less_than_coord(self):
        coords = (-2, 'grid_longitude')
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (0, glon)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_x_dim_greater_than_coord(self):
        coords = (-1, 'grid_latitude')
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (1, glat)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_y_dim_less_than_coord(self):
        coords = ('grid_longitude', 1)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_y_dim_greater_than_coord(self):
        coords = ('grid_latitude', 2)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (glat, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_y_dim_less_than_coord(self):
        coords = ('grid_longitude', -2)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glon = self.cube.coord('grid_longitude')
        expected = (glon, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_negative_y_dim_greater_than_coord(self):
        coords = ('grid_latitude', -1)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        glat = self.cube.coord('grid_latitude')
        expected = (glat, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_less_than_y_dim(self):
        coords = (1, 2)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        expected = (0, 1)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)

    def test_x_dim_greater_than_y_dim(self):
        coords = (2, 1)
        plot = Pyplot(self.cube, self.axes, coords=coords)
        expected = (1, 0)
        self.assertIsInstance(plot.coords, tuple)
        self.assertEqual(plot.coords, expected)


class Test_coord_dims(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.pcoords = ('grid_longitude',
                        'grid_latitude')  # plot axis coordinates.
        self.axes = tests.mock.sentinel.axes

    def test(self):
        cf = Pyplot(self.cube, self.axes, coords=self.pcoords)
        actual = cf.coord_dims()
        expected = dict(forecast_period=0,
                        grid_latitude=1,
                        grid_longitude=2,
                        time=0)
        self.assertEqual(actual, expected)
        self.assertEqual(cf.coord_dim, expected)


class Test_slider_coords(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = tests.mock.sentinel.axes

    def test_slider_one(self):
        coords = ('grid_longitude', 'grid_latitude')
        cf = Pyplot(self.cube, self.axes, coords=coords)
        actual = cf.slider_coords()
        expected = self.cube.coord('time')
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0], expected)


if __name__ == '__main__':
    tests.main()
