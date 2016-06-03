from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
"""Unit tests for the `cube_browser.Browser` class."""

# Import iris.tests first so that some things can be initialised
# before importing anything else.
import iris.tests as tests

from iris.coords import DimCoord
from iris.cube import CubeList
from iris.tests import mock
from iris.tests.stock import realistic_3d

from cube_browser import Browser, Contour, _AxisAlias, _AxisDefn


def _add_levels(cube, levels=13):
    clist = CubeList()
    for level in range(levels):
        mln = DimCoord(level, standard_name='model_level_number')
        other = cube.copy()
        other.add_aux_coord(mln)
        clist.append(other)
    return clist.merge_cube()


class Test__build_mappings__cache(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = mock.sentinel.axes
        self.patch('IPython.display.display')
        self.patch('ipywidgets.SelectionSlider')
        self.patch('ipywidgets.VBox')
        self.patch('cube_browser.Browser.on_change')

    def test_shared_cache(self):
        c1 = Contour(self.cube, self.axes)
        c2 = Contour(self.cube, self.axes)
        browser = Browser([c1, c2])
        lookup = browser._cache_by_cube_id
        cube_id = id(self.cube)
        self.assertEqual(lookup.keys(), [cube_id])
        self.assertEqual(id(c1.cache), id(c2.cache))
        self.assertEqual(lookup.values(), [c1.cache])

    def test_separate_cache(self):
        c1 = Contour(self.cube, self.axes)
        other_cube = realistic_3d()
        c2 = Contour(other_cube, self.axes)
        browser = Browser([c1, c2])
        lookup = browser._cache_by_cube_id
        cube_id = id(self.cube)
        other_id = id(other_cube)
        expected = set([cube_id, other_id])
        self.assertEqual(set(lookup.keys()), expected)
        self.assertNotEqual(id(c1.cache), id(c2.cache))
        self.assertEqual(id(lookup[cube_id]), id(c1.cache))
        self.assertEqual(id(lookup[other_id]), id(c2.cache))


class Test__build_mappings(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = mock.sentinel.axes
        self.patch('IPython.display.display')
        self.patch('ipywidgets.SelectionSlider')
        self.patch('ipywidgets.VBox')
        self.patch('cube_browser.Browser.on_change')

    def _tidy(self, coord):
        coord = coord.copy()
        coord.bounds = None
        coord.var_name = None
        coord.attributes = None
        return coord

    def test_single_plot_with_no_axis(self):
        cube = self.cube[0]
        plot = Contour(cube, self.axes)
        browser = Browser(plot)
        # Check axis_by_name.
        self.assertEqual(browser._axis_by_name, {})
        # Check plots_by_name.
        self.assertEqual(browser._plots_by_name, {})
        # Check names_by_plot_id.
        self.assertEqual(browser._names_by_plot_id, {})

    def test_single_plot_with_axis_no_metadata(self):
        plot = Contour(self.cube, self.axes)
        with mock.patch('cube_browser.Contour.sliders_axis',
                        new_callable=mock.PropertyMock) as sliders_axis:
            alias = _AxisAlias(dim=0, name=None, size=7)
            sliders_axis.return_value = [alias]
            emsg = ("cube {!r} has no meta-data "
                    "for dimension 0".format(self.cube.name()))
            with self.assertRaisesRegexp(ValueError, emsg):
                Browser(plot)

    def test_single_plot_with_axis(self):
        plot = Contour(self.cube, self.axes)
        browser = Browser(plot)
        name = 'time'
        coord = self._tidy(self.cube.coord(name))
        # Check axis_by_name.
        axis = _AxisDefn(dim=0, name=name, size=7, coord=coord)
        expected = dict(time=axis)
        self.assertEqual(browser._axis_by_name, expected)
        # Check plots_by_name.
        plot_id = id(plot)
        self.assertEqual(browser._plots_by_name.keys(), [name])
        self.assertEqual([id(v) for v in browser._plots_by_name[name]],
                         [plot_id])
        # Check names_by_plot_id.
        self.assertEqual(browser._names_by_plot_id.keys(), [plot_id])
        self.assertEqual(browser._names_by_plot_id[plot_id], [name])

    def test_single_plot_with_alias_axis(self):
        plot = Contour(self.cube, self.axes)
        plot.alias(wibble=0)
        browser = Browser(plot)
        # Check axis_by_name.
        axis = _AxisAlias(dim=0, name='wibble', size=7)
        expected = dict(wibble=axis)
        self.assertEqual(browser._axis_by_name, expected)
        # Check plots_by_name.
        plot_id = id(plot)
        plots_by_name = browser._plots_by_name
        self.assertEqual(plots_by_name.keys(), ['wibble'])
        self.assertEqual([id(v) for v in plots_by_name['wibble']], [plot_id])
        # Check names_by_plot_id.
        names_by_plot_id = browser._names_by_plot_id
        self.assertEqual(names_by_plot_id.keys(), [plot_id])
        self.assertEqual(names_by_plot_id[plot_id], ['wibble'])

    def test_two_plots_with_no_axis(self):
        cube = self.cube[0]
        c1 = Contour(cube, self.axes)
        c2 = Contour(cube, self.axes)
        browser = Browser([c1, c2])
        # Check axis_by_name.
        self.assertEqual(browser._axis_by_name, {})
        # Check plots_by_name.
        self.assertEqual(browser._plots_by_name, {})
        # Check names_by_plot_id.
        self.assertEqual(browser._names_by_plot_id, {})

    def test_two_plots_with_shared_axis(self):
        coords = ('time', 'grid_latitude')
        c1 = Contour(self.cube, self.axes, coords=coords)
        c2 = Contour(self.cube, self.axes, coords=coords)
        browser = Browser([c1, c2])
        name = 'grid_longitude'
        coord = self._tidy(self.cube.coord(name))
        # Check axis_by_name.
        axis = _AxisDefn(dim=2, name=name, size=11, coord=coord)
        expected = dict(grid_longitude=axis)
        self.assertEqual(browser._axis_by_name, expected)
        # Check plots_by_name.
        c1_id, c2_id = id(c1), id(c2)
        plots_by_name = browser._plots_by_name
        self.assertEqual(plots_by_name.keys(), [name])
        self.assertEqual(set([id(v) for v in plots_by_name[name]]),
                         set([c1_id, c2_id]))
        # Check names_by_plot_id.
        names_by_plot_id = browser._names_by_plot_id
        self.assertEqual(set(names_by_plot_id.keys()), set([c1_id, c2_id]))
        self.assertEqual(names_by_plot_id[c1_id], [name])
        self.assertEqual(names_by_plot_id[c2_id], [name])

    def test_two_plots_with_shared_axis_and_independent_axis(self):
        c1 = Contour(self.cube, self.axes)
        levels = 10
        other = _add_levels(self.cube, levels)
        c2 = Contour(other, self.axes)
        browser = Browser([c1, c2])
        tcoord = self._tidy(self.cube.coord('time'))
        zcoord = self._tidy(other.coord('model_level_number'))
        # Check axis_by_name.
        taxis1 = _AxisDefn(dim=0, name='time', size=7, coord=tcoord)
        taxis2 = _AxisDefn(dim=1, name='time', size=7, coord=tcoord)
        zaxis = _AxisDefn(dim=0, name='model_level_number', size=levels,
                          coord=zcoord)
        axis_by_name = browser._axis_by_name
        expected = dict(time=taxis1, model_level_number=zaxis)
        self.assertEqual(axis_by_name, expected)
        expected = dict(time=taxis2, model_level_number=zaxis)
        self.assertEqual(axis_by_name, expected)
        # Check plots_by_name.
        c1_id, c2_id = id(c1), id(c2)
        plots_by_name = browser._plots_by_name
        self.assertEqual(set(plots_by_name.keys()),
                         set(['time', 'model_level_number']))
        self.assertEqual(set([id(v) for v in plots_by_name['time']]),
                         set([c1_id, c2_id]))
        self.assertEqual([id(v) for v in plots_by_name['model_level_number']],
                         [c2_id])
        # Check names_by_plot_id.
        names_by_plot_id = browser._names_by_plot_id
        self.assertEqual(set(names_by_plot_id.keys()), set([c1_id, c2_id]))
        self.assertEqual(names_by_plot_id[c1_id], ['time'])
        self.assertEqual(set(names_by_plot_id[c2_id]),
                         set(['time', 'model_level_number']))

    def test_two_plots_with_independent_axes(self):
        c1 = Contour(self.cube, self.axes)
        levels = 5
        other = _add_levels(self.cube, levels)[:, 0]
        c2 = Contour(other, self.axes)
        browser = Browser([c1, c2])
        tcoord = self._tidy(self.cube.coord('time'))
        zcoord = self._tidy(other.coord('model_level_number'))
        # Check axis_by_name.
        taxis = _AxisDefn(dim=0, name='time', size=7, coord=tcoord)
        zaxis = _AxisDefn(dim=0, name='model_level_number', size=levels,
                          coord=zcoord)
        axis_by_name = browser._axis_by_name
        expected = dict(time=taxis, model_level_number=zaxis)
        self.assertEqual(axis_by_name, expected)
        # Check plots_by_name.
        c1_id, c2_id = id(c1), id(c2)
        plots_by_name = browser._plots_by_name
        self.assertEqual(set(plots_by_name.keys()),
                         set(['time', 'model_level_number']))
        self.assertEqual([id(v) for v in plots_by_name['time']],
                         [c1_id])
        self.assertEqual([id(v) for v in plots_by_name['model_level_number']],
                         [c2_id])
        # Check names_by_plot_id.
        names_by_plot_id = browser._names_by_plot_id
        self.assertEqual(set(names_by_plot_id.keys()), set([c1_id, c2_id]))
        self.assertEqual(names_by_plot_id[c1_id], ['time'])
        self.assertEqual(names_by_plot_id[c2_id], ['model_level_number'])

    def test_two_plots_with_shared_alias_axis(self):
        coords = ('time', 'grid_longitude')
        c1 = Contour(self.cube, self.axes, coords=coords)
        c1.alias(wibble=1)
        c2 = Contour(self.cube, self.axes, coords=coords)
        c2.alias(wibble=1)
        browser = Browser([c1, c2])
        # Check axis_by_name.
        axis = _AxisAlias(dim=1, name='wibble', size=9)
        expected = dict(wibble=axis)
        self.assertEqual(browser._axis_by_name, expected)
        # Check plots_by_name.
        c1_id, c2_id = id(c1), id(c2)
        plots_by_name = browser._plots_by_name
        self.assertEqual(plots_by_name.keys(), ['wibble'])
        self.assertEqual(set([id(v) for v in plots_by_name['wibble']]),
                         set([c1_id, c2_id]))
        # Check names_by_plot_id.
        names_by_plot_id = browser._names_by_plot_id
        self.assertEqual(set(names_by_plot_id.keys()), set([c1_id, c2_id]))
        self.assertEqual(names_by_plot_id[c1_id], ['wibble'])
        self.assertEqual(names_by_plot_id[c2_id], ['wibble'])

    def test_two_plots_with_incompatible_axis_to_axis(self):
        c1 = Contour(self.cube, self.axes)
        other = self.cube.copy()[1:]
        c2 = Contour(other, self.axes)
        emsg = ("cube 'air_potential_temperature' has an incompatible axis "
                "'time' on dimension 0")
        with self.assertRaisesRegexp(ValueError, emsg):
            Browser([c1, c2])

    def test_two_plots_with_incompatible_axis_to_alias_axis(self):
        c1 = Contour(self.cube, self.axes)
        c2 = Contour(self.cube, self.axes)
        c2.alias(time=0)
        emsg = ("cube 'air_potential_temperature' has an incompatible axis "
                "'time' on dimension 0")
        with self.assertRaisesRegexp(ValueError, emsg):
            Browser([c1, c2])

    def test_two_plots_with_incompatible_alias_axis_to_alias_axis(self):
        c1 = Contour(self.cube, self.axes)
        c1.alias(time=0)
        other = self.cube.copy()
        other.remove_coord('time')
        c2 = Contour(other, self.axes, coords=(0, 'grid_latitude'))
        c2.alias(time=2)
        emsg = ("cube 'air_potential_temperature' has an incompatible axis "
                "'time' on dimension 2")
        with self.assertRaisesRegexp(ValueError, emsg):
            Browser([c1, c2])


class Test_on_change(tests.IrisTest):
    def setUp(self):
        self.cube = realistic_3d()
        self.axes = mock.sentinel.axes
        self.patch('IPython.display.display')
        self.value = mock.sentinel.value
        mockers = [mock.Mock(value=self.value) for i in range(20)]
        self.patch('ipywidgets.SelectionSlider', side_effect=mockers)
        self.patch('ipywidgets.VBox')
        self.patch('matplotlib.pyplot.colorbar')

    def test(self):
        plot = Contour(self.cube, self.axes)
        with mock.patch('cube_browser.Browser.on_change') as on_change:
            browser = Browser(plot)
            browser.display()
            on_change.assert_called_once_with(None)

    def test_single_plot_with_no_axis(self):
        cube = self.cube[0]
        plot = Contour(cube, self.axes)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser(plot)
            browser.display()
            # Check the initial render - forced!.
            func.assert_called_once_with()

    def test_single_plot_with_axis(self):
        plot = Contour(self.cube, self.axes)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser(plot)
            browser.display()
            # Check the initial render.
            func.assert_called_once_with(time=self.value)
            # Now simulate a slider change.
            slider = browser._slider_by_name['time']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(time=self.value),
                        mock.call(time=self.value)]
            func.assert_has_calls(expected)

    def test_single_plot_with_alias_axis(self):
        plot = Contour(self.cube, self.axes)
        plot.alias(wibble=0)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser(plot)
            browser.display()
            # Check the initial render.
            func.assert_called_once_with(wibble=self.value)
            # Now simulate a slider change.
            slider = browser._slider_by_name['wibble']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(wibble=self.value),
                        mock.call(wibble=self.value)]
            func.assert_has_calls(expected)

    def test_two_plots_with_no_axis(self):
        cube = self.cube[0]
        c1 = Contour(cube, self.axes)
        c2 = Contour(cube, self.axes)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser([c1, c2])
            browser.display()
            # Check the initial render - forced!
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(), mock.call()]
            func.assert_has_calls(expected)

    def test_two_plots_with_shared_axis(self):
        coords = ('time', 'grid_latitude')
        c1 = Contour(self.cube, self.axes, coords=coords)
        c2 = Contour(self.cube, self.axes, coords=coords)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser([c1, c2])
            browser.display()
            # Check the initial render.
            expected = [mock.call(grid_longitude=self.value)]
            self.assertEqual(func.call_args_list, expected * 2)
            # Now simulate a slider change.
            slider = browser._slider_by_name['grid_longitude']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_args_list, expected * 4)

    def test_two_plots_with_shared_axis_and_independent_axis(self):
        c1 = Contour(self.cube, self.axes)
        levels = 10
        other = _add_levels(self.cube, levels)
        c2 = Contour(other, self.axes)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser([c1, c2])
            browser.display()
            # Check the initial render.
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(time=self.value),
                        mock.call(time=self.value,
                                  model_level_number=self.value)]
            func.assert_has_calls(expected)
            # Now simulate a 'time' slider change.
            slider = browser._slider_by_name['time']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 4)
            expected *= 2
            func.assert_has_calls(expected)
            # Now simulate a 'model_level_number' slider change.
            slider = browser._slider_by_name['model_level_number']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 5)
            expected.append(mock.call(time=self.value,
                                      model_level_number=self.value))
            func.assert_has_calls(expected)

    def test_two_plots_with_independent_axes(self):
        c1 = Contour(self.cube, self.axes)
        levels = 5
        other = _add_levels(self.cube, levels)[:, 0]
        c2 = Contour(other, self.axes)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser([c1, c2])
            browser.display()
            # Check the initial render.
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(time=self.value),
                        mock.call(model_level_number=self.value)]
            func.assert_has_calls(expected)
            # Now simulate a 'time' slider change.
            slider = browser._slider_by_name['time']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 3)
            expected.append(mock.call(time=self.value))
            func.assert_has_calls(expected)
            # Now simulate a 'model_level_number' slider change.
            slider = browser._slider_by_name['model_level_number']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 4)
            expected.append(mock.call(model_level_number=self.value))
            func.assert_has_calls(expected)

    def test_two_plots_with_shared_alias_axis(self):
        coords = ('time', 'grid_longitude')
        c1 = Contour(self.cube, self.axes, coords=coords)
        c1.alias(wibble=1)
        c2 = Contour(self.cube, self.axes, coords=coords)
        c2.alias(wibble=1)
        with mock.patch('cube_browser.Contour.__call__') as func:
            browser = Browser([c1, c2])
            browser.display()
            # Check the initial render.
            self.assertEqual(func.call_count, 2)
            expected = [mock.call(wibble=self.value)] * 2
            func.assert_has_calls(expected)
            # Now simulate a slider change.
            slider = browser._slider_by_name['wibble']
            change = dict(owner=slider)
            browser.on_change(change)
            self.assertEqual(func.call_count, 4)
            expected *= 2
            func.assert_has_calls(expected)


if __name__ == '__main__':
    tests.main()
