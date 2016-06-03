Cube Browser Connections
========================

Composing Connections
---------------------

For widgets which possess hard coded options, the only elements you need are the list of input options and the widget itself.
Widgets that depend on the response of previous selections need:
    - The list of input options
    - The widget itself
    - A function defining what to change the input options to if a selection occurs in an influencing widget
    - A statement to observe the influencing widget and execute the function upon event of a change.

While you are adding these elements to your notebook, you will also benefit from moving all your widgets into a single cell so that they can communicate with each other without having to re-run.
When you have done this, you can create containers to display groups of widgets instead of having to display each one individually.

You can see an example with a detailed description of how to compose these elements `here <however/we/get/to/interaction2.ipynb.html>`_.

Links to Notebooks:
-------------------

filePickerSimple.link

interactions2.link



