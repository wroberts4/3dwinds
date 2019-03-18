Usage
=====

Use the **-h** or **--help** flags on any of these scripts to print usage.

wind_info.sh
------------
Calculates area information, j and i displacement, new and old latitude/longitude, v, u, and velocity of the wind.

Required arguments:

* **lat_ts**: Latitude of true scale
* **lat_0**: Latitude of origin
* **long_0**: Central meridian
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long).
  Defaults to [lat_0, long_0] if not provided
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves data and does not print data to shell
  2. When flagged: prints data to shell without saving

.. note::

    wind_info is saved to to name_of_projection.txt, j_displacement.txt, i_displacement.txt, new_latitude.txt,
    new_longitude.txt, old_latitude.txt, old_longitude.txt, v.txt, u.txt, speed.txt, angle.txt, and wind_info.txt
    in that order (name_of_projection varies depending on the type of projection). Each of these variables are
    saved to wind_info.hdf5 by the same name as their .txt counterparts in a new directory by the name of the
    displacement file appended with "_output", which will be created where the script is ran.

Calculating wind_info::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/velocity.sh 60 90 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0 --no_save
    [67.62, -137.17, 42.33, 317.58, 31.25, -28.55]
    $ pywinds/wind_info.sh 60 0 100 --pixel_size 4000 --center 90,0
    Saving data to the directory /Desktop/in.flo_output


Print and Save Format
---------------------

If j and i values are provided, then data is calculated at a single pixel:

::

    wind_info: [new_latitude, new_longitude, velocity, angle, v, u]

    velocity: [speed, direction]

    lat_long: [latitude, longitude]

    displacements: [j_displacement, i_displacement]

If no j and i values are provided, then velocity is calculated at every pixel (n-rows, m-columns):

::

    wind_info:
        [[latitude_11, longitude_11, velocity_11, angle_11, v_11, u_11],
         ...,
         [latitude_1m, longitude_1m, velocity_1m, angle_1m, v_1m, u_1m],
         ...,
         [latitude_nm, longitude_nm, velocity_nm, angle_nm, v_nm, u_nm]]

    lat_long:
        [[latitude_11, longitude_11, velocity_11, angle_11, v_11, u_11],
         ...,
         [latitude_1m, longitude_1m, velocity_1m, angle_1m, v_1m, u_1m],
         ...,
         [latitude_nm, longitude_nm, velocity_nm, angle_nm, v_nm, u_nm]]

Area is saved and printed in different formats

::

    area:
        projection:
        lat_0:
        long_0:
        equatorial radius:
        eccentricity:
        flattening:
        area_extent:
        shape:
        pixel_size:
        center:


Advanced arguments
------------------

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_spheroid**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

velocity.sh
-----------

Calculates the speed and angle of wind given an area and displacements at pixel(s).

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data.
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves velocity and does not print velocity to shell
  2. When flagged: prints velocity to shell without saving

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_spheroid**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

If j and i values are provided, then velocity is calculated at a single pixel:

::

    [speed, direction]

If no j and i values are provided, then velocity is calculated at every pixel (n-rows, m-columns):

::

    [[[speed_11, ..., speed_1m],
      ...,
      [speed_n1, ..., speed_nm]],
     [[angle_11, ..., angle_1m],
      ...,
      [angle_n1, ..., angle_nm]]]

.. note::

    velocity is saved to to speed.txt, angle.txt, and wind_info.hdf5 (under the group "velocity")
    in a new directory by the name of the displacement file appended with "_output", which will be
    created where the script is ran

Calculating velocity::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0 --no_save
    [42.33, 317.58]
    $ pywinds/velocity.sh 60 0 100 --pixel_size 4000 --center 90,0
    Saving velocity to:
    /Desktop/in.flo_output/speed.txt
    /Desktop/in.flo_output/angle.txt
    /Desktop/in.flo_output/wind_info.hdf5


vu.sh
-----

Calculates the v and u component of wind at pixel(s).

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data.
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves vu and does not print vu to shell
  2. When flagged: prints vu to shell without saving

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_spheroid**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

If j and i values are provided, then vu is calculated at a single pixel:

::

    [v, u]

If no j and i values are provided, then vu is calculated at every pixel (n-rows, m-columns):

::

    [[[v_11, ..., v_1m],
      ...,
      [v_n1, ..., v_nm]],
     [[u_11, ..., u_1m],
      ...,
      [u_n1, ..., u_nm]]]

.. note::

    vu is saved to to v.txt, u.txt, and wind_info.hdf5 (under the group "vu")
    in a new directory by the name of the displacement file appended with "_output",
    which will be created where the script is ran

