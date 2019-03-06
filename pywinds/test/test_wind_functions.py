import unittest
import numpy as np
from pywinds.wind_functions import _create_area, _extrapolate_j_i, _pixel_to_pos, area, displacements, lat_long, \
    velocity, vu, wind_info


class TestCase:
    def __init__(self, displacement_data, projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                 long_0=None, image_geod=None, earth_geod=None, center=None, speed=None, angle=None, u=None, v=None,
                 old_lat=None, old_long=None, new_lat=None, new_long=None, old_x=None, old_y=None, new_x=None,
                 new_y=None, delta_time=100):
        # Input data
        self.i = i
        self.j = j
        self.lat_0 = lat_0
        self.long_0 = long_0
        self.delta_time = delta_time
        self.image_geod = image_geod
        self.earth_geod = earth_geod
        self.pixel_size = pixel_size
        self.projection = projection
        self.displacement_data = displacement_data
        self.center = center
        j_displacements, i_displacements = displacements(lat_0, long_0, displacement_data=displacement_data,
                                                         shape=shape)[:, j, i]
        self.j_displacements = j_displacements
        self.i_displacements = i_displacements
        area_data = area(lat_0, long_0, displacement_data=displacement_data, shape=shape, pixel_size=pixel_size,
                         center=center)
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
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y


