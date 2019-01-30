import unittest
import numpy as np
from pyproj import Geod


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
        self.i_new = i_old + x_displacements[i_old][j_old]
        # TODO: IS NEGATIVE Y DISPLACEMENT UP?
        self.j_new = j_old + y_displacements[i_old][j_old]
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
        x_displacements, y_displacements = get_displacements('C:/Users/William/Documents/3dwinds/airs1.flo',
                                                             shape=(1000, 1000))
        u_out = np.fromfile('C:/Users/William/Documents/3dwinds/u.out', dtype=np.float32).reshape((1000, 1000))
        v_out = np.fromfile('C:/Users/William/Documents/3dwinds/v.out', dtype=np.float32).reshape((1000, 1000))
        self.test_cases.append(TestCase(area_def, 500, 500, x_displacements, y_displacements, distance=9825.44020675,
                                        speed=5.89526412, angle=-23.23618184, u=5.41707794, v=-2.32581291,
                                        old_lon_lat=(89.97641074, 45.00226286),
                                        new_lon_lat=(89.93305828, -103.77020444),
                                        old_pos=(2000.0, 3427327.91717782),
                                        new_pos=(-7796.72622681, 3431237.40585579)))
        area_def = AreaDefinition('daves', 'daves', 'daves',
                                  {'lat_0': '0.0', 'lon_0': '0.0', 'proj': 'stere', 'units': 'km'},
                                  5, 5, [-10, -10, 10, 10])
        # i displacement: odd index
        x_displacements = np.ones((5, 5))
        # j displacement: even index
        y_displacements = np.ones((5, 5))
        self.test_cases.append(TestCase(area_def, 0, 0, x_displacements, y_displacements, distance=5656.85163627,
                                        speed=3.39411098, angle=134.9999548, u=-2.399997, v=2.40000078,
                                        old_lon_lat=(0.07234952, -0.07186524),
                                        new_lon_lat=(0.03617477, -0.03593261),
                                        old_pos=(-8.0, 8.0), new_pos=(-4.0, 4.0)))

    def test_calculate_velocity(self):
        from main import calculate_velocity
        for case in self.test_cases:
            speed, angle = calculate_velocity(case.i_old, case.j_old, case.x_displacements[case.i_old][case.j_old],
                                              case.y_displacements[case.i_old][case.j_old], case.area_definition)
            # print('velocity:', '{0} km/hr, {1}°'.format(speed, angle))
            self.assertEqual(case.speed, round(speed, 8))
            self.assertEqual(case.angle, round(angle, 8))

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.i_old, case.j_old, case.x_displacements[case.i_old][case.j_old],
                                 case.y_displacements[case.i_old][case.j_old], case.area_definition)
            # print('(u, v):', '({0} km/hr, {1} km/hr)'.format(u, v))
            self.assertEqual(case.u, round(u, 8))
            self.assertEqual(case.v, round(v, 8))

    def test_compute_lat_long(self):
        from main import compute_lat_long
        import math
        import numpy as np
        for case in self.test_cases:
            old_lon_lat = compute_lat_long(case.i_old, case.j_old, case.area_definition)
            # print('old_lon_lat:', old_lon_lat)
            self.assertEqual(case.old_lon_lat, tuple(np.round(old_lon_lat, 8)))
            new_lon_lat = compute_lat_long(case.i_new, case.j_new, case.area_definition)
            # print('new_lon_lat:', new_lon_lat)
            self.assertEqual(case.new_lon_lat, tuple(np.round(new_lon_lat, 8)))
            self.assertEqual(case.new_lon_lat, tuple(np.round(new_lon_lat, 8)))
            # Uses a sphere as an ellipsoid
            Z = math.pi / 180
            R = 6370.997
            RLAT = 40 * Z
            RLON = 0 * Z
            PLAT = 40 * Z
            PLON = 40 * Z
            CRLAT = math.cos(RLAT)
            CRLON = math.cos(RLON)
            SRLAT = math.sin(RLAT)
            SRLON = math.sin(RLON)
            CPLAT = math.cos(PLAT)
            CPLON = math.cos(PLON)
            SPLAT = math.sin(PLAT)
            SPLON = math.sin(PLON)
            XX = CPLAT * CPLON - CRLAT * CRLON
            YY = CPLAT * SPLON - CRLAT * SRLON
            ZZ = SPLAT - SRLAT
            DIST = math.sqrt(XX * XX + YY * YY + ZZ * ZZ)
            ARCL = 2. * math.asin(DIST / 2.) * R

            if abs(DIST) > 0.0001:
                ANG = math.sin(RLON - PLON) * math.sin(math.pi / 2. - PLAT) / math.sin(DIST)
            else:
                ANG = 0
            if abs(ANG) > 1.0:
                ANG = np.sign(ANG)
            ANG = math.asin(ANG) / Z
            if PLAT < RLAT:
                ANG = 180. - ANG
            if ANG < 0.0:
                ANG = 360. + ANG
            IANG = (ANG + 180) % 360
            print('IANG, ARCL: ', IANG, ARCL)
            g = Geod(ellps='WGS84')
            my_angle = g.inv(*(0, 40), *(40, 40))[1] + 180
            print(my_angle, my_angle - IANG)

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos
        for case in self.test_cases:
            old_pos = _pixel_to_pos(case.i_old, case.j_old, case.area_definition)
            new_pos = _pixel_to_pos(case.i_new, case.j_new, case.area_definition)
            # print('old_pos:', old_pos)
            self.assertEqual(case.old_pos, tuple(np.round(old_pos, 8)))
            # print('new_pos:', new_pos)
            self.assertEqual(case.new_pos, tuple(np.round(new_pos, 8)))

    def test_calculate_displacement_vector(self):
        from main import _calculate_displacement_vector
        for case in self.test_cases:
            angle, distance = _calculate_displacement_vector(case.i_old, case.j_old,
                                                             case.x_displacements[case.i_old][case.j_old],
                                                             case.y_displacements[case.i_old][case.j_old],
                                                             case.area_definition)
            # print('displacement_vector:', '({0}, {1})'.format(angle, distance))
            self.assertEqual(case.angle, round(angle, 8))
            self.assertEqual(case.distance, round(distance, 8))


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
