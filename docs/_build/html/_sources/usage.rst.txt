Usage
=====

Use the **-h** or **--help** flags on any of these scripts to print a usage message.

wind_info.sh
------------
Calculates area information, j and i displacement, new and old latitude/longitude, v, u, and velocity of the wind.

Required arguments:

* **lat_ts**: Projection latitude of true scale
* **lat_0**: Projection latitude of origin
* **long_0**: Projection central meridian
* **delta_time**: Amount of time that separates both files in minutes

Optional arguments:

* **center**: Projection y and x coordinate of the center of area (lat, long)
* **pixel_size**: Projection size of pixels in the y and x direction (dy, dx)
* **displacement_data**: Name of binary file (32-bit float) containing pixels displacements; How far the
  pixels had to move in the y (positive is down) and x (positive is right) direction to get to their new position.
  Wildcard ("*") syntax is accepted. If not provided, reads every file ending in ".flo" where the script is ran
* **j**: Row to run calculations on
* **i**: Column to run calculations on
* **no_save**:

  1. When not flagged (Default): saves data without printing to shell
  2. When flagged: prints data to shell without saving

Additional information:

    * For more optional arguments, please see :ref:`advanced_arguments`.
    * For more information on save files and their formats, please see :ref:`save_format`

Calculating wind_info::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/velocity.sh 60 90 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0 --no_save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 0 100 --pixel_size 4000 --center 90,0
    Data saved to the directory /Desktop/in.flo_output


For more examples of using wind_info.sh, please see :ref:`Examples_of_wind_info.sh`.

Data format
-------------

If j and i values are provided, then data is calculated at a single pixel:

::

    wind_info: [new_latitude, new_longitude, velocity, angle, v, u]

    velocity: [speed, direction]

    vu: [v, u]

    lat_long: [latitude, longitude]

    displacements: [j_displacement, i_displacement]

If no j and i values are provided, then data is calculated at every pixel (n-rows, m-columns):

::

    wind_info:
        [[new_latitude_11, new_longitude_11, velocity_11, angle_11, v_11, u_11],
         ...,
         [new_latitude_1m, new_longitude_1m, velocity_1m, angle_1m, v_1m, u_1m],
         ...,
         [new_latitude_nm, new_longitude_nm, velocity_nm, angle_nm, v_nm, u_nm]]

    velocity:
        [[[speed_11, ..., speed_1m],
          ...,
          [speed_n1, ..., speed_nm]],
         [[angle_11, ..., angle_1m],
          ...,
          [angle_n1, ..., angle_nm]]]

    vu:
        [[[v_11, ..., v_1m],
          ...,
          [v_n1, ..., v_nm]],
         [[u_11, ..., u_1m],
          ...,
          [u_n1, ..., u_nm]]]

    lat_long:
        [[[latitude_11, ..., latitude_1m],
          ...,
          [latitude_n1, ..., latitude_nm]],
         [[longitude_11, ..., longitude_1m],
          ...,
          [longitude_n1, ..., longitude_nm]]]

    displacements:
        [[[j_displacement_11, ..., j_displacement_1m],
          ...,
          [j_displacement_n1, ..., j_displacement_nm]],
         [[i_displacement_11, ..., i_displacement_1m],
          ...,
          [i_displacement_n1, ..., i_displacement_nm]]]

Area is printed in a different format than it's saved::

    projection:
    lat_ts (degrees):
    lat_0 (degrees):
    long_0 (degrees):
    equatorial_radius (meters):
    eccentricity:
    inverse_flattening:
    shape:
    area_extent (degrees):
    pixel_size (meters):
    center (degrees):


.. _save_format:

Save format
-----------

wind_info.sh saves data to ::

    Text files: polar_stereographic.txt, j_displacement.txt, i_displacement.txt,
                new_latitude.txt, new_longitude.txt, old_latitude.txt, old_longitude.txt,
                v.txt, u.txt, speed.txt, angle.txt, wind_info.txt

    netcdf4 file: wind_info.nc
    

