import unittest
import numpy as np
from pywinds.wind_functions import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area,\
    _extrapolate_j_i, _pixel_to_pos


class TestCase:
    def __init__(self):
        return


class TestWrappers(unittest.TestCase):
    def setUp(self):
        return

    def test_velocity(self):
        return

    def test_uv(self):
        return

    def test_lat_long(self):
        return

    def test_displacements(self):
        return

    def test_area(self):
        return


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWrappers))
    return mysuite
