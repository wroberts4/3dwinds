Examples
========

.. _examples_of_wind_info.sh:

Examples of wind_info.sh
------------------------

Changing the center of area::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000 --center 60 -45 -p
    [50.62, -86.47, 48.28, 1.59, 48.26, 1.34]


.. note::

    **------center** defaults to (**lat-0**, **long-0**) if area is incomplete and doesn't override user provided data.

Having multiple files in run directory::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000 -vv -p
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/test.flo
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/test.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.sh] Data saved to the directory
    /Desktop/test.flo_output_20190301_115959
    [INFO: 2019-03-01 12:00:08 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [INFO: 2019-03-01 12:00:16 : wind_info.sh] Data saved to the directory
    /Desktop/in.flo_output_20190301_115959


.. note::

    When **------displacement-data** is not provided, then every file ending in ".flo" where the script was ran is read.

.. note::

    In this case, **wind_info.sh** saves all files mentioned in :ref:`save_format`
    to /Desktop/test.flo_output_20190301_115959 and /Desktop/in.flo_output_20190301_115959.

Specifying a displacement file to read::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --displacement-data in.flo -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000
      --displacement-data path_to_other_directory/in.flo
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000
      --displacement-data path_to_other_directory/in.flo -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    path_to_other_directory/in.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.sh] Data saved to the directory
    /Desktop/in.flo_output_20190301_115959


Specifying multiple displacement files to read::

    $ pwd
    /Desktop
    $ ls
    in.flo        windtest.flo        windtest2.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --displacement-data \*test*.flo -vv -p
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest.flo
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest2.flo
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000
      --displacement-data \*test*.flo -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.sh] Data saved to the directory
    /Desktop/windtest.flo_output_20190301_115959
    [INFO: 2019-03-01 12:00:08 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest2.flo
    [INFO: 2019-03-01 12:00:16 : wind_info.sh] Data saved to the directory
    /Desktop/windtest2.flo_output_20190301_115959


Specifying save directory::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 -vv -s new_directory
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.sh] Data saved to the directory
    /Desktop/new_directory/in.flo_output_20190301_115959
    [INFO: 2019-03-01 12:00:08 : pywinds.wind_functions] Reading displacements from
    /Desktop/test.flo
    [INFO: 2019-03-01 12:00:16 : wind_info.sh] Data saved to the directory
    /Desktop/new_directory/test.flo_output_20190301_115959

Altering ellipsoids::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --projection-ellipsoid sphere -p
    [63.26, -135.0, 51.92, 315.21, 36.85, -36.58]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --earth-ellipsoid sphere -p
    [63.36, -135.0, 51.63, 315.29, 36.69, -36.32]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --projection-ellipsoid sphere --earth-ellipsoid sphere -p
    [63.26, -135.0, 51.76, 315.25, 36.76, -36.44]


.. _input_units:

Specifying input units::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4 --units km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4 km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4 --center 0 0 m  --units km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4 km --center 0 0 m -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4000 m --units km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --upper-left-extent 2000 -2000 km
      --radius 2000 2000 km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --upper-left-extent 2000 -2000
      --radius 2000 2000 --units km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --upper-left-extent 63.335 -135 deg
      --radius 2000 2000 --units km -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]


.. note::

    **center**'s units default to degrees and are not affected by the **units** option.

Using other advanced args::

    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --radius 2000000 2000000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --upper-left-extent 2000000 -2000000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --area-extent -2000000 -2000000 2000000 2000000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --upper-left-extent 2000000 -2000000
      --radius 2000000 2000000 -p
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0
      --pixel-size 4000 --shape 10000 100 -p
    [WARNING: 2019-03-01 12:00:00 : pywinds.wind_functions] Shape found
    from area or provided by user does not match the shape of the file:
    (10000, 100) vs (1000, 1000)
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]


Shuffling order of arguments/options::


    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds

    $ pywinds/wind_info.sh -j 0 -i 0
      -p --pixel-size 4000 -i 0 60 90 0 100
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]
    $ pywinds/wind_info.sh -j 0 60 90 -i 0
      0 -p --pixel-size 4000 4000 100 -i 0
    [63.36, -135.0, 51.78, 315.25, 36.78, -36.46]


.. note::

    For **------pixel-size** to have positional arguments after it, it must be specified using two numbers
    or with units. This is because **------pixel-size** would interpret the second number as input since
    **------pixel-size** can take one or two numbers as arguments).

**------displacement-data** can also be a list ([j_displacement,i_displacement] in row-major format)::


    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -j 0 -i 0 --pixel-size 4000
      --displacement-data [[1,2,3,4],[5,6,7,8]] -p
    [89.97, -135.0, 3.68, 346.03, 3.57, -0.89]

