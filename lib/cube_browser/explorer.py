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
        # Defines the file system path for input files.
        self.path = ipywidgets.Text(
            description='Path:',
            value=iris.sample_data_path('GloSea4'))
        # Observe the path.
        self.path.observe(self.handle_path, names='value')
        # Use default path value to initialise file options.
        self.options = ['None'] + glob.glob('{}/*'.format(self.path.value))
        self.options.sort()
        # Defines the files selected to be loaded.
        self.files = ipywidgets.SelectMultiple(
            description='Files:',
            options=self.options,
            width='100%'
        )
        # Load action.
        self.load_button = ipywidgets.Button(description="Load these Files!")
        self.load_button.on_click(self.handle_load)
        self.cubes = []

        # Widget for cube description; currently non-functional:
        # https://github.com/ipython/ipywidgets/issues/565
        self.cubes_print = ipywidgets.Output()

        # Defines the cube which is to be plotted.
        self.cube_picker = ipywidgets.Dropdown(
            description = 'Cubes:',
            options = {'None': None},
            value = None,
            width = '100%'
        )

        self.cube_picker.observe(self.handle_cube_selection, names='value')

        # Define the type of cube browser plot required
        self.plot_type = ipywidgets.Dropdown(
            description='Plot type:',
            options={'pcolormesh': cube_browser.Pcolormesh,
                     'contour': cube_browser.Contour,
                     'contourf': cube_browser.Contourf},
            value=cube_browser.Pcolormesh
        )

        self.x_coord = ipywidgets.Dropdown(
            description='X Coordinate',
            options=['None']
        )
        self.y_coord = ipywidgets.Dropdown(
            description='Y Coordinate',
            options=['None']
        )

        # Plot action.
        self.plot_button = ipywidgets.Button(description="Plot my cube")
        # Create a Box to manage the plot.
        self.plot_container = ipywidgets.Box()
        self.plot_button.on_click(self.goplot)

        # Define a container for the main controls in the browse interface.
        self.container = ipywidgets.Box(children=[self.path, self.files,
                                                  self.load_button,
                                                  self.cubes_print,
                                                  self.cube_picker,
                                                  self.plot_type,
                                                  self.x_coord,
                                                  self.y_coord,
                                                  self.plot_button])

        # Display the browse interface.
        IPython.display.display(self.container)

        IPython.display.display(self.plot_container)


    def handle_path(self, sender):
        """Path box action."""
        options = glob.glob('{}/*'.format(self.path.value))
        options.sort()
        self.files.value = ()
        self.files.options = options

    def handle_load(self, sender):
        """Load button action."""
        self.cube_picker.options['None'] = None
        self.cubes = iris.load(self.files.value)
        options = [(cube.summary(shorten=True), cube) for cube in self.cubes]
        self.cube_picker.value = None
        self.cube_picker.options = dict([('None', None)] + options)
        try:
            self.cube_picker.value = options[0][1]
            self.cube_picker.options = dict(options)
        except Exception:
            pass

    def handle_cube_selection(self, sender):
        """Cube selector action."""
        if self.cube_picker.value is not None:
            self.x_coord.options = ['None'] + [coord.name() for coord in
                               self.cube_picker.value.coords(dim_coords=True)]
            self.x_coord.value = self.cube_picker.value.coord(axis='X').name()
            self.y_coord.options = ['None'] + [coord.name() for coord in
                               self.cube_picker.value.coords(dim_coords=True)]
            self.y_coord.value = self.cube_picker.value.coord(axis='Y').name()

    def goplot(self, sender):
        """Create the cube_browser.Plot2D and cube_browser.Browser"""
        cube = self.cube_picker.value
        if cube:
            IPython.display.clear_output()
            fig = plt.figure()
            x_name = self.x_coord.value
            y_name = self.y_coord.value
            if (cube.coord(axis='X').name() == x_name and
                cube.coord(axis='Y').name() == y_name):
                projection = cube.coord_system().as_cartopy_projection()
                ax = fig.add_subplot(111, projection=projection)
                ax.coastlines()
            else:
                ax = fig.add_subplot(111)
            conf = self.plot_type.value(cube, ax, coords=[x_name, y_name])
            self.browser = cube_browser.Browser(conf)
            self.browser.on_change(None)
            self.plot_container.children = [self.browser.form]
