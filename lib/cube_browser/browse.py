import glob
import IPython.display
import ipywidgets
import iris

import cube_browser
IPython.display.clear_output()

class State(object):
    """the State of my notebook"""

#https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html
path = ipywidgets.Text(
    description='Path:',
    value=iris.sample_data_path('GloSea4'),
)
#IPython.display.display(path)

options = glob.glob('{}/*'.format(path.value))
options.sort()

files = ipywidgets.SelectMultiple(
    description='Files:',
    options=options,
    width='100%'
)
#IPython.display.display(files)

def handle_path(sender):
    options = glob.glob('{}/*'.format(path.value))
    options.sort()
    files.options = options

#path.on_submit(handle_submit)
# path is the widget which i want to observe
# the first argument is the function to run on 'event'
# names is the thing that i want know about, within path
path.observe(handle_path, names='value')


load_button = ipywidgets.Button(description="Load these Files!")



cubes_print = ipywidgets.Output()


cube_picker = ipywidgets.Dropdown(
    description='Cubes:',
    options={},
    width='100%'
)

def handle_load(sender):
    cubes = iris.load(files.value)
    cube_picker.options = dict([(cube.summary(shorten=True), cube) for cube in cubes])

load_button.on_click(handle_load)

plot_container = ''

def goplot(sender):
    cube = None
    cube = cube_picker.value
    if cube:
        IPython.display.clear_output()
        conf = cube_browser.Contourf(cube, ['longitude', 'latitude'])
        browser = cube_browser.Browser(conf)
        sender.plot_container.children=[browser.form]


plot_button = ipywidgets.Button(description="Plot my cube")
plot_button.plot_container = ipywidgets.Box()
plot_button.on_click(goplot)

container = ipywidgets.Box(children=[path, files, load_button, cubes_print, cube_picker, plot_button])

IPython.display.display(container)

IPython.display.display(plot_button.plot_container)
