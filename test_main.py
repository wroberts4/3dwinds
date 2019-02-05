from pyproj import Geod
import unittest
import numpy as np


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                 lon_0=None, image_geod=Geod(ellps='WGS84'), earth_geod=Geod(ellps='WGS84'), units='m', center=None,
                 distance=None, speed=None, angle=None, u=None, v=None, old_lat_long=None, new_lat_long=None,
                 old_pos=None, new_pos=None):
        from main import get_displacements, _get_delta
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
        self.displacement_data = displacement_data
        self.shape = shape
        self.center = center
        self.i_displacements, self.j_displacements, self.shape = _get_delta(i, j, *get_displacements(displacement_data,
                                                                                                     shape=shape))
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
        self.test_cases.append(TestCase('/Users/wroberts/Documents/3dwinds/airs1.flo', i=0, j=0, pixel_size=4000,
                                        lat_0=60, lon_0=0, distance=255333.02691, shape=(1000,1000), center=(90, 0),
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
        self.test_cases.append(TestCase(displacement_data, pixel_size=4, lat_0=10, lon_0=10,
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
            speed, angle = calculate_velocity(case.displacement_data, projection=case.projection, i=case.i, j=case.j,
                                              shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0,
                                              lon_0=case.lon_0, center=case.center, units=case.units)
            if np.size(speed) == 1:
                self.assertEqual(case.speed, round(speed, 5))
                self.assertEqual(case.angle, round(angle, 5))
            else:
                self.assertEqual(case.speed, tuple(np.round(speed, 5).tolist()))
                self.assertEqual(case.angle, tuple(np.round(angle, 5).tolist()))

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.displacement_data, projection=case.projection, i=case.i, j=case.j,
                                 shape=case.shape, pixel_size=case.pixel_size, lat_0=case.lat_0, lon_0=case.lon_0,
                                 center=case.center, units=case.units)
            if np.size(u) == 1:
                self.assertEqual(case.u, round(u, 5))
                self.assertEqual(case.v, round(v, 5))
            else:
                self.assertEqual(case.u, tuple(np.round(u, 5).tolist()))
                self.assertEqual(case.v, tuple(np.round(v, 5).tolist()))

    def test_compute_lat_long(self):
        from main import compute_lat_long, _compute_lat_long
        for case in self.test_cases:
            old_lat_long = compute_lat_long(projection=case.projection, i=case.i, j=case.j,
                                            shape=case.shape, pixel_size=case.pixel_size,
                                            lat_0=case.lat_0, lon_0=case.lon_0, center=case.center, units=case.units)
            new_lat_long = _compute_lat_long(projection=case.projection, i=case.i, j=case.j, shape=case.shape,
                                            pixel_size=case.pixel_size, lat_0=case.lat_0, lon_0=case.lon_0,
                                            center=case.center, units=case.units,
                                            delta_i=case.i_displacements,
                                            delta_j=case.j_displacements)
            self.assertEqual(case.old_lat_long, tuple(np.round(old_lat_long, 5).tolist()))
            self.assertEqual(case.new_lat_long, tuple(np.round(new_lat_long, 5).tolist()))

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos, get_area, _extrapolate_i_j
        for case in self.test_cases:
            area_definition = get_area(case.projection, (case.lat_0, case.lon_0), case.shape, case.pixel_size,
                                       geod=case.image_geod, units=case.units, center=case.center)
            i_old, j_old = _extrapolate_i_j(case.i, case.j, case.shape)
            i_new, j_new = _extrapolate_i_j(case.i, case.j, case.shape, case.i_displacements, case.j_displacements)
            old_pos = _pixel_to_pos(area_definition, i=i_old, j=j_old)
            new_pos = _pixel_to_pos(area_definition, i=i_new, j=j_new)
            self.assertEqual(case.old_pos, tuple(np.round(old_pos, 5).tolist()))
            self.assertEqual(case.new_pos, tuple(np.round(new_pos, 5).tolist()))


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
