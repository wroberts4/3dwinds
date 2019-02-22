#!/Users/wroberts/anaconda3/envs/newpyre/bin/python3.6
from wrapper_utils import run_script
from wind_functions import area
import sys
import numpy as np


def output_format(output, kwargs):
    proj_dict = dict(output.proj_dict)
    if output.height is None or output.width is None:
        shape = None
    else:
        shape = (output.height, output.width)
    return 'projection data: {0}\narea_extent: {1}\nshape: {2}'.format(proj_dict,
                                                                       np.round(output.area_extent, 2).tolist(),
                                                                       shape)


def main(argv):
    run_script(area, argv, output_format, 'area', is_area=True)


if __name__ == "__main__":
    main(sys.argv)
