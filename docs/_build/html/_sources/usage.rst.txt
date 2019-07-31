Usage
=====

Use the **-h** or **------help** flags on any scripts to print a usage message. These scripts follow
GNU command line style; order in which options are provided does not matter and positional arguments may be mixed
in with options (as long as they are not interpreted as part of the option).

.. warning::

    The following is **NOT** interchangeable and calling one is not the same as calling the other:

    * If pywinds was installed via the git repository, then scripts must be called directly (ie **$ wind_info.sh**)
    * If pywinds was installed via the tarball, then scripts must be called as scripts: (ie **$ ./wind_info.sh**)

    **Documentation assumes pywinds was installed using the tarball.**

.. _wind_info.sh:

wind_info.sh
------------
wind_info.sh calculates area information, j and i displacement, new and old latitude/longitude, velocity, and
v and u components of the wind. This is the primary function of pywinds.

Required arguments:

* **lat-ts**: Projection latitude of true scale
* **lat-0**: Projection latitude of origin
* **long-0**: Projection central meridian
* **delta-time**: Amount of time that separates both files in minutes

Optional arguments:

* **------center**: Projection y and x coordinate of the center of area (lat, long). If center is not provided/found
  and the area created is not complete, then center defaults to the projection center (**lat-0**, **long-0**)
* **------pixel-size**: Projection size of pixels in the y and x direction (dy, dx). If pixels are square, i.e. dy = dx,
  then only one value needs to be entered.
* **------displacement-data**: Name of binary file (32-bit float) containing pixels displacements; How far the
  pixels had to move in the y (positive is down) and x (positive is right) direction to get to their new position.
  Wildcard ("*") syntax is accepted when past as a string. If not provided, reads every file ending in ".flo"
  where the script is ran
* **-j**: Row to run calculations on
* **-i**: Column to run calculations on
* **------print** (**-p**):

  1. When not flagged (Default): saves data without printing to shell
  2. When flagged: prints data to shell without saving
* **------verbose** (**-v**): Provides 4 levels of information to users:

  1. ERROR (Default): The only thing printed to the shell will be errors (and potentially data).
  2. WARNING: Additionally to the above, instances that may cause faulty data will be displayed.
     Specified using **-v**
  3. INFO: Additionally to the above, information about where data is read from and saved to will be displayed.
     Specified using **-vv**
  4. DEBUG: Additionally to the above, information about the program's progress will be displayed.
     Specified using **-vvv**

Additional information:

    * For more optional arguments, please see :ref:`advanced_arguments`.
    * For more information on save files and their formats, please see :ref:`save_format`
    * For information on the output, please see :ref:`output_format`

.. _area_information_note:

.. note::

    Enough information must be provided to make an area. Some common combinations of parameters are:

    1. **------pixel-size** and **------center** (defaults to the projection center if not provided)
    2. **------radius** and **------center** (defaults to the projection center if not provided)
    3. **------upper-left-extent** and **------pixel-size**
    4. **------area-extent**

    along with shape, which should automatically be found from **------displacement-data**.

.. note::

    * Pixels are referenced from their center.
    * velocity, v, and u are calculated using :ref:`loxodrome.sh<loxodrome.sh>`.
    * velocity is the speed and angle that the wind is moving when it reaches its new location.

Calculating wind_info::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000 --center 90 0 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ ./pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ ./pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000
    $ ./pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.py] Data saved to the directory
    /Desktop/in.flo_output_20190301_115959


For more examples of using wind_info.sh, please see :ref:`examples_of_wind_info.sh`.

.. _advanced_arguments:

Advanced arguments
------------------

.. |cs2cs_lu.png| image:: cs2cs_lu
   :target: _static/cs2cs_lu.png

.. |cs2cs_le.png| image:: cs2cs_le
   :target: _static/cs2cs_le.png

.. |cs2cs_lp.png| image:: cs2cs_lp
   :target: _static/cs2cs_lp.png

* **------save_directory** (**-s**): Directory in which to save the file containing data (also a directory) to.
  If the directory provided does not exist, then it is created. Defaults to a new directory by the name of
  the displacement file read appended with "_output_YYYYmmdd_HHMMSS" (the date and time when the script was ran),
  created where the script is ran
* **------precision**: Determines the number of decimal places to round printed data to. Saved data will always
  be the highest precision regardless of this input. Defaults to 2.
* **------from-lat-long**: Skips directly to using delta-time and two provided positions in order to find
  wind information (see :ref:`Using latitudes and longitudes directly<from_lat_long>`).
* **------projection**: Name of projection that the image is in
  (`cs2cs -lp <https://proj.org/apps/cs2cs.html?highlight=note#cmdoption-cs2cs-lp>`_: |cs2cs_lp.png|).
  Defaults to stere
