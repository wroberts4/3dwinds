import unittest
# from pywinds import velocity, uv, lat_long, displacements, area, arg_utils
from pywinds.wind_functions import get_displacements
import numpy as np
import subprocess
import sys
import ast


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                 lon_0=None, image_geod=None, earth_geod=None, units=None, center=None, distance=None, speed=None,
                 angle=None, u=None, v=None, old_lat=None, old_long=None, new_lat=None, new_long=None,
                 old_x=None, old_y=None, new_x=None, new_y=None):
        # Input data
        self.i = i
        self.j = j
        self.lat_0 = lat_0
        self.lon_0 = lon_0
        self.image_geod = image_geod
        self.earth_geod = earth_geod
        self.pixel_size = pixel_size
        self.projection = projection
        self.units = units
        self.displacement_data = str(displacement_data)
        self.shape = shape
        self.center = center
        displacements, self.shape = get_displacements(displacement_data, shape=shape, i=i, j=j)
        self.j_displacements, self.i_displacements = displacements
        # Output data
        self.distance = distance
        self.speed = speed
        self.angle = angle
        self.u = u
        self.v = v
        self.old_lat = old_lat
        self.old_long = old_long
        self.new_lat = new_lat
        self.new_long = new_long
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y


class TestWrappers(unittest.TestCase):
    def setUp(self):
        self.test_cases = []
        self.test_cases.append(TestCase('./test_files/test_data_two.flo',
                                        i=1, j=8, pixel_size=10000, lat_0=60, lon_0=0, center=(90, 0),
                                        distance=255333.02691, speed=2101.88674, angle=141.3029, u=1314.1062,
                                        v=-1640.44285, old_lat=89.58692, old_long=-45.03963, new_lat=1.02424,
                                        new_long=55.49562, old_x=-35000.0, old_y=3394327.91718, new_x=8065000.0,
                                        new_y=-4705672.08282))
        displacement_data = np.array(([x for x in range(100)], [x for x in range(100)])) * 10
        self.test_cases.append(TestCase(displacement_data.tolist(), pixel_size=5, lat_0=90, lon_0=20, i=1, j=8,
                                        distance=56.56842, units='km', center=(40, 10), speed=688.49049,
                                        angle=139.13855, u=450.43258, v=-520.7011, old_lat=39.84993, old_long=9.86386,
                                        new_lat=11.64909, new_long=36.80117, old_x=-1051407.88566, old_y=-5881082.99511,
                                        new_x=2998592.11434, new_y=-9931082.99511))

    def test_velocity(self):
        for case in self.test_cases:
            args = list(np.vectorize(str)([case.lat_0, case.lon_0, case.displacement_data]))
            args = list(np.vectorize(str.replace)(args, ' ', ''))
            kwargs_names = ['projection', 'j', 'i', 'shape', 'pixel_size', 'center',
                            'units', 'image_geod', 'earth_geod']
            kwargs_vals = list(np.vectorize(str)([case.projection, case.j, case.i, case.shape, case.pixel_size,
                                                  case.center, case.units, case.image_geod, case.earth_geod]))
            kwargs = []
            for i in range(len(kwargs_names)):
                kwargs.append('--' + kwargs_names[i])
                kwargs.append(kwargs_vals[i].replace(' ', ''))
            output = subprocess.check_output([sys.executable, '../velocity.py'] + args + kwargs).decode('utf-8')
            print(ast.literal_eval('%s' % output))

            kwargs_names = ['projection', 'shape', 'pixel_size', 'center',
                            'units', 'image_geod', 'earth_geod']
            kwargs_vals = list(np.vectorize(str)([case.projection, case.shape, case.pixel_size,
                                                  case.center, case.units, case.image_geod, case.earth_geod]))
            kwargs = []
            for i in range(len(kwargs_names)):
                kwargs.append('--' + kwargs_names[i])
                kwargs.append(kwargs_vals[i].replace(' ', ''))
            output = subprocess.check_output([sys.executable, '../velocity.py'] + args + kwargs).decode('utf-8')
            print(ast.literal_eval('%s' % output))

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
