from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Contour` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from iris.tests.stock import realistic_3d
import iris.plot
from cartopy.mpl.geoaxes import GeoAxesSubplot
from matplotlib.contour import QuadContourSet
import matplotlib.pyplot as plt

from cube_browser import Contour


class Test__call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.pcoords = ('grid_longitude',
                        'grid_latitude')  # plot axis coordinates.

    def test_plot_type(self):
        fig = plt.figure()
        projection = self.cube.coord_system().as_cartopy_projection()
        ax = fig.add_subplot(111, projection=projection)
        cf = Contour(self.cube, ax, coords=self.pcoords)
        return_ax = cf(time=0)
        self.assertTrue(isinstance(return_ax, GeoAxesSubplot))
        self.assertTrue(isinstance(cf.qcs, QuadContourSet))


if __name__ == '__main__':
    tests.main()
