Cube Explorer Components
========================

Construction
------------

**Decide on options and widgets**

To start making your own Cube Explorer, you need to decide which options to offer when plotting your data.

The examples in the notebooks below show some of the options that you might want to offer, and the widgets that you could use to display them.
The syntax to create each widget is very similar, but some small aspects (like the widget type) differ.  The basic outline looks like this::

    x_selector = ipywidgets.ToggleButtons(
                        description='Dimension:',
                        options=coordinates,
                        value = 'time')

In this example, the ``x_selector`` widget could be used to provide the user with the option to select the dimension to plot on the x-axis (by default 'time' would be on the x-axis).

For more detailed guidance and a more complete list of widgets that are available, please visit the `ipywidgets <http://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html>`_ website.

**Construct one widget per cell**

Once you have decided what options and widgets you would like to present you can treat them as your individual components, each possessing a Jupyter notebook cell.
Each component can be displayed using this line at the bottom of the cell::

    IPython.display.display()

**Make plotting button**

At the end of your notebook you will need to add a cell which creates your plots using the values selected in the options widgets.  This will incorporate the Browser call.
It is convenient to make a button to achieve this (see button example below) as it will be necessary at a later stage of Explorer development.

Usage
-----

To use your Explorer, run a cell to produce your selection widget and make the selection for that widget before running the next cell.
If you would like to change any of your options retrospectively, you will have to re-run the following widget after that change to ensure that the values update.
This is important if you have any dependencies between widgets (see Options List for an example of this).


Links to Notebooks:
-------------------

:download:`Value Catcher <ValueCatcher.ipynb>`

:download:`Dimension Picker 1 <DimPicker1.ipynb>`

:download:`Dimension Picker 2 <DimPicker2.ipynb>`

:download:`Dimension Picker 3 <DimPicker3.ipynb>`

:download:`Plot Type Picker <iplotPicker.ipynb>`

:download:`Options List <OptionsCascade.ipynb>`

:download:`Button <Button.ipynb>`

Extra Notebook:
---------------
This is a link to a collection of components which are not linked together:

:download:`Workflow <Workflow1.ipynb>`


Linking up your Widgets
-----------------------

If you have more than one option widget in any Explorer notebook, the process of re-running cells after every options selection soon becomes cumbersome and confusing.
The following page demonstrates how you can construct connections between the components so that they can pass information between each other without the need to re-run.





