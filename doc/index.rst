
.. Cube Browser documentation master file

Introduction
____________

Cube Browser is a Python package that makes it quicker and easier to plot and explore your Iris cube data.
The package allows you to view your data in a user-friendly interactive interface that you can customize as you require.

Cube Browser incorporates Ipython widgets (`ipywidgets <http://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Basics.html>`_) for plotting, including the use of sliders to browse through slices of data in your plot.

There are three different ways which you can use Cube Browser:


1. **Using Cube Explorer:**

   You can use our ready-made Cube Explorers to choose and plot your Iris cubes.
   This is an interactive Graphical User Interface, which is available to :download:`download <explorers/explore.ipynb>`


2. **Browsing cubes:**

   If you wish to write a Jupyter notebook to make your bespoke interactive visualisation, you can follow our `guide <browsing_cubes/intro.html>`_ and `reference <ref_docs.html>`_ pages.
   This will give you more flexibility and control over your plots and layout.


3. **Writing your own Cube Explorer:**

   You can construct your own cube plotting explorer in the same way that we have constructed ours.
   We have provided some `developer documentation <write_your_own/intro.html>`_ illustrating how to use widgets to achieve this.
   This could be useful if you have a combination of plots you wish to use frequently and repeatedly.

   Here is the `source code <https://github.com/SciTools/cube_browser/blob/master/lib/cube_browser/explorer.py>`_ for the Cube Explorer we have provided.


Installation
____________

In the following pages you will find downloads of Jupyter notebooks containing Cube Browser operations.
To be able to use these notebooks, you will need to configure your environment correctly.
The most efficient and clean method to do this is to use a Conda environment.

If you have never used Conda before, you will need to follow these `quick installation instructions <http://conda.pydata.org/docs/install/quick.html>`_ to get started.

Once you have done this, open a terminal and type:

``conda install -c scitools -c conda-forge -c scitools/label/dev python=2.7 cube_browser``

This will install Cube Browser with the specific requirements necessary to run it.


Support
_______

Cube Browser is developed through a collaboration between
`Continuum Analytics <https://continuum.io>`_ and the `UK Met Office
<http://www.metoffice.gov.uk>`_.  Cube Browser is open source, available
under a BSD license freely for both commercial and non-commercial use.  Please file
bug reports and feature requests on our
`github site <https://github.com/SciTools/cube_browser/issues>`_.

.. toctree::
   :titlesonly:
   :hidden:
   :maxdepth: 2

   Home <self>
   explorers/intro
   browsing_cubes/intro
   ref_docs
   write_your_own/intro
   help


   Github source <https://github.com/SciTools/cube_browser>
