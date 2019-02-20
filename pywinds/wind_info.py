#!C:\Users\William\Anaconda3\envs\pyre\python
from wrapper_utils import run_script
from wind_functions import wind_info
import sys
import numpy as np


def main(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') is not True:
            return np.round(output, 2).tolist()
        return ''

    run_script(wind_info, argv, output_format, 'wind_info')


if __name__ == "__main__":
    main(sys.argv)