.. note::

    All files are saved in a new directory by the name of the displacement file appended with "_output", which
    will be created where the script is ran.

.. note::

    Data is saved in the order given by "Text files" above, which means that if not enough information
    was provided or an error occurs, data up to that point will be saved.

.. note::

    If re-saving data or saving data with the same **displacement_data** name, it is best to manually
    delete or rename the directory that old data was saved to. This ensures that the directory only
    contains that file's data (in conjunction with the above note).

Text files:

    * Text files are saved as comma separated files (except for polar_stereographic.txt
      which is the same format as it is in wind_info.nc). Numbers are rounded to 2 decimal places.

    * For examples of what the text files looks like, please see :ref:`Content_of_text_files`.

wind_info.nc:
    * wind_info.nc is a netcdf4 file saved using 32-bit floats which follows
      `CF-1.7 conventions <http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apf.html>`_.

    * Each variable listed under "Text files" at the top of this section is saved to wind_info.nc by the same
      name as their .txt counterparts.

    * For an example of what wind_info.nc looks like, please see :ref:`Content_of_wind_info.nc`.

.. _advanced_arguments:

Advanced arguments
------------------

* **projection**: Name of projection that the image is in (stere, laea, merc, etc). Defaults to stere
* **projection_spheroid**: Spheroid of projection (WGS84, sphere, etc). Defaults to WGS84
* **earth_spheroid**: Spheroid of Earth (WGS84, sphere, etc). Defaults to WGS84
* **shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from **displacement_data**
* **upper_left_extent**: Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **radius**: Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
* **units**: Units that provided arguments should be interpreted as. This can be
    one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
    parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
    command. Units are determined in the following priority:

    1. units expressed with variables via @your_units (see 'Using units' under
       :ref:`Examples_of_wind_info.sh` for examples)
    2. units passed to ``--units`` (exluding center)
    3. meters (exluding center, which is degrees)
* **area_extent**: Area extent as a list (lat_ll, long_ll, lat_ur, long_ur)

where

* **lat_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **long_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **lat_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **long_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. warning::

    The shape provided or found can alter the native shape of **displacement_data**.


Additional utility methods
--------------------------

None of these functions can save data, thus they **do not** have the **no_save** argument.
They have similar or identical arguments to wind_info.sh

* **velocity.sh**: Prints just the velocity of the wind. Same arguments as wind_info.sh

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/velocity.sh 60 90 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0
    [51.8, 315.24]


* **vu.sh**: Prints just the v and u components of the wind. Same arguments as wind_info.sh

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/vu.sh 60 90 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0
    [36.78, -36.47]


* **lat_long.sh**: Prints just the latitude and longitude of the pixels. If displacements data is provided,
  then old_latitude and old_longitude are calculated, else new_latitude and new_longitude are calculated.
  Same arguments as wind_info.sh but does not take **delta_time** as an argument.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/lat_long.sh 60 90 0 --j 0 --i 0 --pixel_size 4000
      --center 90,0 --shape 1000,1000
    [63.36, -135.0]
    $ pywinds/lat_long.sh 60 90 0 --j 0 --i 0 --pixel_size 4000
      --center 90,0 --displacement_data in.flo
    [61.38, -130.77]


* **displacements.sh**: Prints just the j and i displacements of the pixels. Does not take **delta_time**
  as an argument. All other required arguments for wind_info.sh are optional arguments.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/displacements.sh --j 0 --i 0
    [-2.53, 76.8]


* **area.sh**: Prints information about the projection given. Same arguments as
  wind_info.sh but does not take **delta_time** as an argument.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ pywinds/area.sh 60 90 0 --pixel_size 4000 --center 90,0
    projection: stere
    lat_ts: 60
    lat_0: 90
    long_0: 0
    equatorial radius: 6378137.0
    eccentricity: 0.003353
    area_extent: (65.81, -47.35, 67.6, 137.18)
    shape: (1000, 1000)
    pixel_size: (4000.0, 4000.0)
    center: (90.0, 0.0)