Calculating vu::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/vu.sh 60 0 100 --j 0 --i 0
      --pixel_size 4000 --center 90,0 --no_save
    [31.25, -28.55]
    $ pywinds/vu.sh 60 0 100
      --pixel_size 4000 --center 90,0
    Saving vu to:
    /Desktop/in.flo_output/v.txt
    /Desktop/in.flo_output/u.txt
    /Desktop/in.flo_output/wind_info.hdf5


lat_long.sh
-----------

Calculates the latitude and longitude of pixel(s).

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection

Optional arguments:

* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data.
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, then old lats/longs will be calculated. If provided, new lats/longs will be calculated.
  Thus does **NOT** default to searching for displacement files.
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves lat_long and does not print lat_long to shell
  2. When flagged: prints lat_long to shell without saving

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

If j and i values are provided, then lat_long is calculated at a single pixel:

::

    [latitude, longitude]

If no j and i values are provided, then lat_long is calculated at every pixel (n-rows, m-columns):

::

    [[[latitude_11, ..., latitude_1m],
      ...,
      [latitude_n1, ..., latitude_nm]],
     [[longitude_11, ..., longitude_1m],
      ...,
      [longitude_n1, ..., longitude_nm]]]

.. note::

    lat_long is saved to to old_latitude.txt, old_longitude.txt, new_latitude.txt, new_longitude.txt,
    and wind_info.hdf5 (under the group "lat_long") in a new directory by the name of the displacement
    file appended with "_output", which will be created where the script is ran. Thus displacement_data must be
    provided in order to save lat_long to a file.

Calculating lat_long::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/lat_long.sh 60 0 --j 0 --i 0
      --pixel_size 4000 --center 90,0 --shape 1000,1000 --no_save
    [67.62, -137.17]
    $ pywinds/lat_long.sh 60 0 --j 0 --i 0 --pixel_size 4000
      --center 90,0 --displacement_data "'in.flo'" --no_save
    [65.94, -133.28]
    $ pywinds/lat_long.sh 60 0 --pixel_size 4000
      --center 90,0 --displacement_data "'in.flo'"
    Saving lat_long to:
    /Desktop/in.flo_output/old_latitude.txt
    /Desktop/in.flo_output/old_longitude.txt
    /Desktop/in.flo_output/new_latitude.txt
    /Desktop/in.flo_output/new_longitude.txt
    /Desktop/in.flo_output/wind_info.hdf5


displacements.sh
----------------

Finds displacements of pixel(s).

Optional arguments:

* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data.
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **no_save**:

  1. When not flagged (Default): saves displacements and does not print displacements to shell
  2. When flagged: prints displacements to shell without saving

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    displacements is saved to to j_displacement.txt, i_displacement.txt, and wind_info.hdf5
    (under the group "displacements") in a new directory by the name of the displacement
    file appended with "_output", which will be created where the script is ran. Thus
    displacement_data must be found in order to save displacements to a file.

If j and i values are provided, then displacements is calculated at a single pixel:

::

    [j_displacement, i_displacement]

If no j and i values are provided, then displacements is calculated at every pixel (n-rows, m-columns):

::

    [[[j_displacement_11, ..., j_displacement_1m],
      ...,
      [j_displacement_n1, ..., j_displacement_nm]],
     [[i_displacement_11, ..., i_displacement_1m],
      ...,
      [i_displacement_n1, ..., i_displacement_nm]]]

Calculating displacements::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/displacements.sh --j 0 --i 0 --no_save
    [-2.53, 76.8]
    $ pywinds/displacements.sh
    Saving displacements to:
    /Desktop/in.flo_output/j_displacement.txt
    /Desktop/in.flo_output/i_displacement.txt
    /Desktop/in.flo_output/wind_info.hdf5


area.sh
-------

Calculates information about the area that images are describing.

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection

Optional arguments:

* **center**: Projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from displacement_data.
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **no_save**:

  1. When not flagged (Default): saves lat_long and does not print lat_long to shell
  2. When flagged: prints lat_long to shell without saving

* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    area is saved to to area.txt and wind_info.hdf5 (under the group "area")
    in a new directory by the name of the displacement file appended with "_output",
    which will be created where the script is ran. Thus displacement_data must be
    found in order to save area to a file.

Calculating area::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/area.sh 60 0 --pixel_size 4000 --center 90,0 --no_save
    projection: stere
    lat_0: 60
    long_0: 0
    equatorial radius: 6378137.0
    eccentricity: 0.003353
    area_extent: (65.81, -47.35, 67.6, 137.18)
    shape: (1000, 1000)
    pixel_size: (4000.0, 4000.0)
    center: (90.0, 0.0)
    $ pywinds/area.sh 60 0 --pixel_size 4000 --center 90,0
    Saving area to:
    /Desktop/in.flo_output/area.txt
    /Desktop/in.flo_output/wind_info.hdf5

