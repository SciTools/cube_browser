# Hi reader! This Dockerfile is purely to build the mybinder image suitable to run the examples.
# Installing cube_browser itself couldn't be simpler - just `conda install cube_browser -c scitools/label/dev`.

FROM andrewosh/binder-base

MAINTAINER Phil Elson <pelson.pub@gmail.com>

USER main

# Install ipywidgets and cube_browser and sample data into the image.
# Also prepare the matplotlib font cache to speed initial setup up.
RUN conda install -c conda-forge -c scitools -c scitools/label/dev cube_browser ipywidgets && \
    git clone https://github.com/SciTools/iris-sample-data.git && \
    cp -rf iris-sample-data/iris_sample_data/sample_data /home/main/anaconda2/lib/python2.7/site-packages/iris/ && \
    rm -rf iris-sample-data && \
    python -c "import matplotlib.pyplot"
     
