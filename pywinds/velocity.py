#!/usr/bin/env python
from pywinds.wrapper_utils import run_script
from pywinds.wind_functions import velocity
import sys
import numpy as np
import os
import ntpath


def output_format(output):
    return np.round(output, 2).tolist()


def main(argv):
    run_script(velocity, argv, output_format, 'velocity')


if __name__ == "__main__":
    main(sys.argv)
