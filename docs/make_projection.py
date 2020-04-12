# Copyright Cartopy Contributors
#
# This file is part of Cartopy and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

from __future__ import (absolute_import, division, print_function)
import os
import inspect
import textwrap
import numpy as np
import cartopy.crs as ccrs

#: A dictionary to allow examples to use non-default parameters to the CRS
#: constructor.
SPECIFIC_PROJECTION_KWARGS = {
    ccrs.RotatedPole: {'pole_longitude': 177.5, 'pole_latitude': 37.5},
    ccrs.AzimuthalEquidistant: {'central_latitude': 90},
    ccrs.NearsidePerspective: {
        'central_longitude': -3.53, 'central_latitude': 50.72,
        'satellite_height': 10.0e6},
    ccrs.OSGB: {'approx': False},
    ccrs.OSNI: {'approx': False},
    ccrs.TransverseMercator: {'approx': False},
}


def plate_carree_plot():
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    nplots = 2

    fig = plt.figure(figsize=(6, 6))

    for i in range(0, nplots):
        central_longitude = 0 if i == 0 else 180
        ax = fig.add_subplot(
            nplots, 1, i+1,
            projection=ccrs.PlateCarree(central_longitude=central_longitude))
        ax.coastlines(resolution='110m')
        ax.gridlines()


def utm_plot():
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    nplots = 60

    fig = plt.figure(figsize=(10, 3))

    for i in range(0, nplots):
        ax = fig.add_subplot(1, nplots, i+1,
                             projection=ccrs.UTM(zone=i+1,
                                                 southern_hemisphere=True))
        ax.coastlines(resolution='110m')
        ax.gridlines()


MULTI_PLOT_CASES = {
    ccrs.PlateCarree: plate_carree_plot,
    ccrs.UTM: utm_plot,
}


COASTLINE_RESOLUTION = {ccrs.OSNI: '10m',
                        ccrs.OSGB: '50m',
                        ccrs.EuroPP: '50m'}


PRJ_SORT_ORDER = {'PlateCarree': 1,
                  'Mercator': 2, 'Mollweide': 2, 'Robinson': 2,
                  'TransverseMercator': 2, 'LambertCylindrical': 2,
                  'LambertConformal': 2, 'EquidistantConic': 2,
                  'Stereographic': 2, 'Miller': 2,
                  'Orthographic': 2, 'UTM': 2, 'AlbersEqualArea': 2,
                  'AzimuthalEquidistant': 2, 'Sinusoidal': 2,
                  'InterruptedGoodeHomolosine': 3, 'RotatedPole': 3,
                  'OSGB': 4, 'EuroPP': 5,
                  'Geostationary': 6, 'NearsidePerspective': 7,
                  'EckertI': 8.1, 'EckertII': 8.2, 'EckertIII': 8.3,
                  'EckertIV': 8.4, 'EckertV': 8.5, 'EckertVI': 8.6}


def find_projections():
    for obj_name, o in vars(ccrs).copy().items():
        if isinstance(o, type) and issubclass(o, ccrs.Projection) and \
           not obj_name.startswith('_') and obj_name not in ['Projection']:

            yield o


def create_instance(prj_cls, instance_args):
    name = prj_cls.__name__

    # Format instance arguments into strings
    instance_params = ',\n                            '.join(
        '{}={}'.format(k, v)
        for k, v in sorted(instance_args.items()))

    if instance_params:
        instance_params = '\n                            ' \
                          + instance_params

    instance_creation_code = '{}({})'.format(name, instance_params)

    prj_inst = prj(**instance_args)

    return prj_inst, instance_creation_code


if __name__ == '__main__':
    fname = os.path.join(os.path.dirname(__file__), 'source',
                         'crs', 'projections.rst')
    table = open(fname, 'w')

    notes = """
        .. (comment): DO NOT EDIT this file.
        .. It is auto-generated by running : cartopy/docs/make_projection.py
        .. Please adjust by making changes there.
        .. It is included in the repository only to aid detection of changes.

        .. _cartopy_projections:

        Cartopy projection list
        =======================

        """
    table.write(textwrap.dedent(notes))

    def prj_class_sorter(cls):
        return (PRJ_SORT_ORDER.get(cls.__name__, 100),
                cls.__name__)

    for prj in sorted(find_projections(), key=prj_class_sorter):
        name = prj.__name__

        table.write(name + '\n')
        table.write('-' * len(name) + '\n\n')

        table.write('.. autoclass:: cartopy.crs.%s\n' % name)

        if prj not in MULTI_PLOT_CASES:
            # Get instance arguments and number of plots
            instance_args = SPECIFIC_PROJECTION_KWARGS.get(prj, {})

            prj_inst, instance_repr = create_instance(prj, instance_args)

            aspect = (np.diff(prj_inst.x_limits) /
                      np.diff(prj_inst.y_limits))[0]

            width = 3 * aspect
            width = '{:.4f}'.format(width).rstrip('0').rstrip('.')

            # Generate plotting code
            code = textwrap.dedent("""
            .. plot::

                import matplotlib.pyplot as plt
                import cartopy.crs as ccrs

                plt.figure(figsize=({width}, 3))
                ax = plt.axes(projection=ccrs.{proj_constructor})
                ax.coastlines(resolution={coastline_resolution!r})
                ax.gridlines()


            """).format(width=width,
                        proj_constructor=instance_repr,
                        coastline_resolution=COASTLINE_RESOLUTION.get(prj,
                                                                      '110m'))

        else:
            func = MULTI_PLOT_CASES[prj]

            lines = inspect.getsourcelines(func)
            func_code = "".join(lines[0][1:])

            code = textwrap.dedent("""
            .. plot::

            {func_code}

            """).format(func_code=func_code)

        table.write(code)
