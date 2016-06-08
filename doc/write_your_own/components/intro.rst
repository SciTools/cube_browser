Cube Explorer Components
========================

Construction
------------

**Decide on options and widgets**

To start making your own Cube Explorer, you need to decide which options to offer when plotting your data.

The examples in the notebooks below show some of the options that you might want to offer, and the widgets you could use to display them.
The syntax to create each widget is very similar, but some small aspects (like the widget type) differ.  The basic outline looks like this::

    x_selector = ipywidgets.ToggleButtons(
                        description='Dimension:',
                        options=coordinates,
                        value = 'time')

In this example, the ``x_selector`` widget could be used to provide the user with the option to select which dimension to plot on the x-axis (by default this would be 'time').

For more detailed guidance and a more complete list of widgets that are available, please visit the `ipywidgets <http://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html>`_ website.

Follow the links below to view some examples of widgets which could be used as components of a Cube Explorer.


:download:`Text Input Box <ValueCatcher.ipynb>`

:download:`Toggle Button Menu <DimPicker1.ipynb>`

:download:`Radio Button Menu <DimPicker2.ipynb>`

:download:`Dropdown Menu <DimPicker3.ipynb>`

:download:`Plot Type Selector (Dropdown) <iplotPicker.ipynb>`


**Construct one widget per cell**

Once you have decided what options and widgets you would like to present you can treat them as your individual components by containing each one in a single Jupyter notebook cell.
Each component can be displayed using this line at the bottom of the cell::

    IPython.display.display()

**Make plotting button**

Finally, at the end of your notebook you will need a cell that creates your plots using the values selected in the options widgets.  This will incorporate the Cube Browser call, like so::

    Browser([plot_name]).display()

It is convenient to make a button to achieve this (see button example below) as it will be necessary at a later stage of Explorer development.

:download:`Plotting Button <Button.ipynb>`


Usage
-----

To use your Cube Explorer, you must run each cell consecutively to produce your widgets and store your selected values.
Hence, as you run each cell, you set your value for the widget before running the next.

If you would like to change any of your selections retrospectively, you will have to re-run all following cells to ensure that the values update.
This is important if you have any dependencies between widgets (see following notebook links for examples of this).


:download:`Options List <OptionsCascade.ipynb>`

:download:`Selection Process <Workflow1.ipynb>`


Linking up your Widgets
-----------------------

If you have more than one selection widget in any Cube Explorer notebook, the process of re-running cells after every selection soon becomes cumbersome and confusing.
This can be overcome by connecting the component widgets in order to pass information between them.

Press Next to see the 'Cube Explorer Connections' page of this tutorial, which demonstrates how you can construct these connections.





