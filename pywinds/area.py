#!/usr/bin/env python
import ntpath
import os
import sys
from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output):
    return area_to_string(output)


def main(argv):
    run_script(area, argv, output_format, 'area', is_area=True)


if __name__ == "__main__":
    main(sys.argv)
