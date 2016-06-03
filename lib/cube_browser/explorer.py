from collections import OrderedDict
import glob
import IPython.display
import ipywidgets
import iris
import matplotlib.pyplot as plt
import os
import traitlets

import cube_browser

# Clear output, such as autosave disable notification.
IPython.display.clear_output()

class FilePicker(object):
    """
    File picker widgets.
    """
    def __init__(self):
        # Define the file system path for input files.
        self._path = ipywidgets.Text(
            description='Path:',
            value=iris.sample_data_path('GloSea4'),
            width="100%")
        # Observe the path.
        self._path.observe(self._handle_path, names='value')
        # Use default path value to initialise file options.
        self._file_options = []
        if os.path.exists(self._path.value):
            self._file_options = glob.glob('{}/*'.format(self._path.value))
            self._file_options.sort()
        # Defines the files selected to be loaded.
        self._files = ipywidgets.SelectMultiple(
            description='Files:',
            options=OrderedDict([(os.path.basename(f), f)
                                 for f in self._file_options]),
            width="100%"
        )
        self._box = ipywidgets.Box(children=[self._path, self._files],
                                   width="100%")

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
                                               for f in self._file_options])
        else:
            self._files.options = OrderedDict()

    @property
    def box(self):
        """The IPywidgets box to display."""
        return self._box


class PlotControl(object):
    """Control widgets for a plot."""
    def __init__(self):
        self.mpl_kwargs = {}
        # Defines the cube which is to be plotted.
        self.cube_picker = ipywidgets.Dropdown(
            description = 'Cubes:',
            options = {'None': None},
            value = None,
            width = '50%')

        # Define the type of cube browser plot required
        self.plot_type = ipywidgets.Dropdown(
            description='Plot type:',
            options={'pcolormesh': cube_browser.Pcolormesh,
                     'contour': cube_browser.Contour,
                     'contourf': cube_browser.Contourf},
            value=cube_browser.Contour)

        self.x_coord = ipywidgets.Dropdown(
            description='X Coord',
            options=['None'])
        self.y_coord = ipywidgets.Dropdown(
            description='Y Coord',
            options=['None'])
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
            self.x_coord.options = ['None'] + [coord.name() for coord in
                               self.cube_picker.value.coords(dim_coords=True)]
            self.x_coord.value = self.cube_picker.value.coord(axis='X').name()
            self.y_coord.options = ['None'] + [coord.name() for coord in
                               self.cube_picker.value.coords(dim_coords=True)]
            self.y_coord.value = self.cube_picker.value.coord(axis='Y').name()

    def _handle_cmap(self, sender):
        # This should test colour map string is valid: and warn.
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
    def __init__(self):
        self.file_pickers = [FilePicker()]
        # Load action.
        self._load_button = ipywidgets.Button(description="load these files")
        self._load_button.on_click(self._handle_load)
        self._file_tab_button = ipywidgets.Button(description="add tab")
        self._file_tab_button.on_click(self._handle_new_tab)

        self._subplots = ipywidgets.RadioButtons(
            description = 'subplots',
            options = [1, 2])

        self.plot_controls = [PlotControl(), PlotControl()]

        # Plot action.
        self._plot_button = ipywidgets.Button(description="Plot my cube")
        # Create a Box to manage the plot.
        self._plot_button.on_click(self._goplot)
        self._cubes = traitlets.List()

        self.layout()

    def layout(self):
        self._plot_container = ipywidgets.Box()
        # Define a container for the main controls in the browse interface.
        self.ftabs = ipywidgets.Tab(children=[fp.box for fp in self.file_pickers])
        self.bbox = ipywidgets.HBox(children=[self._load_button,
                                         self._file_tab_button])
        self._file_picker_tabs = ipywidgets.Box(children=[self.ftabs, self.bbox])

        pcc_children = [pc.box for pc in self.plot_controls]
        self._plot_control_container = ipywidgets.Tab(children=pcc_children)

        acc_children = [self._file_picker_tabs, self._subplots,
                        self._plot_control_container]
        self._accord = ipywidgets.Accordion(children=acc_children)
        self._accord.set_title(0, 'Files')
        self._accord.set_title(1, 'SubPlots')
        self._accord.set_title(2, 'Plots')

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

    @traitlets.observe('self._cubes')
    def update_cubes_list(self):
        """Update the list of cubes available in the Explorer."""
        options = [('{}: {}'.format(i, cube.summary(shorten=True)), cube) for i, cube in enumerate(self._cubes)]
        for pc in self.plot_controls:
            pc.cube_picker.value = None
            pc.cube_picker.options = dict([('None', None)] + options)

    def _handle_load(self, sender):
        """Load button action."""
        fpfs = [fp.files for fp in self.file_pickers]
        selected_files = reduce(list.__add__, (list(files) for files in fpfs))
        self._cubes = iris.load(selected_files)
        self.update_cubes_list()

    def _handle_new_tab(self, sender):
        """Add new file tab."""
        self.file_pickers.append(FilePicker())
        self.ftabs = ipywidgets.Tab(children=[fp.box for fp in self.file_pickers])
        self._file_picker_tabs.children = [self.ftabs, self.bbox]

    def _goplot(self, sender):
        """Create the cube_browser.Plot2D and cube_browser.Browser"""
        IPython.display.clear_output()
        fig = plt.figure(figsize=(12, 6))
        sub_plots = 110
        if self._subplots.value == 2:
            sub_plots = 120
            
        confs = []
        for spl, pc in enumerate(self.plot_controls):
            spl+=1
            cube = pc.cube_picker.value
            if cube and spl <= self._subplots.value:
                x_name = pc.x_coord.value
                y_name = pc.y_coord.value
                if (cube.coord(axis='X').name() == x_name and
                    cube.coord(axis='Y').name() == y_name):
                    projection = cube.coord_system().as_cartopy_projection()
                    ax = fig.add_subplot(sub_plots+spl,
                                         projection=projection)
                    ax.coastlines()
                else:
                    ax = plt.gca()
                    ax = fig.add_subplot(sub_plots+spl)
                plot_type = pc.plot_type
                confs.append(plot_type.value(cube, ax,
                                             coords=[x_name, y_name],
                                             **pc.mpl_kwargs))
        self.browser = cube_browser.Browser(confs)
        self.browser.on_change(None)
        # For each PlotControl, assign the plot's mpl_kwargs back to
        # that PlotControl.
        for pc, plot in zip(self.plot_controls, confs):
            pc.mpl_kwargs = plot.kwargs
        self._plot_container.children = [self.browser.form]
