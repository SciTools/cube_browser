from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Contourf` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from cartopy.mpl.geoaxes import GeoAxesSubplot
import iris.plot as iplt
from iris.tests.stock import realistic_3d
from matplotlib.contour import QuadContourSet
import matplotlib.pyplot as plt

from cube_browser import Contourf


class Test___call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.coords = ('grid_longitude', 'grid_latitude')

    def test(self):
        projection = iplt.default_projection(self.cube)
        ax = plt.subplot(111, projection=projection)
        plot = Contourf(self.cube, ax, coords=self.coords)
        for index in range(self.cube.shape[0]):
            element = plot(time=index)
            self.assertIsInstance(element, QuadContourSet)
            self.assertEqual(element, plot.element)
            self.assertIsInstance(plot.axes, GeoAxesSubplot)
            self.assertEqual(ax, plot.axes)
            self.assertEqual(self.cube[index], plot.subcube)


if __name__ == '__main__':
    tests.main()
