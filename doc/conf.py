# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.getcwd())

# # General information about the project.
project = u'CubeBrowser'
copyright = u'2016, CubeBrowser developers'
authors = u'CubeBrowser developers'
module = 'cube_browser'
description = 'Browser based exploration of Iris cubes'


# # The short X.Y version.
version = u'v0.1'
# The full version, including alpha/beta/rc tags.
release = u'v0.1'

# Override default theme
import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_logo = ''
html_favicon = ''

# -------------------------------------------------------------------------
# -- The remaining items are less likely to need changing for a new project

# The master toctree document.
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'test_data', 'reference_data', 'nbpublisher',
                    'builder']

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = module+'doc'


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  ('index', module+'.tex', project+u' Documentation', authors, 'manual'),
]

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', module, project+u' Documentation', [authors], 1)
]
# If true, show URL addresses after external links.
#man_show_urls = False


# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', project, project+u' Documentation', authors, project, description,
   'Miscellaneous'),
]


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://ipython.org/ipython-doc/2/': None}

js_includes = ['js/theme.js', 'bootstrap.js', 'custom.js', 'require.js']

