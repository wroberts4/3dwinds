import unittest
from pyproj import Geod
from pywinds.wind_functions import get_displacements
from pyresample.geometry import AreaDefinition
from pyresample.utils import proj4_str_to_dict
import numpy as np
import subprocess
import sys
import ast


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                 lon_0=None, image_geod=None, earth_geod=None, units=None, center=None, area_extent=None, distance=None,
                 speed=None, angle=None, u=None, v=None, old_lat=None, old_long=None, new_lat=None, new_long=None):
        # Input data
        self.i = i
        self.j = j
        self.lat_0 = str(lat_0).replace(' ', '')
        self.lon_0 = str(lon_0).replace(' ', '')
        self.image_geod = str(image_geod).replace(' ', '')
        self.earth_geod = str(earth_geod).replace(' ', '')
        self.pixel_size = str(pixel_size).replace(' ', '')
        self.projection = str(projection).replace(' ', '')
        self.units = str(units).replace(' ', '')
        self.displacement_data = str(displacement_data).replace(' ', '')
        self.center = str(center).replace(' ', '')
        self.area_extent = str(area_extent)
        displacements, shape = get_displacements(displacement_data, shape=shape, i=i, j=j)
        self.shape = shape
        self.j_displacements, self.i_displacements = displacements
        # Output data
        self.distance = str(distance).replace(' ', '')
        self.speed = speed
        self.angle = angle
        self.u = u
        self.v = v
        self.old_lat = old_lat
        self.old_long = old_long
        self.new_lat = new_lat
        self.new_long = new_long


