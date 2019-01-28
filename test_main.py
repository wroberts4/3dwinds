import unittest
import numpy as np


class TestCase():
    def __init__(self, area_definition, i_old, j_old, x_displacements, y_displacements, distance=None, speed=None,
                 angle=None, u=None, v=None, old_lon_lat=None, new_lon_lat=None, old_pos=None, new_pos=None):
        #  Input data
        self.i_old = i_old
        self.j_old = j_old
        self.area_definition = area_definition
        # Pixel_x displacement
        self.x_displacements = x_displacements
        # Pixel_y displacement
        self.y_displacements = y_displacements
        self.x_new = i_old + x_displacements[i_old][j_old]
        # TODO: IS NEGATIVE Y DISPLACEMENT UP?
        self.y_new = j_old + y_displacements[i_old][j_old]
        # Output data
        self.distance = distance
        self.speed = speed
        self.angle = angle
        self.u = u
        self.v = v
        self.old_lon_lat = old_lon_lat
        self.new_lon_lat = new_lon_lat
        self.old_pos = old_pos
        self.new_pos = new_pos


class Test3DWinds(unittest.TestCase):
    def setUp(self):
        from main import get_displacements, get_area
        from pyresample.geometry import AreaDefinition
        self.test_cases = []
        # TODO: VERIFY WHAT THE AREA IS.
        area_def = get_area(0, 60, 'stere', 'm', (1000, 1000), 4000, (0, 90))
        # i, j displacement: even index, odd index
        x_displacements, y_displacements = get_displacements('/Users/wroberts/Documents/optical_flow/airs1.flo',
                                                             (1000, 1000))
        self.test_cases.append(TestCase(area_def, 500, 500, x_displacements, y_displacements, distance=9825.4402089071,
                                        speed=5.8952641253, angle=-23.236181832, u=5.4170779396, v=-2.3258129125,
                                        old_lon_lat=(45.00226285953939, 89.97641074433204),
                                        new_lon_lat=(-103.77020444095085, 89.93305827798719),
                                        old_pos=(2000.0, 3427327.917177815),
                                        new_pos=(-7796.7262268066, 3431237.4058557935)))
        area_def = AreaDefinition('daves', 'daves', 'daves',
                                  {'lat_0': '0.0', 'lon_0': '0.0', 'proj': 'stere', 'units': 'km'},
                                  5, 5, [-10, -10, 10, 10])
        # i displacement: odd index
        x_displacements = np.ones((5, 5))
        # j displacement: even index
        y_displacements = np.ones((5, 5))
        self.test_cases.append(TestCase(area_def, 0, 0, x_displacements, y_displacements, distance=5656.8516362645,
                                        speed=3.3941109818, angle=134.9999548033, u=-2.3999969981, v=2.4000007845,
                                        old_lon_lat=(-0.0718652415729765, 0.07234951970824183),
                                        new_lon_lat=(-0.03593261372020854, 0.036174774274673145),
                                        old_pos=(-8.0, 8.0), new_pos=(-4.0, 4.0)))

    def test_calculate_velocity(self):
        from main import calculate_velocity
        for case in self.test_cases:
            speed, angle = calculate_velocity(case.i_old, case.j_old, case.x_displacements[case.i_old][case.j_old],
                                              case.y_displacements[case.i_old][case.j_old], case.area_definition)
            # print('velocity:', '{0} km/hr, {1}°'.format(speed, angle))
            self.assertEqual(round(speed, 10), case.speed)
            self.assertEqual(round(angle, 10), case.angle)

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.i_old, case.j_old, case.x_displacements[case.i_old][case.j_old],
                                 case.y_displacements[case.i_old][case.j_old], case.area_definition)
            # print('(u, v):', '({0} km/hr, {1} km/hr)'.format(u, v))
            self.assertEqual(round(u, 10), case.u)
            self.assertEqual(round(v, 10), case.v)

    def test_compute_lat_lon(self):
        from main import compute_lat_lon
        for case in self.test_cases:
            old_lon_lat = compute_lat_lon(case.i_old, case.j_old, case.area_definition)
            # print('old_lon_lat:', old_lon_lat)
            self.assertEqual(old_lon_lat, case.old_lon_lat)
            new_lon_lat = compute_lat_lon(case.x_new, case.y_new, case.area_definition)
            # print('new_lon_lat:', new_lon_lat)
            self.assertEqual(new_lon_lat, case.new_lon_lat)

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos
        for case in self.test_cases:
            old_pos = _pixel_to_pos(case.i_old, case.j_old, case.area_definition)
            new_pos = _pixel_to_pos(case.x_new, case.y_new, case.area_definition)
            # print('old_pos:', old_pos)
            self.assertEqual(tuple(np.round(old_pos, 10)), case.old_pos)
            # print('new_pos:', new_pos)
            self.assertEqual(tuple(np.round(new_pos, 10)), case.new_pos)

    def test_calculate_displacement_vector(self):
        from main import _calculate_displacement_vector
        for case in self.test_cases:
            angle, distance = _calculate_displacement_vector(case.i_old, case.j_old,
                                                             case.x_displacements[case.i_old][case.j_old],
                                                             case.y_displacements[case.i_old][case.j_old],
                                                             case.area_definition)
            # print('displacement_vector:', '({0}, {1})'.format(angle, distance))
            self.assertEqual(round(angle, 10), case.angle)
            self.assertEqual(round(distance, 10), case.distance)


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
