Cube Explorer Connections
=========================

To run a notebook with multiple options widgets, it is often convenient to connect the components.  This allows the widgets to automatically update selection changes.


Composing Connections
---------------------

For widgets which possess hard coded options, the only elements you need are the list of input options and the widget itself.
Widgets that depend on the response of previous selections need:
    - An initial list of input options
    - The widget itself
    - A function defining what change occurs on selection change in an influencing widget
    - A statement to observe the influencing widget and execute the function upon event of a change.

When adding these elements to your notebook, you could also benefit from moving all your widgets into a single cell.
Doing so means that the selection values will update without having to re-run all the cells that contain widgets.

At this point you may wish to display your widgets in a group, rather than one by one.
You can do this by adding them to a display tool called a container and displaying that instead, like so::

    container = ipywidgets.Box(children=[widget1, widget2])
    IPython.display.display(container)



You can see examples of how to compose and connect your widget elements below.

Links to Notebooks:
-------------------

:download:`Simple File Picker <filePickerSimple.ipynb>`

:download:`Interactions <interactions_1.ipynb>`



