Plotting Cubes
==============

This tutorial explains the first steps to working with Iris and Holoviews to 
create a simple cube browser.

.. notebook:: holocube plotting_examples.ipynb

.. note::

    The 'dynamic' keyword is used to reduce your memory footprint.  
    When dynamic=True, the notebook will only load the slice of data you are 
    currently viewing, so each time you move a slider a new slice of data will 
    be loaded.  This prevents the entire cube being loaded for each plot, but 
    can cause complications with some plot types (such as hv.NdLayout, which 
    requires mutliple slices at once).

You can access more in-depth tutorials and guidelines on plotting via the 
Holoviews_ and Geoviews_ websites.

.. _Holoviews: http://holoviews.org/index.html
.. _Geoviews: http://geo.holoviews.org/index.html

