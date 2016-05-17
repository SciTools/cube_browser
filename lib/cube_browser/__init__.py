import matplotlib.pyplot as plt


class Contourf(object):
    def __init__(self, cube, coords, **kwargs):
        self.cube = cube
        self.coords = coords # coords to plot
        self.kwargs = kwargs
        self.axes = self.new_axes()
        self.qcs = None  # QuadContourSet
        # A mapping of 1d-coord name to dimension
        self.coord_dim = self.coord_dims()

    # This constructs the original and updated plots
    def __call__(self, **kwargs):
        index = [slice(None)] * self.cube.ndim
        for name, value in kwargs.items():
            if name in self.coord_dim:
                index[self.coord_dim[name]] = value
        cube = self.cube[tuple(index)]
        plt.sca(self.axes)
        self.qcs = iplt.contourf(cube, coords=self.coords,
                                 axes=self.axes, **self.kwargs)
        return plt.gca()

    def new_axes(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection=cube.coord_system().
                             as_cartopy_projection())
        return ax

    # This makes a mapping dictionary of DIMENSION coordinates
    def coord_dims(self):
        mapping = {}
        for dim in range(self.cube.ndim):
            coords = self.cube.coords(dimensions=(dim,))
            mapping.update([(c.name(), dim) for c in coords])
        return mapping

    # This makes a list of the dim coords not used on the axes,
    # so they are available for use as sliders
    def slider_coords(self):
        available = []
        for dim in range(len(self.cube.dim_coords)):
            if self.cube.dim_coords[dim].name() not in self.coords:
                available.append(self.cube.dim_coords[dim])
        return available

