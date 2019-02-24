#!/Users/wroberts/anaconda3/envs/newpyre/bin/python3.6
from wrapper_utils import run_script
from wind_functions import area
import sys
import numpy as np


def output_format(output, kwargs):
    proj_dict = dict(output.proj_dict)
    area_extent = output.area_extent
    if output.height is None or output.width is None:
        shape = None
    else:
        shape = (output.height, output.width)
    try:
        pixel_size = (output.pixel_size_y, output.pixel_size_x)
    except AttributeError:
        pixel_size = output.resolution
    if output.area_extent is not None:
        center = ((area_extent[0] + area_extent[2]) / 2, (area_extent[1] + area_extent[3]) / 2)
    else:
        center = None
    return 'projection data: {0}\narea_extent: {1}\nshape: {2}\npixel_size: {3}\ncenter: {4}'.format(proj_dict,
                                                                                                     area_extent,
                                                                       shape, pixel_size, center)


def main(argv):
    run_script(area, argv, output_format, 'area', is_area=True)


if __name__ == "__main__":
    main(sys.argv)
