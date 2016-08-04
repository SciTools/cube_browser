from collections import OrderedDict
import glob
import os
try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

import IPython.display
import cartopy.crs as ccrs
import ipywidgets
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
import traitlets

import cube_browser

# Clear output, such as autosave disable notification.
IPython.display.clear_output()


class FilePicker(object):
    """
    File picker widgets.
    """
    def __init__(self, initial_value='', default=''):
        if initial_value == '':
            try:
                initial_value = iris.sample_data_path('')
            except ValueError:
                initial_value = ''
        # Define the file system path for input files.
        self._path = ipywidgets.Text(
            description='Path:',
            value=initial_value,
            width="100%")
        # Observe the path.
        self._path.observe(self._handle_path, names='value')
        # Use default path value to initialise file options.
        options = []
        if os.path.exists(self._path.value):
            options = glob.glob('{}/*'.format(self._path.value))
            options.sort()
        default_list = []
        for default_value in default.split(','):
            if default_value in options:
                default_list.append(default_value)
        default_tuple = tuple(default_list)

        # Defines the files selected to be loaded.
        self._files = ipywidgets.SelectMultiple(
            description='Files:',
            options=OrderedDict([(os.path.basename(f), f)
                                 for f in options]),
            value=default_tuple,
            width="100%"
        )
        self.deleter = ipywidgets.Button(description='delete tab',
                                         height='32px', width='75px')
        hbox = ipywidgets.HBox(children=[self._files, self.deleter])
        self._box = ipywidgets.Box(children=[self._path, hbox], width="100%")

    @property
    def files(self):
        """The files from the FilePicker."""
        return self._files.value

    def _handle_path(self, sender):
        """Path box action."""
        if os.path.exists(self._path.value):
            options = glob.glob('{}/*'.format(self._path.value))
            options.sort()
            self._files.value = ()
            self._files.options = OrderedDict([(os.path.basename(f), f)
                                               for f in options])
        else:
            self._files.options = OrderedDict()
        self._files.width = "100%"

    @property
    def box(self):
        """The IPywidgets box to display."""
        return self._box


class PlotControl(object):
    """Control widgets for a plot."""
    def __init__(self):
        self.mpl_kwargs = {}
        # Defines the cube which is to be plotted.
        self.cube_picker = ipywidgets.Dropdown(description='Cubes:',
                                               options=('None', None),
                                               value=None,
                                               width='50%')

        # Define the type of cube browser plot required
        self.plot_type = ipywidgets.Dropdown(
            description='Plot type:',
            options={'pcolormesh': cube_browser.Pcolormesh,
                     'contour': cube_browser.Contour,
                     'contourf': cube_browser.Contourf},
            value=cube_browser.Pcolormesh)

        self.x_coord = ipywidgets.Dropdown(
            description='X Coord',
            options=('None', None))
        self.y_coord = ipywidgets.Dropdown(
            description='Y Coord',
            options=('None', None))
        self.cmap = ipywidgets.Text(
            description='colour map')

        # Handle events:
        self.cube_picker.observe(self._handle_cube_selection,
                                 names='value')
        self.cmap.observe(self._handle_cmap, names='value')
        self.plot_type.observe(self._handle_plot_type, names='value')

        self._box = ipywidgets.Box(children=[self.cube_picker,
                                             self.plot_type,
                                             self.x_coord,
                                             self.y_coord,
                                             self.cmap])

    def _handle_cube_selection(self, sender):
        """Cube selector action."""
        if self.cube_picker.value is not None:
            cube = self.cube_picker.cubes[self.cube_picker.value]
            options = [('None', None)]
            options += [(coord.name(), coord.name()) for coord in
                        cube.coords(dim_coords=True)]
            ndims = cube.ndim
            for i in range(ndims):
                options.append(('dim{}'.format(i), i))
            self.x_coord.options = options
            if (cube.coords(axis='X', dim_coords=True) and
               cube.coord(axis='X', dim_coords=True).name() in
               [o[1] for o in self.x_coord.options]):
                default = cube.coord(axis='X', dim_coords=True).name()
                self.x_coord.value = default
            self.y_coord.options = options
            if (cube.coords(axis='Y', dim_coords=True) and
               cube.coord(axis='Y', dim_coords=True).name() in
               [o[1] for o in self.y_coord.options]):
                default = cube.coord(axis='Y', dim_coords=True).name()
                self.y_coord.value = default

    def _handle_cmap(self, sender):
        # This tests that the colour map string is valid: else warns.
        from matplotlib.cm import cmap_d
        cmap_string = self.cmap.value
        if cmap_string and cmap_string in cmap_d.keys():
            self.mpl_kwargs['cmap'] = cmap_string
            self.cmap.description = 'colour map'
        else:
            self.cmap.description = 'not a cmap'

    def _handle_plot_type(self, sender):
        cmap = self.cmap.value
        self.mpl_kwargs = {}
        if cmap:
            self.mpl_kwargs['cmap'] = cmap

    @property
    def box(self):
        """The IPywidgets box to display."""
        return self._box