.. _content_of_wind_info.nc:

Content of wind_info.nc
-----------------------

::

    $ pwd
    /Desktop/pywinds/in.flo_output_20190301_115959
    $ ls
    angle.txt		old_latitude.txt	v.txt
    i_displacement.txt	old_longitude.txt	wind_info.nc
    j_displacement.txt	polar_stereographic.txt	wind_info.txt
    new_latitude.txt	speed.txt
    new_longitude.txt	u.txt
    $ ncdump -h wind_info.nc
    netcdf wind_info {
    dimensions:
        y = 1000 ;
        x = 1000 ;
        yx = 1000000 ;
        vars = 6 ;
    variables:
        float polar_stereographic ;
            polar_stereographic:_FillValue = NaNf ;
            polar_stereographic:straight_vertical_longitude_from_pole = -180. ;
            polar_stereographic:latitude_of_projection_origin = 90. ;
            polar_stereographic:scale_factor_at_projection_origin = 0.933069071736357 ;
            polar_stereographic:standard_parallel = 60. ;
            polar_stereographic:resolution_at_standard_parallel = 4000. ;
            polar_stereographic:false_easting = 0. ;
            polar_stereographic:false_northing = 0. ;
            polar_stereographic:semi_major_axis = 6378137. ;
            polar_stereographic:semi_minor_axis = 6356752.31424518 ;
            polar_stereographic:inverse_flattening = 298.257223563 ;
        float j_displacement(y, x) ;
            j_displacement:_FillValue = NaNf ;
            j_displacement:standard_name = "divergence_of_wind" ;
            j_displacement:description = "vertical pixel displacement at each pixel" ;
            j_displacement:grid_mapping = "polar_stereographic" ;
        float i_displacement(y, x) ;
            i_displacement:_FillValue = NaNf ;
            i_displacement:standard_name = "divergence_of_wind" ;
            i_displacement:description = "horizontal pixel displacement at each pixel" ;
            i_displacement:grid_mapping = "polar_stereographic" ;
        float new_latitude(y, x) ;
            new_latitude:_FillValue = NaNf ;
            new_latitude:standard_name = "latitude" ;
            new_latitude:grid_mapping = "polar_stereographic" ;
            new_latitude:units = "degrees" ;
        float new_longitude(y, x) ;
            new_longitude:_FillValue = NaNf ;
            new_longitude:standard_name = "longitude" ;
            new_longitude:grid_mapping = "polar_stereographic" ;
            new_longitude:units = "degrees" ;
        float old_latitude(y, x) ;
            old_latitude:_FillValue = NaNf ;
            old_latitude:standard_name = "latitude" ;
            old_latitude:grid_mapping = "polar_stereographic" ;
            old_latitude:units = "degrees" ;
        float old_longitude(y, x) ;
            old_longitude:_FillValue = NaNf ;
            old_longitude:standard_name = "longitude" ;
            old_longitude:grid_mapping = "polar_stereographic" ;
            old_longitude:units = "degrees" ;
        float v(y, x) ;
            v:_FillValue = NaNf ;
            v:standard_name = "northward_wind" ;
            v:grid_mapping = "polar_stereographic" ;
            v:units = "m/s" ;
        float u(y, x) ;
            u:_FillValue = NaNf ;
            u:standard_name = "eastward_wind" ;
            u:grid_mapping = "polar_stereographic" ;
            u:units = "m/s" ;
        float speed(y, x) ;
            speed:_FillValue = NaNf ;
            speed:standard_name = "wind_speed" ;
            speed:grid_mapping = "polar_stereographic" ;
            speed:units = "m/s" ;
        float angle(y, x) ;
            angle:_FillValue = NaNf ;
            angle:standard_name = "wind_to_direction" ;
            angle:grid_mapping = "polar_stereographic" ;
            angle:description = "Forward bearing of rhumb line" ;
            angle:units = "degrees" ;
        float wind_info(yx, vars) ;
            wind_info:_FillValue = NaNf ;
            wind_info:standard_name = "wind_speed" ;
            wind_info:description = "new_lat, new_long, speed, angle, v, u" ;
            wind_info:grid_mapping = "polar_stereographic" ;

    // global attributes:
            :Conventions = "CF-1.7" ;
    }


.. _content_of_text_files:

Content of text files
---------------------

To reduce space, these examples are with a different (smaller) data set than the data used above.

polar_stereographic.txt::

    straight_vertical_longitude_from_pole: -180.0
    latitude_of_projection_origin: 90.0
    scale_factor_at_projection_origin: 0.93
    standard_parallel: 60.0
    resolution_at_standard_parallel: 4000.0
    false_easting: 0.0
    false_northing: 0.0
    semi_major_axis: 6378137.0
    semi_minor_axis: 6356752.31
    inverse_flattening: 298.26


