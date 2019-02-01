import unittest
import numpy as np
from pyproj import Geod


class TestCase():
    def __init__(self, area_definition, i_old, j_old, i_displacements, j_displacements, distance=None, speed=None,
                 angle=None, u=None, v=None, old_lat_long=None, new_lat_long=None, old_pos=None, new_pos=None):
        #  Input data
        self.i_old = i_old
        self.j_old = j_old
        self.area_definition = area_definition
        # Pixel_x displacement
        self.i_displacements = i_displacements
        # Pixel_y displacement
        self.j_displacements = j_displacements
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
        from main import get_displacements, get_area
        from pyresample.geometry import AreaDefinition
        self.test_cases = []
        # TODO: VERIFY WHAT THE AREA IS.
        area_def = get_area(0, 60, 'stere', 'm', (1000, 1000), 4000, (0, 90))
        # i, j displacement: even index, odd index
        i_displacements, j_displacements = get_displacements('C:/Users/William/Documents/3dwinds/airs1.flo',
                                                             shape=(1000, 1000))
        u_out = np.fromfile('C:/Users/William/Documents/3dwinds/u.out', dtype=np.float32).reshape((1000, 1000))
        v_out = np.fromfile('C:/Users/William/Documents/3dwinds/v.out', dtype=np.float32).reshape((1000, 1000))
        self.test_cases.append(TestCase(area_def, 0, 0, i_displacements, j_displacements, distance=255333.02691,
                                        speed=42.5555, angle=310.54371, u=-32.33837, v=27.66227,
                                        old_lat_long=(67.62333, -137.17366),
                                        new_lat_long=(69.17597, -141.74266),
                                        old_pos=(-1998000.0, 5427327.91718),
                                        new_pos=(-1690795.53223, 5437447.69676)))
        self.test_cases.append(TestCase(area_def, 500, 500, i_displacements, j_displacements, distance=9825.44021,
                                        speed=1.63757, angle=187.99136, u=-0.22766, v=-1.62167,
                                        old_lat_long=(89.97641, 45.00226),
                                        new_lat_long=(89.93306, -103.7702),
                                        old_pos=(2000.0, 3427327.91718),
                                        new_pos=(-7796.72623, 3431237.40586)))
        area_def = AreaDefinition('3DWinds', '3DWinds', '3DWinds',
                                  {'lat_0': 10, 'lon_0': 10, 'proj': 'stere', 'units': 'km'},
                                  5, 5, [-10, -10, 10, 10])
        # i displacement: odd index
        i_displacements = np.ones((5, 5)) * .01
        # j displacement: even index
        j_displacements = np.ones((5, 5)) * .01
        self.test_cases.append(TestCase(area_def, 0, 0, i_displacements, j_displacements, distance=56.56842,
                                        speed=0.00943, angle=134.98743, u=0.00667, v=-0.00667,
                                        old_lat_long=(10.07232, 9.92702),
                                        new_lat_long=(10.07196, 9.92738),
                                        old_pos=(-8000.0, 8000.0), new_pos=(-7960.0, 7960.0)))

    def test_calculate_velocity(self):
        from main import calculate_velocity
        for case in self.test_cases:
            speed, angle = calculate_velocity(case.i_old, case.j_old, case.i_displacements[case.i_old][case.j_old],
                                              case.j_displacements[case.i_old][case.j_old], case.area_definition)
            # print('velocity:', '{0} m/sec, {1}°'.format(speed, angle))
            self.assertEqual(case.speed, round(speed, 5))
            self.assertEqual(case.angle, round(angle, 5))

    def test_u_v_component(self):
        from main import u_v_component
        for case in self.test_cases:
            u, v = u_v_component(case.i_old, case.j_old, case.i_displacements[case.i_old][case.j_old],
                                 case.j_displacements[case.i_old][case.j_old], case.area_definition)
            # print('(u, v):', '({0} m/sec, {1} m/sec)'.format(u, v))
            self.assertEqual(case.u, round(u, 5))
            self.assertEqual(case.v, round(v, 5))

    def test_compute_lat_long(self):
        from main import compute_lat_long
        import math
        import numpy as np
        for case in self.test_cases:
            old_lat_long = compute_lat_long(case.i_old, case.j_old, case.area_definition)
            # print('old_lat_long:', old_lat_long)
            self.assertEqual(case.old_lat_long, tuple(np.round(old_lat_long, 5)))
            new_lat_long = compute_lat_long(case.i_new, case.j_new, case.area_definition)
            # print('new_lat_long:', new_lat_long)
            self.assertEqual(case.new_lat_long, tuple(np.round(new_lat_long, 5)))
            # # Uses a sphere as an ellipsoid
            # Z = math.pi / 180
            # R = 6370.997
            # RLAT = 67.62332747020073 * Z
            # RLON = -137.1736645856486 * Z
            # PLAT = 69.17597131140518 * Z
            # PLON = -141.7426590658713 * Z
            # CRLAT = math.cos(RLAT)
            # CRLON = math.cos(RLON)
            # SRLAT = math.sin(RLAT)
            # SRLON = math.sin(RLON)
            # CPLAT = math.cos(PLAT)
            # CPLON = math.cos(PLON)
            # SPLAT = math.sin(PLAT)
            # SPLON = math.sin(PLON)
            # XX = CPLAT * CPLON - CRLAT * CRLON
            # YY = CPLAT * SPLON - CRLAT * SRLON
            # ZZ = SPLAT - SRLAT
            # DIST = math.sqrt(XX * XX + YY * YY + ZZ * ZZ)
            # ARCL = 2. * math.asin(DIST / 2.) * R
            #
            # if abs(DIST) > 0.0001:
            #     ANG = math.sin(RLON - PLON) * math.sin(math.pi / 2. - PLAT) / math.sin(DIST)
            # else:
            #     ANG = 0
            # if abs(ANG) > 1.0:
            #     ANG = np.sign(ANG)
            # ANG = math.asin(ANG) / Z
            # if PLAT < RLAT:
            #     ANG = 180. - ANG
            # if ANG < 0.0:
            #     ANG = 360. + ANG
            # IANG = (ANG + 180) % 360
            # print('IANG, ARCL: ', IANG, ARCL)
            # g = Geod(ellps='WGS84')
            # my_angle = g.inv(*(-137.1736645856486, 67.62332747020073), *(-141.7426590658713, 69.17597131140518))[1] + 180
            # print(my_angle, my_angle - IANG)

    def test_pixel_to_pos(self):
        from main import _pixel_to_pos
        for case in self.test_cases:
            old_pos = _pixel_to_pos(case.i_old, case.j_old, case.area_definition)
            new_pos = _pixel_to_pos(case.i_new, case.j_new, case.area_definition)
            # print('old_pos:', old_pos)
            self.assertEqual(case.old_pos, tuple(np.round(old_pos, 5)))
            # print('new_pos:', new_pos)
            self.assertEqual(case.new_pos, tuple(np.round(new_pos, 5)))

    def test_calculate_displacement_vector(self):
        from main import _calculate_displacement_vector
        for case in self.test_cases:
            angle, distance = _calculate_displacement_vector(case.i_old, case.j_old,
                                                             case.i_displacements[case.i_old][case.j_old],
                                                             case.j_displacements[case.i_old][case.j_old],
                                                             case.area_definition)
            # print('displacement_vector:', '({0}, {1})'.format(angle, distance))
            self.assertEqual(case.angle, round(angle, 5))
            self.assertEqual(case.distance, round(distance, 5))


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
