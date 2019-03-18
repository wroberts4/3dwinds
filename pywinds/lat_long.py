#!/usr/bin/env python
import ntpath
import os
import sys
import numpy as np
from pywinds.wind_functions import lat_long
from pywinds.wrapper_utils import run_script


def output_format(output):
    return np.round(output, 2).tolist()


def main(argv):
    run_script(lat_long, argv, output_format, 'lat_long', is_lat_long=True)


if __name__ == "__main__":
    main(sys.argv)