j_displacement.txt::

    0.00,100.00,200.00
    300.00,400.00,500.00
    600.00,700.00,800.00


i_displacement.txt::

    0.00,100.00,200.00
    300.00,400.00,500.00
    600.00,700.00,800.00


new_latitude.txt::

    89.95,89.96,89.95
    89.96,90.00,89.96
    89.95,89.96,89.95


new_longitude.txt::

    -135.00,180.00,135.00
    -90.00,0.00,90.00
    -45.00,0.00,45.00


old_latitude.txt::

    89.95,84.55,79.18
    73.79,68.53,63.36
    58.24,53.29,48.48


old_longitude.txt::

    -135.00,-135.29,-135.29
    -134.90,-135.00,-135.06
    -134.90,-134.96,-135.00


v.txt::

    0.00,100.76,200.48
    300.90,399.44,494.88
    589.67,681.78,770.76


u.txt::

    0.00,-15.86,-59.25
    38.97,0.00,-177.67
    144.64,232.85,362.30


speed.txt::

    0.00,102.00,209.05
    303.41,399.44,525.81
    607.15,720.45,851.66


angle.txt::

    0.00,351.05,343.54
    7.38,0.00,340.25
    13.78,18.86,25.18


wind_info.txt::

    89.95,-135.00,0.00,0.00,0.00,0.00
    89.96,180.00,102.00,351.05,100.76,-15.86
    89.95,135.00,209.05,343.54,200.48,-59.25
    89.96,-90.00,303.41,7.38,300.90,38.97
    90.00,0.00,399.44,0.00,399.44,0.00
    89.96,90.00,525.81,340.25,494.88,-177.67
    89.95,-45.00,607.15,13.78,589.67,144.64
    89.96,0.00,720.45,18.86,681.78,232.85
    89.95,45.00,851.66,25.18,770.76,362.30


.. _advanced_examples:

Advanced examples
-----------------

Getting shape of displacement file using area.sh::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/area.sh 60 90 0
    projection: stere
    lat-ts: 60.0
    lat-0: 90.0
    long-0: 0.0
    equatorial-radius: 6378137.0
    eccentricity: 0.08
    inverse-flattening: 298.26
    shape: [1000, 1000]
    area-extent: None
    pixel-size: None
    center: None


.. _error_messages:

Error and usage messages
------------------------

If incorrect commands were given::

    $ pywinds/wind_info.sh 60 90 0 --pixel-size 4000
    usage: wind_info.sh [-h] [-j int] [-i int] [-p] [-s path_name]
                        [--earth-ellipsoid str] [--center y x [units]]
                        [--pixel-size dy [dx] [units]] [--displacement-data filename]
                        [--units str]
                        [--upper-left-extent y x [units]]
                        [--radius dy dx [units]]
                        [--area-extent y_ll x_ll y_ur x_ur [units]]
                        [--shape height width] [--projection str]
                        [--projection-ellipsoid str] [-v]
                        lat-ts lat-0 long-0 delta-time
    wind_info.sh: error: the following arguments are required: delta-time


If not enough information is provided to a script, this kind of
error will be displayed (see :ref:`common combinations of area information<area_information_note>`)::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 -i 0 -j 0 -p
    Traceback (most recent call last):
      File "<stdin>", line 35, in <module>
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wrapper_utils.py",
      line 223, in run_script
        output = output_format(func(*args, **kwargs), **kwargs)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py", line 1046, in wind_info
        save_directory=save_directory)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py", line 451, in _compute_vu
        save_directory=save_directory)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py", line 418, in _compute_velocity
        no_save=no_save, save_directory=save_directory)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py", line 365, in _compute_lat_long
        raise ValueError('Not enough information provided to create an area for projection')
    ValueError: Not enough information provided to create an area for projection


If an invalid area is created (in this case the lower left corner is the upper right corner)::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/area.sh 60 90 0 --upper-left-extent 60 45 deg -v
    [WARNING: 2019-07-08 09:02:54 : pywinds.wind_functions] invalid area_extent.
      Lower left corner is above or to the right of the upper right corner:
    [59.99999999999866, 135.00000000000003, 59.99999999999866, -44.99999999999999]
    projection: stere
    lat-ts: 60.0
    lat-0: 90.0
    long-0: 0.0
    equatorial-radius: 6378137.0
    eccentricity: 0.08
    inverse-flattening: 298.26
    shape: [1000, 1000]
    area-extent: [60.0, 135.0, 60.0, -45.0]
    pixel-size: [-4521.39, -4521.39]
    center: [90.0, 0.0]


.. note::
    Brackets around an argument means that argument is optional.
