from pyproj import transform, Proj, Geod
from pyresample.geometry import AreaDefinition
from pyresample.utils import proj4_str_to_dict
import numpy as np


def _pixel_to_pos(i, j, area_definition):
    u_l_pixel = area_definition.pixel_upper_left
    # (x, y) in projection space.
    position = u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    tmp_proj_dict = area_definition.proj_dict.copy()
    # Get position in meters.
    if tmp_proj_dict['units'] != 'm':
        tmp_proj_dict['units'] = 'm'
        position = transform(p, Proj(tmp_proj_dict, errcheck=True, preserve_units=True), *position)
    return position


def _delta_longitude(new_long, old_long):
    delta_long = new_long - old_long
    if abs(delta_long) > 180.0:
        if delta_long > 0.0:
            return delta_long - 360.0
        else:
            return delta_long + 360.0
    return delta_long


def _make_geod(default, **kwargs):
    # Only allow values that are not None in kwargs:
    for key, val in kwargs.items():
        if val is not None:
            return Geod(**{key: val for key, val in kwargs.items() if val is not None})
    try:
        return Geod(**default)
    except KeyError:
        return Geod(ellps='WGS84')


def _lat_long_dist(lat, g):
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    lat = np.pi / 180 * lat
    lat_dist = 2 * np.pi * g.a * (1 - g.es) / (1 - g.es * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * g.a / (1 - g.es * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def make_geod(default, ellps=None, a=None, b=None, rf=None, f=None, **kwargs):
    """
    ellps: ellipsoid:
        MERIT a=6378137.0      rf=298.257       MERIT 1983
        SGS85 a=6378136.0      rf=298.257       Soviet Geodetic System 85
        GRS80 a=6378137.0      rf=298.257222101 GRS 1980(IUGG, 1980)
        IAU76 a=6378140.0      rf=298.257       IAU 1976
        airy a=6377563.396     b=6356256.910    Airy 1830
        APL4.9 a=6378137.0.    rf=298.25        Appl. Physics. 1965
        APL4.9 a=6378137.0.    rf=298.25        Appl. Physics. 1965
        NWL9D a=6378145.0.     rf=298.25        Naval Weapons Lab., 1965
        mod_airy a=6377340.189 b=6356034.446    Modified Airy
        andrae a=6377104.43    rf=300.0         Andrae 1876 (Den., Iclnd.)
        aust_SA a=6378160.0    rf=298.25        Australian Natl & S. Amer. 1969
        GRS67 a=6378160.0      rf=298.247167427 GRS 67(IUGG 1967)
        bessel a=6377397.155   rf=299.1528128   Bessel 1841
        bess_nam a=6377483.865 rf=299.1528128   Bessel 1841 (Namibia)
        clrk66 a=6378206.4     b=6356583.8      Clarke 1866
        clrk80 a=6378249.145   rf=293.4663      Clarke 1880 mod.
        CPM a=6375738.7        rf=334.29        Comm. des Poids et Mesures 1799
        delmbr a=6376428.      rf=311.5         Delambre 1810 (Belgium)
        engelis a=6378136.05   rf=298.2566      Engelis 1985
        evrst30 a=6377276.345  rf=300.8017      Everest 1830
        evrst48 a=6377304.063  rf=300.8017      Everest 1948
        evrst56 a=6377301.243  rf=300.8017      Everest 1956
        evrst69 a=6377295.664  rf=300.8017      Everest 1969
        evrstSS a=6377298.556  rf=300.8017      Everest (Sabah & Sarawak)
        fschr60 a=6378166.     rf=298.3         Fischer (Mercury Datum) 1960
        fschr60m a=6378155.    rf=298.3         Modified Fischer 1960
        fschr68 a=6378150.     rf=298.3         Fischer 1968
        helmert a=6378200.     rf=298.3         Helmert 1906
        hough a=6378270.0      rf=297.          Hough
        helmert a=6378200.     rf=298.3         Helmert 1906
        hough a=6378270.0      rf=297.          Hough
        intl a=6378388.0       rf=297.          International 1909 (Hayford)
        krass a=6378245.0      rf=298.3         Krassovsky, 1942
        kaula a=6378163.       rf=298.24        Kaula 1961
        lerch a=6378139.       rf=298.257       Lerch 1979
        mprts a=6397300.       rf=191.          Maupertius 1738
        new_intl a=6378157.5   b=6356772.2      New International 1967
        plessis a=6376523.     b=6355863.       Plessis 1817 (France)
        SEasia a=6378155.0     b=6356773.3205   Southeast Asia
        walbeck a=6376896.0    b=6355834.8467   Walbeck
        WGS60 a=6378165.0      rf=298.3         WGS 60
        WGS66 a=6378145.0      rf=298.25        WGS 66
        WGS72 a=6378135.0      rf=298.26        WGS 72
        WGS84 a=6378137.0      rf=298.257223563 WGS 84
        sphere a=6370997.0     b=6370997.0      Normal Sphere (r=6370997)
    a: semi-major or equatorial axis radius
    b: semi-minor, or polar axis radius
    e: eccentricity
    es: eccentricity squared
    f:flattening
    rf: reciprocal flattening
    """
    return _make_geod(default, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)


def get_area(projection, lat_long_0, shape, pixel_size, center=(90, 0), units='m',
             ellps=None, a=None, b=None, rf=None, f=None, **kwargs):
    # proj_dict = {'ellps': 'WGS84', 'lat_0': lat_long_0[0], 'lon_0': lat_long_0[1], 'proj': projection, 'units': units}
    g = make_geod({'ellps': 'WGS84'}, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)
    proj_string = '+lat_0=' + str(lat_long_0[0]) + ' +lon_0=' + str(lat_long_0[1]) +\
                  ' +proj=' + projection + ' +units=' + units + ' ' + g.initstring
    proj_dict = proj4_str_to_dict(proj_string)
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    center = p(*tuple(reversed(center)))
    area_extent = [center[0] - shape[1] * pixel_size / 2, center[1] - shape[0] * pixel_size / 2,
                   center[0] + shape[1] * pixel_size / 2, center[1] + shape[0] * pixel_size / 2]
    return AreaDefinition('3DWinds', '3DWinds', '3DWinds', proj_dict, shape[0], shape[1], area_extent)


def get_displacements(displacment_data, shape=None):
    if isinstance(displacment_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        i_displacements = np.fromfile(displacment_data, dtype=np.float32)[3:][0::2].reshape(shape)
        j_displacements = np.fromfile(displacment_data, dtype=np.float32)[3:][1::2].reshape(shape)
        # Displacements are in pixels.
        return i_displacements, j_displacements
    return displacment_data


def calculate_velocity(displacment_data, i, j, area_definition, delta_time=100, shape=None,
                       ellps=None, a=None, b=None, rf=None, f=None, **kwargs):
    u, v = u_v_component(displacment_data, i, j, area_definition, delta_time=delta_time, shape=shape,
                         ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)
    # When wind vector azimuth is 0 degrees it points North (npematically 90 degrees) and moves clockwise.
    return (u**2 + v**2)**.5, ((90 - np.arctan2(v, u) * 180 / np.pi) + 360) % 360


def u_v_component(displacment_data, i, j, area_definition, delta_time=100, shape=None,
                  ellps=None, a=None, b=None, rf=None, f=None, **kwargs):
    delta_i, delta_j = get_displacements(displacment_data, shape=shape)
    old_lat, old_long = compute_lat_long(i, j, area_definition)
    new_lat, new_long = compute_lat_long(i + delta_i[i][j], j + delta_j[i][j], area_definition)
    g = make_geod(area_definition.proj_dict, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, g)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    u = np.vectorize(_delta_longitude)(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    return u, v


def compute_lat_long(i, j, area_definition):
    proj_dict = area_definition.proj_dict.copy()
    proj_dict['units'] = 'm'
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    return tuple(reversed(p(*_pixel_to_pos(i, j, area_definition), errcheck=True, inverse=True)))
