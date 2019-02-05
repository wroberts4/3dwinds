from pyproj import Geod
import unittest
import numpy as np


class TestCase:
    def __init__(self, projection, displacement_data, i_old=None, j_old=None, shape=None, pixel_size=None, lat_0=None,
                 lon_0=None, image_geod=Geod(ellps='WGS84'), earth_geod=Geod(ellps='WGS84'), units='m', center=(90, 0),
                 distance=None, speed=None, angle=None, u=None, v=None, old_lat_long=None, new_lat_long=None,
                 old_pos=None, new_pos=None):
        from main import get_displacements
        # Input data
        self.i_old = i_old
        self.j_old = j_old
        self.lat_0 = lat_0
        self.lon_0 = lon_0
        self.image_geod = image_geod
        self.earth_geod = earth_geod
        self.pixel_size = pixel_size
        self.projection = projection
        self.units = units
        self.displacement_data = displacement_data
        self.shape = shape
        self.center = center
        i_displacements, j_displacements = get_displacements(displacement_data, shape=shape)
        if i_old is None:
            self.i_new = [[x for x in range(shape[1])] for y in range(shape[0])] + i_displacements
            self.j_new = [[y for x in range(shape[1])] for y in range(shape[0])] + j_displacements
        else:
            self.i_new = i_old + i_displacements[i_old][j_old]
            self.j_new = j_old + j_displacements[i_old][j_old]
        # Output data
        self.distance = distance
        self.speed = speed
        self.angle = angle
        self.u = u
        self.v = v
        self.old_lat_long = old_lat_long
        self.new_lat_long = new_lat_long
        self.old_pos = old_pos
        self.new_pos = new_pos


class Test3DWinds(unittest.TestCase):
    def setUp(self):
        self.test_cases = []
        self.test_cases.append(TestCase('stere', 'C:/Users/William/Documents/3dwinds/airs1.flo', 0, 0, pixel_size=4000,
                                        lat_0=60, lon_0=0, distance=255333.02691, shape=(1000,1000),
                                        speed=42.57497, angle=312.6841, u=-31.29698, v=28.86394,
                                        old_lat_long=(67.62333, -137.17366),
                                        new_lat_long=(69.17597, -141.74266),
                                        old_pos=(-1998000.0, 5427327.91718),
                                        new_pos=(-1690795.53223, 5437447.69676)))
        displacement_data = np.array((np.ones((2, 2)), np.ones((2, 2))))
        old_lat_long = ([[10.01808, 10.01808], [9.98192, 9.98192]], [[9.98176, 10.01824], [9.98176, 10.01824]])
        new_lat_long = ([[9.98192, 9.98191], [9.94575, 9.94575]], [[10.01824, 10.05472], [10.01824, 10.05472]])
        old_pos = ([[-2000.0, 2000.0], [-2000.0, 2000.0]], [[2000.0, 2000.0], [-2000.0, -2000.0]])
        new_pos = ([[2000.0, 6000.0], [2000.0, 6000.0]], [[-2000.0, -2000.0], [-6000.0, -6000.0]])
        self.test_cases.append(TestCase('stere', displacement_data, pixel_size=4, lat_0=10, lon_0=10,
                                        distance=56.56842, shape=(2, 2), units='km', center=(10, 10),
                                        speed=([0.94281, 0.94281], [0.94281, 0.94281]),
                                        angle=([135.0, 135.00629], [135.0, 135.00628]),
                                        u=([0.66667, 0.66659], [0.66667, 0.66659]),
                                        v=([-0.66667, -0.66674], [-0.66667, -0.66674]),
                                        old_lat_long=old_lat_long,
                                        new_lat_long=new_lat_long,
                                        old_pos=old_pos, new_pos=new_pos))

    def test_calculate_velocity(self):
        from main import calculate_velocity
        for case in self.test_cases:
            speed, angle = calculate_velocity(case.projection, case.displacement_data, case.i_old, case.j_old,
                                              shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0,
                                              lon_0=case.lon_0, center=case.center, units=case.units)
            # print('velocity:', '{0} m/sec, {1}°'.format(speed, angle))
            if np.size(speed) == 1:
                self.assertEqual(case.speed, round(speed, 5))
                self.assertEqual(case.angle, round(angle, 5))
            else:
                self.assertEqual(case.speed, tuple(np.round(speed, 5).tolist()))
                self.assertEqual(case.angle, tuple(np.round(angle, 5).tolist()))

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.projection, case.displacement_data, case.i_old, case.j_old,
                                 shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0, lon_0=case.lon_0,
                                 center=case.center, units=case.units)
            # print('(u, v):', '({0} m/sec, {1} m/sec)'.format(u, v))
            if np.size(u) == 1:
                self.assertEqual(case.u, round(u, 5))
                self.assertEqual(case.v, round(v, 5))
            else:
                self.assertEqual(case.u, tuple(np.round(u, 5).tolist()))
                self.assertEqual(case.v, tuple(np.round(v, 5).tolist()))

    def test_compute_lat_long(self):
        from main import compute_lat_long
        for case in self.test_cases:
            old_lat_long = compute_lat_long(case.projection, case.i_old, case.j_old,
                                            shape=case.shape, pixel_size=case.pixel_size,
                                            lat_0=case.lat_0, lon_0=case.lon_0, center=case.center, units=case.units)
            new_lat_long = compute_lat_long(case.projection, case.i_new, case.j_new, shape=case.shape,
                                            pixel_size=case.pixel_size, lat_0=case.lat_0, lon_0=case.lon_0,
                                            center=case.center, units=case.units)
            # print('old_lat_long:', old_lat_long)
            # print('new_lat_long:', new_lat_long)
            self.assertEqual(case.old_lat_long, tuple(np.round(old_lat_long, 5).tolist()))
            self.assertEqual(case.new_lat_long, tuple(np.round(new_lat_long, 5).tolist()))

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos, get_area
        for case in self.test_cases:
            area_definition = get_area(case.projection, (case.lat_0, case.lon_0), case.shape, case.pixel_size,
                                       geod=case.image_geod, units=case.units, center=case.center)
            old_pos = _pixel_to_pos(area_definition, i=case.i_old, j=case.j_old)
            new_pos = _pixel_to_pos(area_definition, i=case.i_new, j=case.j_new)
            # print('old_pos:', old_pos)
            # print('new_pos:', new_pos)
            self.assertEqual(case.old_pos, tuple(np.round(old_pos, 5).tolist()))
            self.assertEqual(case.new_pos, tuple(np.round(new_pos, 5).tolist()))


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
