from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Pcolormesh` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from iris.tests.stock import realistic_3d

from cartopy.mpl.geoaxes import GeoAxesSubplot
from matplotlib.pcolormesh import QuadMesh
from cube_browser import Pcolormesh


class Test__call__(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.pcoords = ('grid_longitude',
                        'grid_latitude')  # plot axis coordinates.

    def test_plot_type(self):
        pcm = Pcolormesh(self.cube, self.pcoords)
        ax = pcm(time=0)
        self.assertTrue(isinstance(ax, GeoAxesSubplot))
        self.assertTrue(isinstance(pcm.qm, QuadMesh))

if __name__ == '__main__':
    tests.main()