* **------projection-ellipsoid**: ellipsoid of projection
  (`cs2cs -le <https://proj.org/apps/cs2cs.html?highlight=note#cmdoption-cs2cs-le>`_: |cs2cs_le.png|).
  Defaults to WGS84. Custom ellipsoids can be made, see.
* **------earth-ellipsoid**: ellipsoid of Earth
  (`cs2cs -le <https://proj.org/apps/cs2cs.html?highlight=note#cmdoption-cs2cs-le>`_: |cs2cs_le.png|).
  Defaults to WGS84. Custom ellipsoids can be made, see.
* **------shape**: Number of pixels in the y and x direction (height, width). If shape is not provided,
  it attempts to be found from **------displacement-data**
* **------upper-left-extent**: Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **------radius**: Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
* **------units**: Units that provided arguments should be interpreted as. This can be
  one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
  parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
  command (`<https://proj.org/apps/cs2cs.html?highlight=note#cmdoption-cs2cs-lu>`_: |cs2cs_lu.png|).
  Units are determined in the following priority:

  1. units expressed at the end of individual variables (see :ref:`Specifying input units<input_units>` for examples)
  2. units passed to ``--units`` (exluding center)
  3. meters (exluding center, which is degrees)
* **------area-extent**: Area extent as a list [y_ll, x_ll, y_ur, x_ur]

where

* **y_ll**: projection y coordinate of the lower left corner of the lower left pixel in meters
* **x_ll**: projection x coordinate of the lower left corner of the lower left pixel in meters
* **y_ur**: projection y coordinate of the upper right corner of the upper right pixel in meters
* **x_ur**: projection x coordinate of the upper right corner of the upper right pixel in meters

.. warning::

    The shape provided or found can alter the native shape of **------displacement-data**.


.. _output_format:

Output format
-------------

These are the output units for pywinds (Note: output units **cannot** be changed by the user):

    * area: See :ref:`content_of_wind_info.nc` or  :ref:`area print format<area_print>`
    * j: unitless
    * i: unitless
    * latitude: degrees
    * longitude: degrees
    * v: m/s
    * u: m/s
    * velocity speed: m/s
    * velocity angle: degrees

If j and i values are provided, then data is calculated at a single pixel:

::

    wind_info: [new_latitude, new_longitude, speed, angle, v, u]

    velocity: [speed, angle]

    vu: [v, u]

    lat_long: [latitude, longitude]

    displacements: [j_displacement, i_displacement]

If no j and i values are provided, then data is calculated at every pixel (n-rows, m-columns):

::

    wind_info:
        [[new_latitude_11, new_longitude_11, speed_11, angle_11, v_11, u_11],
         ...,
         [new_latitude_1m, new_longitude_1m, speed_1m, angle_1m, v_1m, u_1m],
         ...,
         [new_latitude_nm, new_longitude_nm, speed_nm, angle_nm, v_nm, u_nm]]

    vu:
        [[[v_11, ..., v_1m],
          ...,
          [v_n1, ..., v_nm]],
         [[u_11, ..., u_1m],
          ...,
          [u_n1, ..., u_nm]]]

    velocity:
        [[[speed_11, ..., speed_1m],
          ...,
          [speed_n1, ..., speed_nm]],
         [[angle_11, ..., angle_1m],
          ...,
          [angle_n1, ..., angle_nm]]]

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

.. _area_print:

Area is printed in a different format than it is saved::

    projection:
    lat-ts (degrees):
    lat-0 (degrees):
    long-0 (degrees):
    equatorial-radius (meters):
    eccentricity:
    inverse-flattening:
    shape:
    area-extent (degrees):
    pixel-size (meters):
    center (degrees):


.. _save_format:

Save format
-----------

wind_info.sh saves data to ::

    Text files: polar_stereographic.txt, j_displacement.txt, i_displacement.txt,
                new_latitude.txt, new_longitude.txt, old_latitude.txt, old_longitude.txt,
                v.txt, u.txt, speed.txt, angle.txt, wind_info.txt

    netcdf4 file: wind_info.nc


**All files are saved to --save_directory (see :ref:`advanced_arguments`)**

.. note::

    Data is saved in the order given by "Text files" above, which means that if not enough information
    was provided or an error occurs, data up to that point will be saved.

.. note::

    If re-saving data or saving data with the same **displacement-data** name, it is best to manually
    delete or rename the directory that old data was saved to. This ensures that the directory only
    contains that file's data (in conjunction with the above note).

Text files:

    * Text files are saved as comma separated files (except for polar-stereographic.txt
      which is the same format as it is in wind_info.nc). Numbers are rounded to 2 decimal places.

    * For examples of what the text files looks like, please see :ref:`content_of_text_files`.

