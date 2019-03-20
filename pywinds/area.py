#!/usr/bin/env python
import sys
import warnings

from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output, kwargs):
    return area_to_string(output)


def main(argv):
    run_script(area, output_format, 'area', is_area=True)


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning, module='pyproj')
    main(sys.argv)
