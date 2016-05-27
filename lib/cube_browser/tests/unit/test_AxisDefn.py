from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.AxisDefn` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from cube_browser import AxisAlias, AxisDefn


class Test(tests.IrisTest):
    def test_lookup(self):
        dim, name, size, coord = 0, 1, 2, 4
        a = AxisDefn(dim=dim, name=name, size=size, coord=coord)
        self.assertEqual(a.dim, dim)
        self.assertEqual(a.name, name)
        self.assertEqual(a.size, size)
        self.assertEqual(a.coord, coord)

    def test_defn_same(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisDefn(dim=0, name=1, size=2, coord=3)
        self.assertEqual(a1, a2)

    def test_defn_same_with_different_dim(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisDefn(dim=1, name=1, size=2, coord=3)
        self.assertEqual(a1, a2)

    def test_defn_with_different_name(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisDefn(dim=0, name=10, size=2, coord=3)
        self.assertNotEqual(a1, a2)

    def test_defn_with_different_size(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisDefn(dim=0, name=1, size=20, coord=3)
        self.assertNotEqual(a1, a2)

    def test_defn_with_different_coord(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisDefn(dim=0, name=1, size=2, coord=30)
        self.assertNotEqual(a1, a2)

    def test_defn_with_alias(self):
        a1 = AxisDefn(dim=0, name=1, size=2, coord=3)
        a2 = AxisAlias(dim=0, name=1, size=2)
        self.assertNotEqual(a1, a2)


if __name__ == '__main__':
    tests.main()