class TestPywinds(unittest.TestCase):
    def setUp(self):
        self.test_cases = []
        self.test_cases.append(
            TestCase('./test_files/test_data_two.flo', i=1, j=8, pixel_size=10000, lat_0=60, long_0=0, center=(90, 0),
                     speed=1688.18055, angle=38.95818, u=1061.44852, v=1312.73783, old_lat=18.825, old_long=-142.64162,
                     new_lat=89.58692, new_long=-45.03963, old_x=-8135000.0, old_y=11494327.91718, new_x=-35000.0,
                     new_y=3394327.91718))
        displacement_data = (np.array([x for x in range(100)]) * 10, np.array([x for x in range(100)]) * 20)
        self.test_cases.append(
            TestCase(displacement_data, pixel_size=5000, lat_0=90, long_0=20, i=1, j=8, center=(40, 10),
                     speed=1190.02614, angle=69.74556, u=1116.44031, v=411.97482, old_lat=17.54702, old_long=-58.68524,
                     new_lat=39.84993, new_long=9.86386, old_x=-9151407.88566, old_y=-1831082.99511,
                     new_x=-1051407.88566, new_y=-5881082.99511))

    def test_wind_info(self):
        for case in self.test_cases:
            lat_ji, long_ji, speed_ji, angle_ji, v_ji, u_ji = wind_info(case.lat_0, case.long_0, case.delta_time,
                                                                        displacement_data=case.displacement_data,
                                                                        projection=case.projection, i=case.i, j=case.j,
                                                                        shape=case.shape, pixel_size=case.pixel_size,
                                                                        center=case.center, image_geod=case.image_geod,
                                                                        earth_geod=case.earth_geod).transpose()
            lat, long, speed, angle, v, u = wind_info(case.lat_0, case.long_0, case.delta_time,
                                                      displacement_data=case.displacement_data,
                                                      projection=case.projection, shape=case.shape,
                                                      pixel_size=case.pixel_size, center=case.center,
                                                      image_geod=case.image_geod,
                                                      earth_geod=case.earth_geod).transpose().reshape(
                [6] + list(case.shape))
            self.assertEqual(case.new_lat, round(lat_ji, 5))
            self.assertEqual(case.new_long, round(long_ji, 5))
            self.assertEqual(lat[case.j, case.i], lat_ji)
            self.assertEqual(long[case.j, case.i], long_ji)
            self.assertEqual(case.speed, round(speed_ji, 5))
            self.assertEqual(case.angle, round(angle_ji, 5))
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)
            self.assertEqual(case.v, round(v_ji, 5))
            self.assertEqual(case.u, round(u_ji, 5))
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_velocity(self):
        for case in self.test_cases:
            speed_ji, angle_ji = velocity(case.lat_0, case.long_0, case.delta_time,
                                          displacement_data=case.displacement_data, projection=case.projection,
                                          i=case.i, j=case.j, shape=case.shape, pixel_size=case.pixel_size,
                                          center=case.center, image_geod=case.image_geod, earth_geod=case.earth_geod)
            speed, angle = velocity(case.lat_0, case.long_0, case.delta_time, displacement_data=case.displacement_data,
                                    projection=case.projection, shape=case.shape, pixel_size=case.pixel_size,
                                    center=case.center, image_geod=case.image_geod, earth_geod=case.earth_geod)
            self.assertEqual(case.speed, round(speed_ji, 5))
            self.assertEqual(case.angle, round(angle_ji, 5))
            self.assertEqual(speed[case.j, case.i], speed_ji)
            self.assertEqual(angle[case.j, case.i], angle_ji)

    def test_vu(self):
        for case in self.test_cases:
            v_ji, u_ji = vu(case.lat_0, case.long_0, case.delta_time, displacement_data=case.displacement_data,
                            projection=case.projection, i=case.i, j=case.j, shape=case.shape,
                            pixel_size=case.pixel_size, center=case.center, image_geod=case.image_geod,
                            earth_geod=case.earth_geod)
            v, u = vu(case.lat_0, case.long_0, case.delta_time, displacement_data=case.displacement_data,
                      projection=case.projection, shape=case.shape, pixel_size=case.pixel_size, center=case.center,
                      image_geod=case.image_geod, earth_geod=case.earth_geod)
            self.assertEqual(case.v, round(v_ji, 5))
            self.assertEqual(case.u, round(u_ji, 5))
            self.assertEqual(v[case.j, case.i], v_ji)
            self.assertEqual(u[case.j, case.i], u_ji)

    def test_lat_long(self):
        for case in self.test_cases:
            old_lat_ji, old_long_ji = lat_long(case.lat_0, case.long_0, projection=case.projection, i=case.i,
                                               displacement_data=case.displacement_data, j=case.j,
                                               pixel_size=case.pixel_size, center=case.center,
                                               image_geod=case.image_geod, )
            new_lat_ji, new_long_ji = lat_long(case.lat_0, case.long_0, projection=case.projection, i=case.i, j=case.j,
                                               shape=case.shape, pixel_size=case.pixel_size, center=case.center,
                                               image_geod=case.image_geod, no_save=True)
            old_lat, old_long = lat_long(case.lat_0, case.long_0, projection=case.projection,
                                         displacement_data=case.displacement_data, pixel_size=case.pixel_size,
                                         center=case.center, image_geod=case.image_geod)
            new_lat, new_long = lat_long(case.lat_0, case.long_0, projection=case.projection, shape=case.shape,
                                         pixel_size=case.pixel_size, center=case.center, image_geod=case.image_geod,
                                         no_save=True)
            self.assertEqual(case.old_lat, round(old_lat_ji, 5))
            self.assertEqual(case.old_long, round(old_long_ji, 5))
            self.assertEqual(case.new_lat, round(new_lat_ji, 5))
            self.assertEqual(case.new_long, round(new_long_ji, 5))
            self.assertEqual(old_lat[case.j, case.i], old_lat_ji)
            self.assertEqual(old_long[case.j, case.i], old_long_ji)
            self.assertEqual(new_lat[case.j, case.i], new_lat_ji)
            self.assertEqual(new_long[case.j, case.i], new_long_ji)

    def test_pixel_to_pos(self):
        for case in self.test_cases:
            area_definition = _create_area(case.lat_0, case.long_0, projection=case.projection, shape=case.shape,
                                           pixel_size=case.pixel_size, image_geod=case.image_geod, center=case.center)
            j_new, i_new = _extrapolate_j_i(None, None, case.shape)
            j_old, i_old = j_new - case.j_displacements, i_new - case.i_displacements
            j_new_ji, i_new_ji = _extrapolate_j_i(case.j, case.i, case.shape)
            j_old_ji, i_old_ji = j_new_ji - case.j_displacements, i_new_ji - case.i_displacements
            new_x, new_y = _pixel_to_pos(area_definition, j_new, i_new)
            old_x, old_y = _pixel_to_pos(area_definition, j_old, i_old)
            new_x_ji, new_y_ji = _pixel_to_pos(area_definition, case.j, case.i)
            old_x_ji, old_y_ji = _pixel_to_pos(area_definition, j_old_ji, i_old_ji)
            self.assertEqual(case.old_x, round(old_x_ji, 5))
            self.assertEqual(case.old_y, round(old_y_ji, 5))
            self.assertEqual(case.new_x, round(new_x_ji, 5))
            self.assertEqual(case.new_y, round(new_y_ji, 5))
            self.assertEqual(old_x[case.j * case.shape[0] + case.i], old_x_ji)
            self.assertEqual(old_y[case.j * case.shape[0] + case.i], old_y_ji)
            self.assertEqual(new_x[case.j * case.shape[0] + case.i], new_x_ji)
            self.assertEqual(new_y[case.j * case.shape[0] + case.i], new_y_ji)


def suite():
    """The test suite for test_wind_functions."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestPywinds))
    return mysuite
