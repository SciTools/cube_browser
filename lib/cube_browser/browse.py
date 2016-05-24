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
# path is the widget which i want to observe
# the first argument is the function to run on 'event'
# names is the thing that i want know about, within path
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
def handle_load(sender):
    cubes = iris.load(files.value)
    cube_picker.options = dict([(cube.summary(shorten=True), cube) for cube in cubes])
load_button.on_click(handle_load)

# Widget for cube description.
cubes_print = ipywidgets.Output()

# Defines the cube which is to be plotted.
cube_picker = ipywidgets.Dropdown(
    description='Cubes:',
    options={},
    width='100%'
)

# Plot action.
plot_button = ipywidgets.Button(description="Plot my cube")
# Create a Box and make the plot button contain this object.
plot_button.plot_container = ipywidgets.Box()
def goplot(sender):
    cube = None
    cube = cube_picker.value
    if cube:
        IPython.display.clear_output()
        fig = plt.figure()
        projection = cube.coord_system().as_cartopy_projection()
        ax = fig.add_subplot(111, projection=projection)
        conf = cube_browser.Contourf(cube, ax, ['longitude', 'latitude'])
        if projection:
            ax.coastlines()
        browser = cube_browser.Browser(conf)
        sender.plot_container.children = [browser.form]
plot_button.on_click(goplot)

# Define a container for the main controls in the browse interface.
container = ipywidgets.Box(children=[path, files, load_button, cubes_print,
                                     cube_picker, plot_button])

# Display the browse interface.
IPython.display.display(container)

IPython.display.display(plot_button.plot_container)
