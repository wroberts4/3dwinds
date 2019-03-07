Usage
=====

velocity.sh
-----------

Calculates the speed and angle of wind given an area and displacements.

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction following row-major format (height, width)
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves velocity and does not print velocity to shell
  2. When flagged: prints velocity to shell without saving

* **image_geod**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_geod**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (y_ll, x_ll, y_ur, x_ur)

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

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

Finds vu

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction following row-major format (height, width)
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves vu and does not print vu to shell
  2. When flagged: prints vu to shell without saving

* **image_geod**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_geod**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (y_ll, x_ll, y_ur, x_ur)

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    vu is saved to to v.txt, u.txt, and wind_info.hdf5 (under the group "vu")
    in a new directory by the name of the displacement file appended with "_output",
    which will be created where the script is ran

::

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

Finds lat_long

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection

Optional arguments:

* **center**: projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction following row-major format (height, width)
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, then old lats/longs will be calculated. If provided, new lats/longs will be calculated.
  Thus does **NOT** default to searching for displacement files.
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves lat_long and does not print lat_long to shell
  2. When flagged: prints lat_long to shell without saving

* **image_geod**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (y_ll, x_ll, y_ur, x_ur)

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    lat_long is saved to to old_latitude.txt, old_longitude.txt, new_latitude.txt, new_longitude.txt,
    and wind_info.hdf5 (under the group "lat_long") in a new directory by the name of the displacement
    file appended with "_output", which will be created where the script is ran. Thus displacement_data must be
    provided in order to save lat_long to a file.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/lat_long.sh 60 0 --j 0 --i 0
      --pixel_size 4000 --center 90,0 --shape 1000,1000 --no_save
    [67.62, -137.17]
    $ pywinds/lat_long.sh 60 0 --j 0 --i 0 --pixel_size 4000
      --center 90,0 --displacement_data "'*.flo'" --no_save
    [65.94, -133.28]
    $ pywinds/lat_long.sh 60 0 --pixel_size 4000
      --center 90,0 --displacement_data "'*.flo'"
    Saving lat_long to:
    /Desktop/in.flo_output/old_latitude.txt
    /Desktop/in.flo_output/old_longitude.txt
    /Desktop/in.flo_output/new_latitude.txt
    /Desktop/in.flo_output/new_longitude.txt
    /Desktop/in.flo_output/wind_info.hdf5

displacements.sh
----------------

Finds displacements

Optional arguments:

* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **shape**: Number of pixels in the y and x direction following row-major format (height, width)
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection
* **center**: projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **no_save**:

  1. When not flagged (Default): saves displacements and does not print displacements to shell
  2. When flagged: prints displacements to shell without saving

* **image_geod**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (y_ll, x_ll, y_ur, x_ur)

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    displacements is saved to to j_displacement.txt, i_displacement.txt, and wind_info.hdf5
    (under the group "displacements") in a new directory by the name of the displacement
    file appended with "_output", which will be created where the script is ran. Thus
    displacement_data must be found in order to save displacements to a file.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/displacements.sh --j 0 --i 0 --no_save
    [-2.53, 76.8]
    $ pywinds/displacements.sh --j 1 --i 0 --no_save --shape 100,10000
    [-3.03, 79.19]
    $ pywinds/displacements.sh
    Saving displacements to:
    /Desktop/in.flo_output/j_displacement.txt
    /Desktop/in.flo_output/i_displacement.txt
    /Desktop/in.flo_output/wind_info.hdf5

area.sh
-------

Finds area

Required arguments:

* **lat_0**: Normal latitude of projection
* **long_0**: Normal longitude of projection

Optional arguments:

* **center**: projection y and x coordinate of the center of projection in degrees (lat, long)
* **pixel_size**: Size of pixels in the y and x direction in meters (dy, dx)
* **shape**: Number of pixels in the y and x direction following row-major format (height, width)
* **displacement_data**: Name of file or list containing displacements; wildcard ("*") syntax is accepted.
  If not provided, reads every file ending in ".flo" where the script is ran
* **no_save**:

  1. When not flagged (Default): saves lat_long and does not print lat_long to shell
  2. When flagged: prints lat_long to shell without saving

* **image_geod**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **area_extent**: Area extent as a list (y_ll, x_ll, y_ur, x_ur)

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. note::

    area is saved to to area.txt and wind_info.hdf5 (under the group "area")
    in a new directory by the name of the displacement file appended with "_output",
    which will be created where the script is ran. Thus displacement_data must be
    found in order to save area to a file.

::

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
