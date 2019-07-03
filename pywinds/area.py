#!/usr/bin/env python

from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output, **kwargs):
    return area_to_string(output, round_nums=2)


if __name__ == "__main__":
    run_script(area, output_format, 'area')
