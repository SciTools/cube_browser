Cube Browser Components
=======================

Construction
------------

**Decide on options and widgets**

To start making your Explorer, you need to decide which aspects of cube plotting you would like to offer selections for and which aspects you would like to hard code.
The examples in the notebooks below show some of the options that you might want to use, and the widgets that you could use to display them.
The syntax to create each widget is very similar, but for more detailed guidance and a more complete list of widgets that are available, please visit the `ipywidgets <http://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html>`_ website.

**Construct one widget per cell**

Once you have decided what options to offer and which widgets to use for them, you can treat them as your individual components, each possessing a Jupyter notebook cell.
Each component can be displayed using this line at the bottom of the cell:

```python
IPython.display.display()
```

**Make plotting button**

At the end of your notebook you will need to add a cell which creates your plots using the values selected in the options widgets.  This will incorporate the Browser() call.
It is convenient to make a button to achieve this (see `button example <wherever/this/is.html>`_) as it will be necessary at a later stage of Explorer development.

Usage
-----

To use your Explorer, run a cell to produce your selection widget and make the selection for that widget before running the next cell.
If you would like to change any of your options retrospectively, you will have to re-run the following widget after that change to ensure that the values update.
This is important if you have any dependencies between widgets (see `OptionsCascade <however/we/link/notebooks.html>`_ for an example of this).


Links to Notebooks:
-------------------

DimPicker.link

iplotPicker.link

OptionsCascade.link

ValueCatcher.link

*Make a notebook example of a button for this space*

Extra Notebook:
---------------
This is a link to a collection of components which are not linked together:

Workflow1.link


Linking up your Widgets
-----------------------

If you have more than one options widget in any Explorer notebook, the process of re-running cells after every options selection soon becomes cumbersome and confusing.
The following page demonstrates how you can construct connections between the components so that they can pass information between each other without having to re-run.





