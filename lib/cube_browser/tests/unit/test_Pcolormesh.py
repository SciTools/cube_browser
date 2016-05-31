from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Pcolormesh` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from cartopy.mpl.geoaxes import GeoAxesSubplot
import iris.plot as iplt
from iris.tests.stock import realistic_3d
from matplotlib.collections import QuadMesh
import matplotlib.pyplot as plt

from cube_browser import Pcolormesh


class Test__call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.coords = ('grid_longitude', 'grid_latitude')
        self.projection = iplt.default_projection(self.cube)

    def test_without_bounds(self):
        for coord in self.coords:
            coord = self.cube.coord(coord)
            coord.bounds = None
        ax = plt.subplot(111, projection=self.projection)
        plot = Pcolormesh(self.cube, ax, coords=self.coords)
        for index in range(self.cube.shape[0]):
            element = plot(time=index)
            self.assertIsInstance(element, QuadMesh)
            self.assertEqual(element, plot.element)
            self.assertIsInstance(plot.axes, GeoAxesSubplot)
            self.assertEqual(ax, plot.axes)
            for coord in self.coords:
                self.assertTrue(plot.subcube.coord(coord).has_bounds())
            subcube = self.cube[index]
            for coord in self.coords:
                subcube.coord(coord).guess_bounds()
            self.assertEqual(subcube, plot.subcube)

    def test_with_bounds(self):
        for coord in self.coords:
            coord = self.cube.coord(coord)
            if not coord.has_bounds():
                coord.guess_bounds()
        ax = plt.subplot(111, projection=self.projection)
        plot = Pcolormesh(self.cube, ax, coords=self.coords)
        for index in range(self.cube.shape[0]):
            element = plot(time=index)
            self.assertIsInstance(element, QuadMesh)
            self.assertEqual(element, plot.element)
            self.assertIsInstance(plot.axes, GeoAxesSubplot)
            self.assertEqual(ax, plot.axes)
            for coord in self.coords:
                self.assertTrue(plot.subcube.coord(coord).has_bounds())
            self.assertEqual(self.cube[index], plot.subcube)


if __name__ == '__main__':
    tests.main()