class TestWrappers(unittest.TestCase):
    def setUp(self):
        self.test_cases = []
        self.test_cases.append(TestCase('./test_files/test_data_three.flo',
                                        i=1, j=4, pixel_size='10:km', lat_0=60, lon_0=0, center=(90, 0),
                                        area_extent=(3454327.9172, 25000.0, 3404327.9172, -25000.0),
                                        distance=255333.02691, speed=3250.56873, angle=144.54325, u=1885.61659,
                                        v=-2647.76266, old_lat=89.81344, old_long=-26.57637, new_lat=-53.72147,
                                        new_long=80.28014))
        displacement_data = np.array(([x for x in range(25)], [x for x in range(25)])) * 10
        self.test_cases.append(TestCase(displacement_data.tolist(), pixel_size=5, lat_0=90, lon_0=20, i=1, j=4,
                                        units='km', center=(40, 10),
                                        area_extent=(-5851082.9951, -1021407.8857, -5876082.9951, -1046407.8857),
                                        distance=56.56842, speed=197.71698,
                                        angle=130.12046, u=151.19247, v=-127.40817, old_lat=39.92071, old_long=9.96938,
                                        new_lat=33.03179, new_long=20.09179))

    def test_velocity(self):
        for case in self.test_cases:
            speed, angle = args_to_data(['../velocity.py', case.lat_0, case.lon_0, case.displacement_data,
                                         '--projection', case.projection, '--pixel_size',
                                         case.pixel_size, '--center', case.center, '--units', case.units,
                                         '--image_geod', case.image_geod, '--earth_geod', case.earth_geod])
            speed_ji, angle_ji = args_to_data(['../velocity.py', case.lat_0, case.lon_0, case.displacement_data,
                                               '--projection', case.projection, '--j', str(case.j), '--i', str(case.i),
                                               '--pixel_size', case.pixel_size, '--center',
                                               case.center, '--units', case.units, '--image_geod', case.image_geod,
                                               '--earth_geod', case.earth_geod])
            self.assertEqual(case.speed, round(speed_ji, 5))
            self.assertEqual(case.angle, round(angle_ji, 5))
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)

    def test_vu(self):
        for case in self.test_cases:
            v, u = args_to_data(['../vu.py', case.lat_0, case.lon_0, case.displacement_data, '--projection',
                                case.projection, '--pixel_size', case.pixel_size, '--center',
                                case.center, '--units', case.units, '--image_geod', case.image_geod, '--earth_geod',
                                case.earth_geod])
            v_ji, u_ji = args_to_data(['../vu.py', case.lat_0, case.lon_0, case.displacement_data, '--projection',
                                       case.projection, '--j', str(case.j), '--i', str(case.i),
                                       '--pixel_size', case.pixel_size, '--center', case.center, '--units', case.units,
                                       '--image_geod', case.image_geod, '--earth_geod', case.earth_geod])
            self.assertEqual(case.v, round(v_ji, 5))
            self.assertEqual(case.u, round(u_ji, 5))
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_lat_long(self):
        for case in self.test_cases:
            old_lat, old_long = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--projection', case.projection,
                                              '--pixel_size', case.pixel_size, '--shape',
                                              str(case.shape).replace(' ', ''), '--center',
                                              case.center, '--units', case.units, '--image_geod', case.image_geod])
            new_lat, new_long = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--displacement_data',
                                              case.displacement_data, '--projection', case.projection,
                                              '--pixel_size', case.pixel_size, '--center', case.center,
                                              '--units', case.units, '--image_geod', case.image_geod])
            old_lat_ji, old_long_ji = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--projection',
                                                    case.projection, '--j', str(case.j), '--i', str(case.i),
                                                    '--pixel_size', case.pixel_size, '--shape',
                                                    str(case.shape).replace(' ', ''), '--center',
                                                    case.center, '--units', case.units, '--image_geod',
                                                    case.image_geod])
            new_lat_ji, new_long_ji = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--displacement_data',
                                                    case.displacement_data, '--projection', case.projection,
                                                    '--j', str(case.j), '--i', str(case.i),
                                                    '--pixel_size', case.pixel_size, '--center', case.center, '--units',
                                                    case.units, '--image_geod', case.image_geod])
            self.assertEqual(case.old_lat, round(old_lat_ji, 5))
            self.assertEqual(case.old_long, round(old_long_ji, 5))
            self.assertEqual(case.new_lat, round(new_lat_ji, 5))
            self.assertEqual(case.new_long, round(new_long_ji, 5))
            self.assertEqual(old_lat[case.j, case.i], old_lat_ji)
            self.assertEqual(old_long[case.j, case.i], old_long_ji)
            self.assertEqual(new_lat[case.j, case.i], new_lat_ji)
            self.assertEqual(new_long[case.j, case.i], new_long_ji)

    def test_displacements(self):
        for case in self.test_cases:
            j_displacements, i_displacements = args_to_data(['../displacements.py', case.displacement_data])
            j_displacements_ji, i_displacements_ji = args_to_data(['../displacements.py', case.displacement_data,
                                                                   '--j', str(case.j), '--i', str(case.i)])
            self.assertEqual(case.j_displacements, round(j_displacements_ji, 5))
            self.assertEqual(case.i_displacements, round(i_displacements_ji, 5))
            self.assertEqual(j_displacements[case.j, case.i], j_displacements_ji)
            self.assertEqual(i_displacements[case.j, case.i], i_displacements_ji)

    def test_area(self):
        for case in self.test_cases:
            test_area = args_to_data(['../area.py', case.lat_0, case.lon_0, '--shape', str(case.shape).replace(' ', ''),
                                      '--center', case.center, '--pixel_size', case.pixel_size, '--units', case.units])
            self.assertTrue('Area extent: ' + case.area_extent in test_area)
            self.assertTrue('Number of columns: {0}'.format(case.shape[1]) in test_area)
            self.assertTrue('Number of rows: {0}'.format(case.shape[0]) in test_area)


def args_to_data(commands):
    output = subprocess.check_output([sys.executable] + commands).decode('utf-8')
    try:
        return np.array(ast.literal_eval('%s' % output))
    except (SyntaxError, ValueError):
        return output


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWrappers))
    return mysuite
