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
                                        speed=(42.57497, 2.33208, 1.68887), angle=(312.6841, 249.75364, 312.57015),
                                        u=(-31.29698, -2.18799, -1.24377),
                                        v=(28.86394, -0.80703, 1.14251),
                                        old_lat_long=(67.62333, -137.17366),
                                        new_lat_long=(69.17597, -141.74266),
                                        old_pos=(-1998000.0, 5427327.91718),
                                        new_pos=(-1690795.53223, 5437447.69676)))
        displacement_data = np.array((np.ones((5, 5)) * .01, np.ones((5, 5)) * .01))
        self.test_cases.append(TestCase('stere', displacement_data, pixel_size=4, lat_0=10, lon_0=10,
                                        distance=56.56842, shape=(5, 5), units='km', center=(10, 10),
                                        speed=(0.00943, 0.00943, 0.00943), angle=(134.9874, 135.00003, 135.01257),
                                        u=(0.00667, 0.00667, 0.00667),
                                        v=(-0.00667, -0.00667, -0.00667),
                                        old_lat_long=(10.07232, 9.92702),
                                        new_lat_long=(10.07196, 9.92738),
                                        old_pos=(-8000.0, 8000.0), new_pos=(-7960.0, 7960.0)))

    def test_calculate_velocity(self):
        from main import calculate_velocity
        for case in self.test_cases:
            speed, angle = calculate_velocity(case.projection, case.displacement_data,
                                              [0, np.floor(case.shape[0] / 2), case.shape[0] - 1],
                                              [0, np.floor(case.shape[1] / 2), case.shape[1] - 1],
                                              shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0,
                                              lon_0=case.lon_0, center=case.center, units=case.units)
            # print('velocity:', '{0} m/sec, {1}°'.format(speed, angle))
            self.assertEqual(case.speed, tuple(np.round(speed, 5)))
            self.assertEqual(case.angle, tuple(np.round(angle, 5)))

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.projection, case.displacement_data,
                                 [0, np.floor(case.shape[0] / 2), case.shape[0] - 1],
                                 [0, np.floor(case.shape[1] / 2), case.shape[1] - 1],
                                 shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0, lon_0=case.lon_0,
                                 center=case.center, units=case.units)
            # print('(u, v):', '({0} m/sec, {1} m/sec)'.format(u, v))
            self.assertEqual(case.u, tuple(np.round(u, 5)))
            self.assertEqual(case.v, tuple(np.round(v, 5)))

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
            self.assertEqual(case.old_lat_long, tuple(np.round(old_lat_long, 5)))
            self.assertEqual(case.new_lat_long, tuple(np.round(new_lat_long, 5)))

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos, get_area
        for case in self.test_cases:
            area_definition = get_area(case.projection, (case.lat_0, case.lon_0), case.shape, case.pixel_size,
                                       geod=case.image_geod, units=case.units, center=case.center)
            old_pos = _pixel_to_pos(area_definition, i=case.i_old, j=case.j_old)
            new_pos = _pixel_to_pos(area_definition, i=case.i_new, j=case.j_new)
            # print('old_pos:', old_pos)
            # print('new_pos:', new_pos)
            self.assertEqual(case.old_pos, tuple(np.round(old_pos, 5)))
            self.assertEqual(case.new_pos, tuple(np.round(new_pos, 5)))



def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
