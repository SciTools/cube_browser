# Hi reader! This Dockerfile is purely to build the mybinder image suitable to run the examples.
# Installing cube_browser itself couldn't be simpler - just `conda install cube_browser -c scitools/label/dev`.

FROM andrewosh/binder-base

MAINTAINER Phil Elson <pelson.pub@gmail.com>

USER main

# Install cube_browser into the image.
# Also prepare the matplotlib font cache to speed initial setup up.
RUN conda install -c conda-forge -c scitools -c scitools/label/dev cube_browser && \
    python -c "import matplotlib.pyplot"
     