wind_info.nc:

    * wind_info.nc is a netcdf4 file saved using 32-bit floats which follows
      `CF-1.7 conventions <http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apf.html>`_.

    * Each variable listed under "Text files" at the top of this section is saved to wind_info.nc by the same
      name as their .txt counterparts.

    * For an example of what wind_info.nc looks like, please see :ref:`content_of_wind_info.nc`.

Additional utility methods
--------------------------

None of these functions can save data, thus they **do not** have the **------print**/**-p** argument.
They have similar or identical arguments to wind_info.sh

* **vu.sh**: Prints just the v and u components of the wind. Same arguments as wind_info.sh

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/vu.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
    [36.78, -36.46]


* **velocity.sh**: Prints just the velocity of the wind. Same arguments as wind_info.sh

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/velocity.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
    [51.78, 315.25]



* **lat_long.sh**: Prints just the latitude and longitude of the pixels. If displacements data is provided,
  then old_latitude and old_longitude are calculated, else new_latitude and new_longitude are calculated.
  Same arguments as wind_info.sh but does not take **delta-time** as an argument.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/lat_long.sh 60 90 0 -j 0 -i 0 --pixel-size 4000 --shape 1000 1000
    [63.36, -135.0]
    $ ./pywinds/lat_long.sh 60 90 0 -j 0 -i 0 --pixel-size 4000 --displacement-data in.flo
    [61.38, -130.77]


* **displacements.sh**: Prints just the j and i displacements of the pixels. Does not take **delta-time**
  as an argument. All other required arguments for wind_info.sh are optional arguments.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/displacements.sh -j 0 -i 0
    [-2.53, 76.8]


* **area.sh**: Prints information about the projection given. Same arguments as
  wind_info.sh but does not take **delta-time** as an argument.

::

    $ pwd
    /Desktop
    $ ls
    in.flo	    pywinds
    $ ./pywinds/area.sh 60 90 0 --pixel-size 4000
    projection: stere
    lat-ts: 60.0
    lat-0: 90.0
    long-0: 0.0
    equatorial-radius: 6378137.0
    eccentricity: 0.08
    inverse-flattening: 298.26
    shape: [1000, 1000]
    area-extent: [63.33, -45.0, 63.33, 135.0]
    pixel-size: [4000.0, 4000.0]
    center: [90.0, 0.0]


You can use area.sh on a file containing displacements to see what shape it is,
even if the area is not completely defined, as shown in :ref:`advanced_examples`.

.. _loxodrome.sh:

* **loxodrome.sh**: Prints the distance, forward bearing, and back bearing between
  two points on the earth provided in latitude and longitude as calculated from the rhumb line.
  This is the angle and distance one would travel if direction is continuously updated.

::

    $ ls
    pywinds
    $ ./pywinds/loxodrome.sh 60 130 61 131
    [124234.33, 26.25, 206.25]

The inverse may be set to True in order to find a given latitude and longitude if given a starting
position, distance, and forward bearing to the new position.

::

    $ ls
    pywinds
    $ ./pywinds/loxodrome.sh 60 130 124234.33 26.25 --inverse
    [61.0, 131.0, 206.25]


* **geodesic.sh**: Prints the shortest distance, initial bearing, and back bearing between
  two points on the earth provided in latitude and longitude as calculated from the great circle arc.
  This is the angle and distance one would travel if walking in a straight line without adjusting their course.

::

    $ ls
    pywinds
    $ ./pywinds/geodesic.sh 60 130 61 131
    [124233.13, 25.82, 206.69]

The inverse may be set to True in order to find a given latitude and longitude if given a starting
position, distance, and initial bearing to the new position.

::

    $ ls
    pywinds
    $ ./pywinds/geodesic.sh 60 130 124233.13 25.82 --inverse
    [61.0, 131.0, 206.69]


* **position_to_pixel.sh**: Returns the pixel that a provided latitude and longitude correspond to on a user
  provided area.

::

    $ ls
    in.flo	    pywinds
    $ ./pywinds/position_to_pixel.sh 60 90 0 80 45 --pixel-size 4 km
    [684.18, 684.18]

Understanding error messages from scripts
-----------------------------------------

All error messages follow one of these two formats::

    1) traceback
       error

    2) usage
       error


The first implies that the command line was understood, but an error occurred down the line due to incorrect
data, not enough information provided, etc.

The second implies that there was a problem reading the command line: not all positional arguments provided,
incorrect formatting, etc.

.. note::

    Remember that you can always enter **-h** or **------help** for more usage detail.

Please see :ref:`error_messages` in Examples.


