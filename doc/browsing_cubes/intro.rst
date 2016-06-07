Browsing Cubes
==============

The Cube Browser package enables you to visualize your `Iris cubes <http://scitools.org.uk/iris/docs/latest/userguide/iris_cubes.html>`_ in a Jupyter notebook.
Cube Browser utilizes Python and the Matplotlib, Iris and Cartopy libraries while offering the additional functionality of plotting an entire cube without having to slice it.

You can make use of the Cube Browser library to write a short notebook to display your Iris cube data.
There are several advantages of using this approach, most notably the flexibility in the options you can apply to each plot and the relative ease with which you can achieve this.
Additionally, if you know what plots you would like and how you would like them laid out, this is a very quick way of producing your plots and exploring your cube data.
You can also apply the same notebook to many different data sets at different times or with different customizations.

Making Your Plots
-----------------

**Prepare your cube**

Before you make your plot, you first have to choose and load the Iris cubes that you would like to visualize.
If you need to perform any data manipulation on the cube, such as aggregating, collapsing or cube maths, this should also be done prior to plotting.

**Configure axes**

Cube Browser uses matplotlib functionality, so you must set up your axes in the layout that you desire for your plots.
The steps that are required here are that you define your map projection
(you can use the Iris convenience function `iplt.default_projection <http://scitools.org.uk/iris/docs/latest/iris/iris/plot.html#iris.plot.default_projection>`_ if this is appropriate),
and that you define the number of axes and subplots that you need for your layout.  Here is an example::

    projection = iplt.default_projection(air_potential_temperature)
    ax1 = plt.subplot(111, projection=projection)

**Define plots**

The plot types that you can choose from are: Contourf, Contour and Pcolormesh.  These plot types mirror those in matplotlib, as do the keyword arguments that you can pass in here.
Please see the `matplotlib documentation <http://matplotlib.org/api/pyplot_api.html?highlight=contour#matplotlib.pyplot.contour>`_ for a full docstring and list of keyword arguments.

You can define your plot using the following syntax (more examples are available in the links below)::

    plot = Contour(cube, ax1)

**Display**

Finally, you need to make the call to the Browser class to construct the plots with their sliders and arrange them in your chosen layout.  Here is how you can do this::

    Browser([plot]).display()

The example described above shows how to plot a single cube on a single set of axes, but you can also use Cube Browser to make combinations of plots, for example side-by-side plots or overlays.
The links below are examples of how you can achieve these.


Example Notebooks
-----------------

`four-axes example <https://nbviewer.jupyter.org/urls/gist.githubusercontent.com/corinnebosley/2fbc9fcb329a2459d926c82eb94386b4/raw/92cfe3b056532e0a469319388495ce4bc212a926/four_axes.ipynb>`_

`overlay example <https://nbviewer.jupyter.org/urls/gist.githubusercontent.com/corinnebosley/7376f8919958027123f2f8ebdb508df3/raw/be561d438842d810fefcf0a90555e4acb8e9dd3c/overlay.ipynb>`_
