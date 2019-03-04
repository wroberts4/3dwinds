#!/usr/bin/env python3
from pywinds.wrapper_utils import run_script
from pywinds.wind_functions import area
import sys
import numpy as np
import os
import ntpath


def _round(val, precision):
    if val is None:
        return None
    if np.shape(val) == ():
        return round(val, precision)
    return tuple(np.round(val, precision).tolist())


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        precision = 2
        projection = output['projection']
        lat_0 = _round(output['lat_0'], precision)
        lon_0 = _round(output['lon_0'], precision)
        equatorial_radius = _round(output['equatorial radius'], precision)
        eccentricity = _round(output['eccentricity'], 6)
        shape = output['shape']
        area_extent = _round(output['area_extent'], precision)
        pixel_size = _round(output['pixel_size'], precision)
        center = _round(output['center'], precision)
        return ('projection: {0}\nlat_0: {1}\nlon_0: {2}\nequatorial radius: {3}\neccentricity: {4}\n'
            'area_extent: {5}\nshape: {6}\npixel_size: {7}\ncenter: {8}').format(projection, lat_0, lon_0,
                                                                                 equatorial_radius, eccentricity,
                                                                                 area_extent, shape, pixel_size, center)
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    return 'Saving area to:\n{0}\n{1}'.format(os.path.join(save_directory, 'area.txt'),
                                                   os.path.join(save_directory, 'wind_info.hdf5'))


def main(argv):
    run_script(area, argv, output_format, 'area', is_area=True)


if __name__ == "__main__":
    main(sys.argv)
