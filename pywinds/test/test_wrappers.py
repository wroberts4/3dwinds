import unittest
from pywinds.wind_functions import displacements, area
import numpy as np
import subprocess
import sys
import ast


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                 lon_0=None, image_geod=None, earth_geod=None, units=None, center=None, area_extent=None,
                 speed=None, angle=None, u=None, v=None, old_lat=None, old_long=None, new_lat=None, new_long=None,
                 delta_time=100):
        # Input data
        self.i = i
        self.j = j
        self.lat_0 = str(lat_0).replace(' ', '')
        self.lon_0 = str(lon_0).replace(' ', '')
        self.delta_time = str(delta_time)
        self.image_geod = str(image_geod).replace(' ', '')
        self.earth_geod = str(earth_geod).replace(' ', '')
        self.pixel_size = str(pixel_size).replace(' ', '')
        self.projection = str(projection).replace(' ', '')
        self.units = str(units).replace(' ', '')
        self.displacement_data = str(displacement_data).replace(' ', '')
        self.center = str(center).replace(' ', '')
        self.area_extent = area_extent
        self.j_displacements, self.i_displacements = displacements(lat_0, lon_0, displacement_data=displacement_data,
                                                                   shape=shape, i=i, j=j, no_save=True)
        area_data = area(lat_0, lon_0, displacement_data=displacement_data, shape=shape, center=center,
                         pixel_size=float(str(pixel_size).split(':')[0]), no_save=True)
        self.shape = area_data['shape']
        # Output data
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
                                        i=1, j=4, pixel_size=10000, lat_0=60, lon_0=0, center=(90.0, 0.0),
                                        area_extent=(89.71, 135.03, 89.71, -45.03),
                                        speed=2820.83, angle=42.94, u=1921.49, v=2065.18, old_lat=-21.9,
                                        old_long=-151.31, new_lat=89.81, new_long=-26.58))
        displacement_data = np.array(([x for x in range(25)], [x for x in range(25)])) * 10
        self.test_cases.append(TestCase(displacement_data.tolist(), pixel_size=5000, lat_0=90, lon_0=20, i=1, j=4,
                                        center=(40.0, 10.0),
                                        area_extent=(40.11, 10.1, 39.89, 9.9),
                                        speed=208.14, angle=118.39, u=183.1, v=-98.98, old_lat=45.27, old_long=-3.42,
                                        new_lat=39.92, new_long=9.97))

    def test_wind_info(self):
        for case in self.test_cases:
            lat_ji, long_ji, speed_ji, angle_ji, v_ji, u_ji =\
                args_to_data(['../wind_info.py', case.lat_0, case.lon_0, case.delta_time,
                              '--displacement_data', case.displacement_data, '--projection', case.projection,
                              '--j', str(case.j), '--i', str(case.i), '--pixel_size', case.pixel_size, '--center',
                              case.center, '--units', case.units, '--image_geod', case.image_geod, '--earth_geod',
                              case.earth_geod, '--no_save']).transpose()
            lat, long, speed, angle, v, u =\
                args_to_data(['../wind_info.py', case.lat_0, case.lon_0, case.delta_time,
                              '--displacement_data', case.displacement_data, '--projection', case.projection,
                              '--pixel_size', case.pixel_size, '--center', case.center, '--units', case.units,
                              '--image_geod', case.image_geod, '--earth_geod',
                              case.earth_geod, '--no_save']).transpose().reshape([6] + list(case.shape))
            self.assertEqual(case.new_lat, lat_ji)
            self.assertEqual(case.new_long, long_ji)
            self.assertEqual(lat[case.j, case.i], lat_ji)
            self.assertEqual(long[case.j, case.i], long_ji)
            self.assertEqual(case.speed, speed_ji)
            self.assertEqual(case.angle, angle_ji)
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)
            self.assertEqual(case.v, v_ji)
            self.assertEqual(case.u, u_ji)
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_velocity(self):
        for case in self.test_cases:
            speed_ji, angle_ji = args_to_data(['../velocity.py', case.lat_0, case.lon_0,
                                               case.delta_time, '--displacement_data', case.displacement_data,
                                               '--projection', case.projection, '--j', str(case.j), '--i',
                                               str(case.i), '--pixel_size', case.pixel_size, '--center',
                                               case.center, '--units', case.units, '--image_geod',
                                               case.image_geod, '--earth_geod', case.earth_geod, '--no_save'])
            speed, angle = args_to_data(['../velocity.py', case.lat_0, case.lon_0,
                                         case.delta_time, '--displacement_data', case.displacement_data,
                                         '--projection', case.projection, '--pixel_size', case.pixel_size,
                                         '--center', case.center, '--units', case.units,
                                         '--image_geod', case.image_geod, '--earth_geod', case.earth_geod, '--no_save'])
            self.assertEqual(case.speed, speed_ji)
            self.assertEqual(case.angle, angle_ji)
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)

    def test_vu(self):
        for case in self.test_cases:
            v_ji, u_ji = args_to_data(['../vu.py', case.lat_0, case.lon_0, case.delta_time,
                                       '--displacement_data', case.displacement_data, '--projection', case.projection,
                                       '--j', str(case.j), '--i', str(case.i), '--pixel_size', case.pixel_size,
                                       '--center', case.center, '--units', case.units, '--image_geod',
                                       case.image_geod, '--earth_geod',
                                       case.earth_geod, '--no_save'])
            v, u = args_to_data(['../vu.py', case.lat_0, case.lon_0, case.delta_time,
                                 '--displacement_data', case.displacement_data, '--projection', case.projection,
                                 '--pixel_size', case.pixel_size, '--center', case.center, '--units', case.units,
                                 '--image_geod', case.image_geod, '--earth_geod', case.earth_geod, '--no_save'])
            self.assertEqual(case.v, v_ji)
            self.assertEqual(case.u, u_ji)
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_lat_long(self):
        for case in self.test_cases:
            old_lat_ji, old_long_ji = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--displacement_data', case.displacement_data,
                                                    '--projection', case.projection, '--j', str(case.j), '--i',
                                                    str(case.i), '--pixel_size', case.pixel_size, '--center', case.center,
                                                    '--units', case.units, '--image_geod', case.image_geod, '--no_save'])
            new_lat_ji, new_long_ji = args_to_data(['../lat_long.py', case.lat_0, case.lon_0,
                                                    '--projection', case.projection, '--shape', str(case.shape).replace(' ', ''),
                                                    '--j', str(case.j), '--i', str(case.i),
                                                    '--pixel_size', case.pixel_size, '--center', case.center,
                                                    '--units', case.units, '--image_geod', case.image_geod, '--no_save'])
            old_lat, old_long = args_to_data(['../lat_long.py', case.lat_0, case.lon_0, '--displacement_data', case.displacement_data,
                                              '--projection', case.projection, '--pixel_size', case.pixel_size,
                                              '--center',
                                              case.center, '--units', case.units, '--image_geod', case.image_geod, '--no_save'])
            new_lat, new_long = args_to_data(['../lat_long.py', case.lat_0, case.lon_0,
                                              '--projection', case.projection, '--shape', str(case.shape).replace(' ', ''),
                                              '--pixel_size', case.pixel_size, '--center',
                                              case.center, '--units', case.units, '--image_geod', case.image_geod, '--no_save'])
            self.assertEqual(case.old_lat, old_lat_ji)
            self.assertEqual(case.old_long, old_long_ji)
            self.assertEqual(case.new_lat, new_lat_ji)
            self.assertEqual(case.new_long, new_long_ji)
            self.assertEqual(old_lat[case.j, case.i], old_lat_ji)
            self.assertEqual(old_long[case.j, case.i], old_long_ji)
            self.assertEqual(new_lat[case.j, case.i], new_lat_ji)
            self.assertEqual(new_long[case.j, case.i], new_long_ji)

    def test_displacements(self):
        for case in self.test_cases:
            displacement = args_to_data(['../displacements.py',
                                         '--displacement_data', case.displacement_data, '--no_save'])
            displacements_ji = args_to_data(['../displacements.py', '--displacement_data',
                                             case.displacement_data, '--j', str(case.j), '--i', str(case.i), '--no_save'])
            j_displacements, i_displacements = displacement
            j_displacements_ji, i_displacements_ji = displacements_ji
            self.assertEqual(case.j_displacements, j_displacements_ji)
            self.assertEqual(case.i_displacements, i_displacements_ji)
            self.assertEqual(j_displacements[case.j][case.i], j_displacements_ji)
            self.assertEqual(i_displacements[case.j][case.i], i_displacements_ji)

    def test_area(self):
        for case in self.test_cases:
            area_data = args_to_data(['../area.py', case.lat_0, case.lon_0, '--shape',
                                      str(case.shape).replace(' ', ''), '--center', case.center, '--pixel_size',
                                      case.pixel_size, '--units', case.units, '--no_save'])
            self.assertTrue('center: ' + case.center.replace(',', ', ') in area_data)
            self.assertTrue('shape: ' + str(case.shape) in area_data)
            self.assertTrue('lat_0: ' + case.lat_0.replace(',', ', ') in area_data)
            self.assertTrue('lon_0: ' + case.lon_0.replace(',', ', ') in area_data)
            self.assertTrue('projection: ' + case.projection.replace(',', ', ') in area_data)
            self.assertTrue(str(case.area_extent[0]) in area_data)
            self.assertTrue(str(case.area_extent[1]) in area_data)
            self.assertTrue(str(case.area_extent[2]) in area_data)
            self.assertTrue(str(case.area_extent[3]) in area_data)
            self.assertTrue(str(case.shape) in area_data)


def args_to_data(commands):
    try:
        output = subprocess.check_output([sys.executable] + commands).decode('utf-8')
    except subprocess.CalledProcessError as err:
        raise ValueError(err.output.decode('utf-8'))
    try:
        return np.array(ast.literal_eval('%s' % output))
    except (SyntaxError, ValueError):
        return output


def suite():
    """The test suite for test_wrappers."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWrappers))
    return mysuite
