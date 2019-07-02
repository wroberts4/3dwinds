#!/usr/bin/env python

import numpy as np

from pywinds.wind_functions import euclidean
from pywinds.wrapper_utils import run_script


def output_format(output, **kwargs):
    return np.round(output, 2).tolist()


if __name__ == "__main__":
    run_script(euclidean, output_format, 'euclidean')