class Explorer(traitlets.HasTraits):
    """
    IPyWidgets and workflow for exploring collections of cubes.

    """
    _cubes = traitlets.List()

    def __init__(self, url=''):
        self.file_pickers = []
        if url:
            o = urlparse(url)
            query = parse_qs(o.query)
            pwd, = query.get('pwd', [''])
            for fname in query.get('files', []):
                self.file_pickers.append(FilePicker(pwd, os.path.join(pwd, fname)))
            for fpath in query.get('folders', []):
                self.file_pickers.append(FilePicker(fpath))
        if not self.file_pickers:
            self.file_pickers.append(FilePicker())

        # Define load action.
        self._load_button = ipywidgets.Button(description="load these files")
        self._load_button.on_click(self._handle_load)
        self._file_tab_button = ipywidgets.Button(description="add tab")
        self._file_tab_button.on_click(self._handle_new_tab)

        self._subplots = ipywidgets.RadioButtons(description='subplots',
                                                 options=[1, 2])
        self._subplots.observe(self._handle_nplots, names='value')

        # Plot action button.
        self._plot_button = ipywidgets.Button(description="Plot my cube")
        self._plot_button.on_click(self._goplot)

        # Configure layout of the Explorer.
        self._plot_container = ipywidgets.Box()
        # Define a Tab container for the main controls in the browse interface.
        children = [fp.box for fp in self.file_pickers]
        self.ftabs = ipywidgets.Tab(children=children)
        children = [self._load_button, self._file_tab_button]
        self.bbox = ipywidgets.HBox(children=children)
        children = [self.ftabs, self.bbox]
        self._file_picker_tabs = ipywidgets.Box(children=children)

        # Define the plot controls, start with 1 (self._subplots default)
        self.plot_controls = [PlotControl()]
        pcc_children = [pc.box for pc in self.plot_controls]
        self._plot_control_container = ipywidgets.Tab(children=pcc_children)
        self._plot_control_container.set_title(0, 'Plot Axes 0')

        # Define an Accordian for files, subplots and plots
        acc_children = [self._file_picker_tabs, self._subplots,
                        self._plot_control_container]
        self._accord = ipywidgets.Accordion(children=acc_children)
        self._accord.set_title(0, 'Files')
        self._accord.set_title(1, 'SubPlots')
        self._accord.set_title(2, 'Plots')

        # Initialise cubes container
        self._cubes = []

        # Display the browse interface.
        IPython.display.display(self._accord)
        IPython.display.display(self._plot_button)
        IPython.display.display(self._plot_container)

    @property
    def mpl_kwargs(self):
        """
        The list of dictionaries of matplotlib keyword arguements in use
        the PlotControls.

        """
        return [pc.mpl_kwargs for pc in self.plot_controls]

    @property
    def cubes(self):
        """The list of cubes the explorer is currently working with."""
        return self._cubes

    @cubes.setter
    def cubes(self, new_cubes):
        """To update the list of cubes the explorer is working with."""
        self._cubes = new_cubes

    @traitlets.observe('_cubes')
    def update_cubes_list(self, change=None):
        """
        Update the list of cubes available in the Explorer.
        Assigning an updated list into `cubes` automatically runs this.

        """
        # Build options list, using index values into the cube list.
        # This avoids the loading of cube's data payload when the
        # widget tests equality on selection.
        options = [('{}: {}'.format(i, cube.summary(shorten=True)), i)
                   for i, cube in enumerate(self._cubes)]
        for pc in self.plot_controls:
            # Provide the cubes list to the cube_picker, to index into.
            pc.cube_picker.cubes = self._cubes
            pc.cube_picker.options = [('None', None)] + pc.cube_picker.options
            pc.cube_picker.value = None
            pc.cube_picker.options = [('None', None)] + options
            if options:
                pc.cube_picker.value = options[0][1]
                pc.cube_picker.options = options

    def _handle_load(self, sender):
        """Load button action."""
        IPython.display.clear_output()
        sender.description = 'loading......'
        fpfs = [fp.files for fp in self.file_pickers]
        selected_files = reduce(list.__add__, (list(files) for files in fpfs))
        # Reassigning into self._cubes updates the cube_pickers.
        self._cubes = iris.load(selected_files)
        self._cubes = self._cubes.concatenate()
        sender.description = 'files loaded, reload'
        IPython.display.clear_output()

    def _handle_new_tab(self, sender):
        """Add new file tab."""
        self.file_pickers.append(FilePicker(self.default_path))
        self._update_filepickers()

    def _update_filepickers(self):
        children = [fp.box for fp in self.file_pickers]
        for i, child in enumerate(children):
            fp.deleter.index = i
            fp.deleter.on_click(self._handle_delete_tab)
        self.ftabs = ipywidgets.Tab(children=children)
        self._file_picker_tabs.children = [self.ftabs, self.bbox]

    def _handle_delete_tab(self, sender):
        """remove a file tab"""
        self.file_pickers.pop(sender.index)
        self._update_filepickers()

    def _handle_nplots(self, sender):
        if self._subplots.value == 1:
            self.plot_controls = [self.plot_controls[0]]
        elif self._subplots.value == 2:
            self.plot_controls = [self.plot_controls[0], PlotControl()]
        pcc_children = [pc.box for pc in self.plot_controls]
        self._plot_control_container.children = pcc_children
        for i in range(self._subplots.value):
            label = 'Plot Axes {}'.format(i)
            self._plot_control_container.set_title(i, label)
        self.update_cubes_list()

    def _goplot(self, sender):
        """Create the cube_browser.Plot2D and cube_browser.Browser"""
        IPython.display.clear_output()
        fig = plt.figure(figsize=(16, 7))
        sub_plots = 110
        if self._subplots.value == 2:
            sub_plots = 120

        confs = []
        for spl, pc in enumerate(self.plot_controls):
            spl += 1
            cube = None
            if pc.cube_picker.value is not None:
                cube = self.cubes[pc.cube_picker.value]
            if cube and spl <= self._subplots.value:
                pc_x_name = pc.x_coord.value
                pc_y_name = pc.y_coord.value
                x_coords = cube.coords(axis='X', dim_coords=True)
                if len(x_coords) == 1:
                    x_name = x_coords[0].name()
                else:
                    x_name = None
                y_coords = cube.coords(axis='Y', dim_coords=True)
                if len(y_coords) == 1:
                    y_name = y_coords[0].name()
                else:
                    y_name = None
                if x_name == pc_x_name and y_name == pc_y_name:
                    proj = iplt.default_projection(cube) or ccrs.PlateCarree()
                    ax = fig.add_subplot(sub_plots + spl, projection=proj)
                    # If the spatial extent is small, use high-res coastlines
                    extent = iplt.default_projection_extent(cube)
                    x0, y0 = ccrs.PlateCarree().transform_point(extent[0],
                                                                extent[2],
                                                                proj)
                    x1, y1 = ccrs.PlateCarree().transform_point(extent[1],
                                                                extent[3],
                                                                proj)
                    if x1-x0 < 20 and y1-y0 < 20:
                        ax.coastlines(resolution='10m')
                    elif x1-x0 < 180 and y1-y0 < 90:
                        ax.coastlines(resolution='50m')
                    else:
                        ax.coastlines()
                else:
                    ax = plt.gca()
                    ax = fig.add_subplot(sub_plots+spl)
                plot_type = pc.plot_type
                coords = [pc_x_name, pc_y_name]
                confs.append(plot_type.value(cube, ax, coords=coords,
                                             **pc.mpl_kwargs))
                title = cube.name().replace('_', ' ').capitalize()
                ax.set_title(title)
        self.browser = cube_browser.Browser(confs)
        self.browser.on_change(None)
        # For each PlotControl, assign the plot's mpl_kwargs back to
        # that PlotControl.
        for pc, plot in zip(self.plot_controls, confs):
            pc.mpl_kwargs = plot.kwargs
        self._plot_container.children = [self.browser.form]
