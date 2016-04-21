Help Options
============

When you are composing your notebook,, there are many ways that you 
can alter the nature and appearance of your plot at various stages.  To make 
this process easy and accessible,there are several ways of accessing help 
documentation when you are writing your notebook.  These are described below.

Elements
--------

You can request information about the options for your Element.  For example::

    hv.help(hc.Image)

A list of all the available options from the matplotlib backend will appear with 
defaults and descriptions.  If you would like help about a specific argument, 
you can add this argument inside the parentheses to narrow down the returned 
information.

Magic
-----

Sometimes you can hit problems with the syntax of Magic.  In this case you can 
use this to get a doc string::

    %%opts?
    
If you are applying an option which requires a specific keyword argument, such 
as cmap, and you enter a selection which is either incorrect or not available, a 
list of available options will appear below the cell.

Alternatively, you can use tab completion inside or outside parentheses to see 
your options for using Magic. 



