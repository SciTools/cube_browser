
.. Cube Browser documentation master file

Introduction
____________

Cube Browser is a Python package which can make it quicker and easier to plot and explore your Iris cubes.  The package 
It makes use of IPython widgets for several aspects of plotting, including the use of sliders to browse through slices of data in your plot.

There are three different ways which you can use Cube Browser:


1. **Explorers:**

   If you have several cubes which you would like to plot and explore in different ways, have a look at our `Explorers <explorers/intro.html>`_, which offer you a ready-made cube-to-plot selection process.
   These are available to download or to run straight from your internet browser.


2. **Browsing cubes:**

   You may want to use the Cube Browser API to write a Jupyter notebook to make a simple or complicated interactive visualisation.
   This will give you more flexibility in the way you would like to plot your data and how you would like it laid out and customized.
   To do this, you can use the `guide <browsing_cubes/info.html>`_ and `reference <ref_docs.html>`_ pages.


3. **Writing your own cube browser:**

   In the same way that we have constructed our Explorers, you can make use of Ipywidgets to string together your own cube plotting process.
   We have provided some `developer documentation <write_your_own/intro.html>`_ illustrating how to use IPywidgets to build a work flow as general or as specialized as you need.
   This could be useful if you have a specific combination of plots which you use frequently and repeatedly.

   `Click here <../lib/cube_browser/explorer.py>`_ to see the source code for the Explorer we have provided.

Installation
____________

Conda is great

------------

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


   Github source <https://github.com/SciTools/cube_browser>
