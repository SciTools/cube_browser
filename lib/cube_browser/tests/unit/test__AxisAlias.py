from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.AxisAlias` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from cube_browser import _AxisAlias, _AxisDefn


class Test(tests.IrisTest):
    def test_lookup(self):
        dim, name, size = 0, 1, 2
        a = _AxisAlias(dim=dim, name=name, size=size)
        self.assertEqual(a.dim, dim)
        self.assertEqual(a.name, name)
        self.assertEqual(a.size, size)

    def test_alias_same(self):
        a1 = _AxisAlias(dim=0, name=1, size=2)
        a2 = _AxisAlias(dim=0, name=1, size=2)
        self.assertEqual(a1, a2)

    def test_alias_same_with_different_dim(self):
        a1 = _AxisAlias(dim=0, name=1, size=2)
        a2 = _AxisAlias(dim=1, name=1, size=2)
        self.assertEqual(a1, a2)

    def test_alias_with_different_name(self):
        a1 = _AxisAlias(dim=0, name=1, size=2)
        a2 = _AxisAlias(dim=0, name=10, size=2)
        self.assertNotEqual(a1, a2)

    def test_alias_with_different_size(self):
        a1 = _AxisAlias(dim=0, name=1, size=2)
        a2 = _AxisAlias(dim=0, name=1, size=20)
        self.assertNotEqual(a1, a2)

    def test_alias_with_defn(self):
        a1 = _AxisAlias(dim=0, name=1, size=2)
        a2 = _AxisDefn(dim=0, name=1, size=2, coord=3)
        self.assertNotEqual(a1, a2)


if __name__ == '__main__':
    tests.main()
