import glob
import IPython.display
import ipywidgets
import iris
import matplotlib.pyplot as plt

import cube_browser

# Clear output, such as autosave disable notification.
IPython.display.clear_output()

# Defines the file system path for input files.
path = ipywidgets.Text(
    description='Path:',
    value=iris.sample_data_path('GloSea4'),
)
def handle_path(sender):
    options = glob.glob('{}/*'.format(path.value))
    options.sort()
    files.options = options
# 'path' is the widget which i want to observe:
# the first argument is the function to run on 'event',
# names is the thing that i want know about, within path
# the value.  'handle_path' is the resulting process,
# which runs when paths changes.
path.observe(handle_path, names='value')

# Use default path value to initialise file options.
options = glob.glob('{}/*'.format(path.value))
options.sort()

# Defines the files selected to be loaded.
files = ipywidgets.SelectMultiple(
    description='Files:',
    options=options,
    width='100%'
)

# Load action.
load_button = ipywidgets.Button(description="Load these Files!")
load_button.cubes = []

# Define load button action
def handle_load(sender):
    sender.cubes = iris.load(files.value)
    cube_picker.options = dict([(cube.summary(shorten=True), cube) for
                                cube in sender.cubes])
load_button.on_click(handle_load)

# Widget for cube description; currently non-functional:
# https://github.com/ipython/ipywidgets/issues/565
cubes_print = ipywidgets.Output()

# Defines the cube which is to be plotted.
cube_picker = ipywidgets.Dropdown(
    description='Cubes:',
    options={},
    width='100%'
)
# Define the behaviour of cube_picker interactions.
def handle_cube_selection(sender):
    x_coord.options = [coord.name() for coord in
                       cube_picker.value.coords(dim_coords=True)]
    x_coord.value = cube_picker.value.coord(axis='X').name()
    y_coord.options = [coord.name() for coord in
                       cube_picker.value.coords(dim_coords=True)]
    y_coord.value = cube_picker.value.coord(axis='Y').name()
    
cube_picker.observe(handle_cube_selection, names='value')

# Define the type of cube browser plot required
plot_type = ipywidgets.Dropdown(
    description='Plot type:',
    options={'pcolormesh': cube_browser.Pcolormesh,
             'contour': cube_browser.Contour,
             'contourf': cube_browser.Contourf},
    value=cube_browser.Pcolormesh
)

x_coord = ipywidgets.Dropdown(
    description='X Coordinate',
    options={}
)
y_coord = ipywidgets.Dropdown(
    description='Y Coordinate',
    options={}
)

# Plot action.
plot_button = ipywidgets.Button(description="Plot my cube")
plot_button.matplotlib_kwargs = {'cmap': 'seismic'}

# Create a Box to manage the plot.
plot_container = ipywidgets.Box()
# Create the cube_browser.Plot2D and cube_browser.Browser
# and mkae them the children of the plot_button's container.
def goplot(sender):
    cube = cube_picker.value
    if cube:
        IPython.display.clear_output()
        fig = plt.figure()
        x_name = x_coord.value
        y_name = y_coord.value
        if (cube.coord(axis='X').name() == x_name and
            cube.coord(axis='Y').name() == y_name):
            projection = cube.coord_system().as_cartopy_projection()
            ax = fig.add_subplot(111, projection=projection)
            ax.coastlines()
        else:
            ax = fig.add_subplot(111)
        conf = plot_type.value(cube, ax, coords=[x_name, y_name],
                               **sender.matplotlib_kwargs)
        browser = cube_browser.Browser(conf)
        plot_container.children = [browser.form]
plot_button.on_click(goplot)

# Define a container for the main controls in the browse interface.
container = ipywidgets.Box(children=[path, files, load_button, cubes_print,
                                     cube_picker, plot_type, x_coord, y_coord,
                                     plot_button])

# Display the browse interface.
IPython.display.display(container)

IPython.display.display(plot_container)
