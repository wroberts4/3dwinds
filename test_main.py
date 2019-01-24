import unittest


class Test3DWinds(unittest.TestCase):
    import numpy as np
    from main import compute_lat_lon, u_v_component, calculate_velocity, _pixel_to_pos
    from pyresample.geometry import AreaDefinition
    size = 1000
    x_old = 500
    y_old = 500
    # TODO: VERIFY WHAT THE AREA IS.
    area_definition = AreaDefinition('daves', 'daves', 'daves',
                                     {'lat_0': '60.0', 'lon_0': '0.0', 'proj': 'stere', 'units': 'm'}, size, size,
                                     [-2000000.0, 1429327.9172, 2000000.0, 5429327.9172])

    print('header:', np.fromfile('/Users/wroberts/Documents/optical_flow/airs1.flo', dtype=np.float32)[:3])
    print('-----------------------------------------------------')
    # i (or x or u) displacement: odd index
    x_displacement = np.fromfile('/Users/wroberts/Documents/optical_flow/airs1.flo', dtype=np.float32)[3:][
                     0::2].reshape([size, size])
    print('pixel_x_displacement:', x_displacement[x_old][y_old])
    # j (or y or v) displacement: even index
    y_displacement = np.fromfile('/Users/wroberts/Documents/optical_flow/airs1.flo', dtype=np.float32)[3:][
                     1::2].reshape([size, size])
    print('pixel_y_displacement:', y_displacement[x_old][y_old])

    x_new = x_old + x_displacement[x_old][y_old]
    # TODO: IS NEGATIVE Y DISPLACEMENT UP?
    y_new = y_old + y_displacement[x_old][y_old]

    print('-----------------------------------------------------')
    print('old_pos:', _pixel_to_pos(x_old, y_old, area_definition))
    print('new_pos:', _pixel_to_pos(x_new, y_new, area_definition))

    print('-----------------------------------------------------')
    old_lat_lon = compute_lat_lon(x_old, y_old, area_definition)
    print('old_lon_lat:', old_lat_lon)
    new_lat_lon = compute_lat_lon(x_new, y_new, area_definition)
    print('new_lon_lat:', new_lat_lon)

    print('-----------------------------------------------------')
    print('(u, v):', '({0} km/hr, {1} km/hr)'.format(
        *u_v_component(x_old, y_old, x_displacement[x_old][y_old], y_displacement[x_old][y_old], area_definition)))
    print('velocity:', '{0} km/hr, {1}°'.format(
        *calculate_velocity(x_old, y_old, x_displacement[x_old][y_old], y_displacement[x_old][y_old], area_definition)))


def suite():
    """The test suite for test_main."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(Test3DWinds))
    return mysuite
