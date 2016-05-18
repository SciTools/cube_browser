from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Contourf` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from iris.tests.stock import realistic_3d

from cube_browser import Contourf


class Test_coord_dims(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.pcoords = ('grid_longitude',
                        'grid_latitude')  # plot axis coordinates.

    def test(self):
        cf = Contourf(self.cube, self.pcoords)
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

    def test_slider_all(self):
        # XXX: This shouldn't be allowed!
        cf = Contourf(self.cube, ())
        actual = cf.slider_coords()
        expected = set(self.cube.dim_coords)
        self.assertEqual(len(actual), len(expected))
        for coord in actual:
            self.assertIn(coord, expected)

    def test_slider_two(self):
        # XXX: This should't be allowed!
        cf = Contourf(self.cube, ('grid_longitude',))
        actual = cf.slider_coords()
        names = ('time', 'grid_latitude')
        expected = set([self.cube.coord(name) for name in names])
        self.assertEqual(len(actual), len(expected))
        for coord in actual:
            self.assertIn(coord, expected)

    def test_slider_one(self):
        cf = Contourf(self.cube, ('grid_longitude', 'grid_latitude'))
        actual = cf.slider_coords()
        expected = self.cube.coord('time')
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0], expected)

    def test_slider_none(self):
        # XXX: This shouldn't be allowed!
        names = ('grid_latitude', 'grid_longitude', 'time')
        cf = Contourf(self.cube, names)
        actual = cf.slider_coords()
        self.assertEqual(len(actual), 0)


if __name__ == '__main__':
    tests.main()
