#!/usr/bin/env python
import sys
import warnings

import numpy as np

from pywinds.wind_functions import lat_long
from pywinds.wrapper_utils import run_script


def output_format(output, kwargs):
    return np.round(output, 2).tolist()


if __name__ == "__main__":
    run_script(lat_long, output_format, 'lat_long')
