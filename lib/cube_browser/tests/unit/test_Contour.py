from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Contour` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from iris.tests.stock import realistic_3d

from cartopy.mpl.geoaxes import GeoAxesSubplot
from matplotlib.contour import QuadContourSet
from cube_browser import Contour


class Test__call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.pcoords = ('grid_longitude',
                        'grid_latitude')  # plot axis coordinates.

    def test_plot_type(self):
        cf = Contour(self.cube, self.pcoords)
        ax = cf(time=0)
        self.assertTrue(isinstance(ax, GeoAxesSubplot))
        self.assertTrue(isinstance(cf.qcs, QuadContourSet))

if __name__ == '__main__':
    tests.main()
