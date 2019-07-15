#!/usr/bin/env python
import ast
import os
import subprocess
import unittest

import numpy as np

from pywinds.wind_functions import area, displacements


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_ts=None,
                 lat_0=None, long_0=None, projection_ellipsoid='WGS84', earth_ellipsoid='WGS84', center=None,
                 area_extent=None, speed=None, angle=None, u=None, v=None, old_lat=None, old_long=None, new_lat=None,
                 new_long=None,
                 delta_time=100):
        # Input data
        self.i = i
        self.j = j
        self.lat_ts = lat_ts
        self.lat_0 = lat_0
        self.long_0 = long_0
        self.delta_time = delta_time
        self.projection_ellipsoid = projection_ellipsoid
        self.earth_ellipsoid = earth_ellipsoid
        self.pixel_size = pixel_size
        self.projection = projection
        self.center = center
        self.area_extent = area_extent
        j_displacements, i_displacements = displacements(lat_ts, lat_0, long_0, displacement_data=displacement_data,
                                                         shape=shape, i=i, j=j)
        self.j_displacements = j_displacements
        self.i_displacements = i_displacements
        area_data = area(lat_ts, lat_0, long_0, displacement_data=displacement_data, shape=shape, center=center,
                         pixel_size=pixel_size)
        if isinstance(displacement_data, list):
            self.displacement_data = str(displacement_data).replace(' ', '')
        else:
            self.displacement_data = displacement_data
        self.shape = list(area_data['shape'])
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
        self.root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'make_env', 'run_scripts')
        self.test_cases = []
        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),'test_files', 'test_data_three.flo')
        self.test_cases.append(
            TestCase(file_name, i=1, j=4, pixel_size=10000, lat_ts=60, lat_0=90, long_0=0, center=[90.0, 0.0],
                     area_extent=[89.66, -45.0, 89.66, 135.0], speed=2610, angle=14.74, u=664.03, v=2524.12,
                     old_lat=-46.64, old_long=-134.96, new_lat=89.79, new_long=-26.57))
        displacement_data = np.array(([x for x in range(25)], [x for x in range(25)])) * 10
        self.test_cases.append(
            TestCase(displacement_data.tolist(), pixel_size=5000, lat_ts=-60, lat_0=-90, long_0=20, i=1, j=4,
                     center=[-40.0, 0.0], area_extent=[-40.06, -0.17, -39.94, 0.17], speed=208.34, angle=157.77,
                     u=78.81, v=-192.86, old_lat=-29.63, old_long=-5.27, new_lat=-40.06, new_long=-0.08))

    def test_wind_info(self):
        for case in self.test_cases:
            lat_ji, long_ji, speed_ji, angle_ji, v_ji, u_ji = args_to_data(
                [os.path.join(self.root, 'wind_info.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data', case.displacement_data, '--projection', case.projection, '-j', str(case.j),
                 '-i', str(case.i), '--pixel-size', case.pixel_size, 'm', '--center', *case.center, 'deg',
                 '--projection-ellipsoid', case.projection_ellipsoid, '--earth-ellipsoid', case.earth_ellipsoid,
                 '-p']).transpose()
            lat, long, speed, angle, v, u = args_to_data(
                [os.path.join(self.root,'wind_info.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data',  case.displacement_data, '--projection', case.projection, '--pixel-size',
                 case.pixel_size, 'm', '--center', *case.center, 'deg', '--projection-ellipsoid',
                 case.projection_ellipsoid, '--earth-ellipsoid',
                 case.earth_ellipsoid, '-p']).transpose().reshape([6] + list(case.shape))
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
            speed_ji, angle_ji = args_to_data(
                [os.path.join(self.root, 'velocity.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data', case.displacement_data, '--projection', case.projection, '-j', str(case.j),
                 '-i', str(case.i), '--pixel-size', case.pixel_size, 'm', '--center', *case.center, 'deg',
                 '--projection-ellipsoid', case.projection_ellipsoid, '--earth-ellipsoid', case.earth_ellipsoid])
            speed, angle = args_to_data(
                [os.path.join(self.root, 'velocity.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data', case.displacement_data, '--projection', case.projection, '--pixel-size',
                 case.pixel_size, 'm', '--center', *case.center, 'deg', '--projection-ellipsoid',
                 case.projection_ellipsoid, '--earth-ellipsoid', case.earth_ellipsoid])
            self.assertEqual(case.speed, speed_ji)
            self.assertEqual(case.angle, angle_ji)
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)

    def test_vu(self):
        for case in self.test_cases:
            v_ji, u_ji = args_to_data(
                [os.path.join(self.root, 'vu.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data', case.displacement_data, '--projection', case.projection, '-j', str(case.j),
                 '-i', str(case.i), '--pixel-size', case.pixel_size, 'm', '--center', *case.center, 'deg',
                 '--projection-ellipsoid', case.projection_ellipsoid, '--earth-ellipsoid', case.earth_ellipsoid])
            v, u = args_to_data(
                [os.path.join(self.root, 'vu.sh'), case.lat_ts, case.lat_0, case.long_0, case.delta_time,
                 '--displacement-data', case.displacement_data, '--projection', case.projection, '--pixel-size',
                 case.pixel_size, 'm', '--center', *case.center, 'deg', '--projection-ellipsoid',
                 case.projection_ellipsoid, '--earth-ellipsoid', case.earth_ellipsoid])
            self.assertEqual(case.v, v_ji)
            self.assertEqual(case.u, u_ji)
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_lat_long(self):
        for case in self.test_cases:
            old_lat_ji, old_long_ji = args_to_data(
                [os.path.join(self.root, 'lat_long.sh'), case.lat_ts, case.lat_0, case.long_0, '--displacement-data',
                 case.displacement_data, '--projection', case.projection, '-j', str(case.j), '-i', str(case.i),
                 '--pixel-size', case.pixel_size, 'm', '--center', *case.center, 'deg', '--projection-ellipsoid',
                 case.projection_ellipsoid])
            new_lat_ji, new_long_ji = args_to_data(
                [os.path.join(self.root, 'lat_long.sh'), case.lat_ts, case.lat_0, case.long_0, '--projection',
                 case.projection, '--shape', *case.shape, '-j', str(case.j), '-i', str(case.i), '--pixel-size',
                 case.pixel_size, 'm', '--center', *case.center, 'deg', '--projection-ellipsoid',
                 case.projection_ellipsoid])
            old_lat, old_long = args_to_data(
                [os.path.join(self.root, 'lat_long.sh'), case.lat_ts, case.lat_0, case.long_0, '--displacement-data',
                 case.displacement_data, '--projection', case.projection, '--pixel-size', case.pixel_size, 'm',
                 '--center', *case.center, 'deg', '--projection-ellipsoid', case.projection_ellipsoid])
            new_lat, new_long = args_to_data(
                [os.path.join(self.root, 'lat_long.sh'), case.lat_ts, case.lat_0, case.long_0, '--projection',
                 case.projection, '--shape', *case.shape, '--pixel-size', case.pixel_size, 'm', '--center',
                 *case.center, 'deg', '--projection-ellipsoid', case.projection_ellipsoid])
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
            displacement = args_to_data([os.path.join(self.root, 'displacements.sh'),
                                         '--displacement-data', case.displacement_data])
            displacements_ji = args_to_data(
                [os.path.join(self.root, 'displacements.sh'), '--displacement-data', case.displacement_data, '-j',
                 str(case.j), '-i', str(case.i)])
            j_displacements, i_displacements = displacement
            j_displacements_ji, i_displacements_ji = displacements_ji
            self.assertEqual(case.j_displacements, j_displacements_ji)
            self.assertEqual(case.i_displacements, i_displacements_ji)
            self.assertEqual(j_displacements[case.j][case.i], j_displacements_ji)
            self.assertEqual(i_displacements[case.j][case.i], i_displacements_ji)

    def test_area(self):
        for case in self.test_cases:
            area_data = args_to_data(
                [os.path.join(self.root, 'area.sh'), case.lat_ts, case.lat_0, case.long_0, '--center', *case.center,
                 'deg', '--pixel-size', case.pixel_size, '--displacement-data', case.displacement_data])
            self.assertTrue('center: ' + str(case.center) in area_data)
            self.assertTrue('shape: ' + str(case.shape) in area_data)
            self.assertTrue('lat-0: ' + str(case.lat_0) in area_data)
            self.assertTrue('long-0: ' + str(case.long_0) in area_data)
            self.assertTrue('projection: ' + case.projection in area_data)
            self.assertTrue(str(case.area_extent) in area_data)
            self.assertTrue(str(case.shape) in area_data)


def args_to_data(commands):
    try:
        output = subprocess.check_output(list(map(str, commands))).decode('utf-8')
    except subprocess.CalledProcessError as err:
        raise ValueError(err.output.decode('utf-8'))
    try:
        return np.array(ast.literal_eval('%s' % output), dtype=float)
    except (SyntaxError, ValueError):
        return output


def suite():
    """The test suite for test_wrappers."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWrappers))
    return mysuite


if __name__ == "__main__":
    unittest.main()
