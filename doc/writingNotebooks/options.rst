Formatting Options
==================

You should now be able to successfully plot an Iris cube with your chosen axes 
and scrolling dimensions, but you may want to format either an individual plot 
or all your plots to your liking.  Here are some ways that you can do this.

Layout
------

If you have two or more cubes that you would like to plot side-by-side, you can 
achieve this in a single line by using the + operator like this::

    plot1 + plot2
    
Additionally, you can choose to overlay plots using the * operator like this::

    plot1 * plot2
    
Examples of using these layout options can be viewed in the Examples section.

Magics
------

When altering the plot formatting options in a notebook, a set of options called 
magics are supplied.  These are simply the formatting options supplied by your 
normal plotting module (i.e. matplotlib).  Further information about how you 
can find the options that are available to you are described in the next page 
(`Help Options`)

.. _`Help Options`: help

Line magics apply to an entire notebook and are denoted by the % symbol, and 
cell magics apply to a single cell and are denoted by %%.  Cell magics will 
override line magics in the selected cell.

To apply the formatting that you prefer, use this syntax at the top of your 
cell::

    %%opts Element [option=keyword]

Here is a notebook example of using line magic to define your formatting 
options for an entire notebook:

.. notebook:: holocube options_example.ipynb 

    
.. NOTE::
    Currently if you are using multiple images in a Layout or Overlay 
    combination, formatting options must be set directly on the outermost plot 
    rather than using line or cell magic.



