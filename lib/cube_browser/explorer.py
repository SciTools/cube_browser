from collections import OrderedDict
import glob
import IPython.display
import ipywidgets
import iris
import matplotlib.pyplot as plt

import cube_browser

# Clear output, such as autosave disable notification.
IPython.display.clear_output()

class Explorer(object):
    """
    IPyWidgets and workflow for exploring collections of cubes.

    """
    def __init__(self):
        # Define the file system path for input files.
        self._path = ipywidgets.Text(
            description='Path:',
            value=iris.sample_data_path('GloSea4'))
        # Observe the path.
        self._path.observe(self._handle_path, names='value')
        # Use default path value to initialise file options.
        self._file_options = ['None'] + glob.glob('{}/*'.format(self._path.value))
        self._file_options.sort()
        # Defines the files selected to be loaded.
        self._files = ipywidgets.SelectMultiple(
            description='Files:',
            options=self._file_options,
            width='100%'
        )
        # Load action.
        self._load_button = ipywidgets.Button(description="Load these Files!")
        self._load_button.on_click(self._handle_load)

        self._subplots_axes = ipywidgets.RadioButtons(
            description = '(subplots, axes)',
            options = OrderedDict((('(1, 1)', (1, 1)),
                            ('(1, 2)', (1, 2)),
                            ('(2, 2)', (2, 2)))))

        for label in ['a', 'b']:
            # Defines the cube which is to be plotted.
            setattr(self, '_{}_plot_cube_picker'.format(label),
                    ipywidgets.Dropdown(
                        description = 'Cubes:',
                        options = {'None': None},
                        value = None,
                        width = '50%'
                    ))

            # Define the type of cube browser plot required
            setattr(self, '_{}_plot_type'.format(label),
                    ipywidgets.Dropdown(
                        description='Plot type:',
                        options={'pcolormesh': cube_browser.Pcolormesh,
                                 'contour': cube_browser.Contour,
                                 'contourf': cube_browser.Contourf},
                        value=cube_browser.Contour
                    ))

            setattr(self, '_{}_plot_x_coord'.format(label),
                    ipywidgets.Dropdown(
                        description='X Coord',
                        options=['None']
                    ))
            setattr(self, '_{}_plot_y_coord'.format(label),
                    ipywidgets.Dropdown(
                        description='Y Coord',
                        options=['None']
                    ))
            setattr(self, '_{}_plot_cmap'.format(label),
                    ipywidgets.Text(
                        description='colour map',
                    ))

        self._a_plot_cube_picker.observe(self._handle_a_cube_selection, names='value')
        self._b_plot_cube_picker.observe(self._handle_b_cube_selection, names='value')
        self._a_plot_cmap.observe(self._handle_a_cmap, names='value')
        self._b_plot_cmap.observe(self._handle_b_cmap, names='value')

        # Plot action.
        self._plot_button = ipywidgets.Button(description="Plot my cube")
        # Create a Box to manage the plot.
        self._plot_container = ipywidgets.Box()
        self._plot_button.on_click(self._goplot)

        # Define a container for the main controls in the browse interface.
        self.container = ipywidgets.Box(children=[self._path, self._files,
                                                  self._load_button,
                                                  self._subplots_axes])
        self._a_plot_container = ipywidgets.Box(children=[
                                                  self._a_plot_cube_picker,
                                                  self._a_plot_type,
                                                  self._a_plot_x_coord,
                                                  self._a_plot_y_coord,
                                                  self._a_plot_cmap,
                                                  ])

        self._b_plot_container = ipywidgets.Box(children=[
                                                  self._b_plot_cube_picker,
                                                  self._b_plot_type,
                                                  self._b_plot_x_coord,
                                                  self._b_plot_y_coord,
                                                  self._b_plot_cmap,
                                                  ])

        self.plot_container = ipywidgets.HBox(children=[self._a_plot_container,
                                                       self._b_plot_container])

        self._a_plot_mpl_kwargs = {}
        self._b_plot_mpl_kwargs = {}
        # Display the browse interface.
        IPython.display.display(self.container)
        IPython.display.display(self.plot_container)
        IPython.display.display(self._plot_button)

        IPython.display.display(self._plot_container)

    @property
    def a_plot_mpl_kwargs(self):
        """
        The dictionary of matplotlib keyword arguements in use for 'plot a'.

        """
        return self._a_plot_mpl_kwargs

    @a_plot_mpl_kwargs.setter
    def a_plot_mpl_kwargs(self, value):
        self._a_plot_mpl_kwargs = value
    
    @property
    def b_plot_mpl_kwargs(self):
        """
        The dictionary of matplotlib keyword arguements in use for 'plot b'.

        """
        return self._b_plot_mpl_kwargs

    @b_plot_mpl_kwargs.setter
    def b_plot_mpl_kwargs(self, value):
        self._b_plot_mpl_kwargs = value

    @property
    def cubes(self):
        """The list of cubes the explorer is currenlty working with."""
        return self._cubes

    def _handle_a_cmap(self, sender):
        cmap_string = self._a_plot_cmap.value
        self.a_plot_mpl_kwargs['cmap'] = cmap_string
        
    def _handle_b_cmap(self, sender):
        cmap_string = self._b_plot_cmap.value
        self.b_plot_mpl_kwargs['cmap'] = cmap_string
        
    def update_cubes_list(self):
        """Update the list of cubes available in the Explorer."""
        options = [(cube.summary(shorten=True), cube) for cube in self._cubes]
        self._a_plot_cube_picker.value = None
        self._a_plot_cube_picker.options = dict([('None', None)] + options)
        self._b_plot_cube_picker.value = None
        self._b_plot_cube_picker.options = dict([('None', None)] + options)
        # try:
        #     self._a_plot_cube_picker.value = options[0][1]
        #     self._a_plot_cube_picker.options = dict(options)
        # except TraitError:
        #     pass
        

    def _handle_path(self, sender):
        """Path box action."""
        options = glob.glob('{}/*'.format(self._path.value))
        options.sort()
        self._files.value = ()
        self._files.options = options

    def _handle_load(self, sender):
        """Load button action."""
        self._a_plot_cube_picker.options['None'] = None
        self._cubes = iris.load(self._files.value)
        self.update_cubes_list()

    def _handle_a_cube_selection(self, sender):
        """Cube selector action."""
        if self._a_plot_cube_picker.value is not None:
            self._a_plot_x_coord.options = ['None'] + [coord.name() for coord in
                               self._a_plot_cube_picker.value.coords(dim_coords=True)]
            self._a_plot_x_coord.value = self._a_plot_cube_picker.value.coord(axis='X').name()
            self._a_plot_y_coord.options = ['None'] + [coord.name() for coord in
                               self._a_plot_cube_picker.value.coords(dim_coords=True)]
            self._a_plot_y_coord.value = self._a_plot_cube_picker.value.coord(axis='Y').name()

    def _handle_b_cube_selection(self, sender):
        """Cube selector action."""
        if self._b_plot_cube_picker.value is not None:
            self._b_plot_x_coord.options = ['None'] + [coord.name() for coord in
                               self._b_plot_cube_picker.value.coords(dim_coords=True)]
            self._b_plot_x_coord.value = self._b_plot_cube_picker.value.coord(axis='X').name()
            self._b_plot_y_coord.options = ['None'] + [coord.name() for coord in
                               self._b_plot_cube_picker.value.coords(dim_coords=True)]
            self._b_plot_y_coord.value = self._b_plot_cube_picker.value.coord(axis='Y').name()

    def _goplot(self, sender):
        """Create the cube_browser.Plot2D and cube_browser.Browser"""
        IPython.display.clear_output()
        fig = plt.figure(figsize=(13, 8))
        cubes = [(self._a_plot_cube_picker.value, '_a_', 1,
                  self.a_plot_mpl_kwargs),
                 (self._b_plot_cube_picker.value, '_b_', 2,
                  self.b_plot_mpl_kwargs)]
        sub_plots = 110
        if self._subplots_axes.value[0] == 2:
            sub_plots = 120
            
        confs = []
        for cube, label, spl, mpl_kwargs in cubes:
            if cube:
                
                x_name = getattr(self, '{}plot_x_coord'.format(label)).value
                y_name = getattr(self, '{}plot_y_coord'.format(label)).value
                if (cube.coord(axis='X').name() == x_name and
                    cube.coord(axis='Y').name() == y_name):
                    projection = cube.coord_system().as_cartopy_projection()
                    if sub_plots == 120 or (sub_plots == 110 and spl == 1):
                        ax = fig.add_subplot(sub_plots+spl,
                                             projection=projection)
                        ax.coastlines()
                    else:
                        ax = plt.gca()
                else:
                    if sub_plots == 120 or (sub_plots == 110 and spl == 1):
                        ax = fig.add_subplot(sub_plots+spl)
                    else:
                        ax = plt.gca()
                    ax = fig.add_subplot(sub_plots+spl)
                plot_type = getattr(self, '{}plot_type'.format(label))
                confs.append(plot_type.value(cube, ax,
                                             coords=[x_name, y_name],
                                             **mpl_kwargs))
        self.browser = cube_browser.Browser(confs)
        self.browser.on_change(None)
        for label, plot in zip(['a_', 'b_'], confs):
            setattr(self, '{}plot_mpl_kwargs'.format(label), plot.kwargs)
        self._plot_container.children = [self.browser.form]
