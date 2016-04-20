Plotting Cubes
==============

This tutorial explains the first steps to working with Iris and Holoviews to 
create a simple cube browser.

Preparing the Plot
------------------

First you must load the cube you wish to view, and pass this to Holocube to 
make into a plot.

To do this, you will need to decide on what type of plot you would like to make 
(known as an Element_).

.. _Element: http://holoviews.org/Tutorials/Elements.html 

Once you have chosen your element, you can plot in two primary ways:

1. You can choose you axes dimensions and plot like this::

    plot = hc.HoloCube(cube)
    plot.to.image(['grid_longitude', 'grid_latitude'])
    
2. You can choose the dimension which you would like to scroll through like this::

    hc.HoloCube(cube).groupby(['time'], group_type=hc.Image)
    
Either way is valid, but the number of dimensions on your cube and which of 
those you would like your plot to scroll through may influence which method 
you choose.


