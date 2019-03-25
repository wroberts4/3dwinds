Examples
========

.. _examples_of_wind_info.sh:

Examples of wind_info.sh
------------------------

Having multiple files in run directory::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 -vv --no-save
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/test.flo
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 --center 90 0 -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/test.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.py] Data saved to the directory
    /Desktop/test.flo_output
    [INFO: 2019-03-01 12:00:08 : pywinds.wind_functions] Reading displacements from
    /Desktop/in.flo
    [INFO: 2019-03-01 12:00:16 : wind_info.py] Data saved to the directory
    /Desktop/in.flo_output


.. note::

    If **displacement-data** is not provided, then every file ending in ".flo" where the script was ran is read.

.. note::

    In this case, **wind_info.sh** saves all files mentioned in :ref:`save_format`
    to /Desktop/test.flo_output and /Desktop/in.flo_output.

Specifying one file to run::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 --displacement-data in.flo --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 --center 90 0
      --displacement-data path_to_other_directory/in.flo
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000 --center 90 0
      --displacement-data path_to_other_directory/in.flo -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    path_to_other_directory/in.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.py] Data saved to the directory
    /Desktop/in.flo_output


Specifying multiple files to run::

    $ pwd
    /Desktop
    $ ls
    in.flo        windtest.flo        windtest2.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 --displacement-data \*test*.flo -vv --no-save
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest.flo
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest2.flo
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --pixel-size 4000
      --center 90 0 --displacement-data \*test*.flo -vv
    [INFO: 2019-03-01 12:00:00 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest.flo
    [INFO: 2019-03-01 12:00:08 : wind_info.py] Data saved to the directory
    /Desktop/windtest.flo_output
    [INFO: 2019-03-01 12:00:08 : pywinds.wind_functions] Reading displacements from
    /Desktop/windtest2.flo
    [INFO: 2019-03-01 12:00:16 : wind_info.py] Data saved to the directory
    /Desktop/windtest2.flo_output


Altering spheroids::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 --projection-spheroid sphere --no-save
    [63.26, -135.0, 51.93, 315.2, 36.85, -36.59]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000 --center 90 0
      --projection-spheroid sphere --earth-spheroid sphere --no-save
    [63.26, -135.0, 51.77, 315.24, 36.76, -36.46]


Using other advanced args::

    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --radius 2000000 2000000 --center 90 0 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --upper-left-extent 2000000 -2000000 --center 90 0 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --area-extent -2000000 -2000000 2000000 2000000 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --upper-left-extent 2000000 -2000000
      --radius 2000000 2000000 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --center 90 0
      --pixel-size 4000 --shape 10000 100 -v --no-save
    [WARNING: 2019-03-01 12:00:00 : pywinds.wind_functions] Shape found
    from area or provided by user does not match the shape of the file:
    (10000, 100) vs (1000, 1000)
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]


Using units::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4000 --center 90 0 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4 --center 90 0 --units km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4 km --center 90 0 --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4 --center 0 0 m  --units km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4 km --center 0 0 m --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --pixel-size 4000 m --center 90 0 --units km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --upper-left-extent 2000 -2000 km
      --radius 2000 2000 km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --upper-left-extent 2000 -2000
      --radius 2000 2000 --units km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0
      --upper-left-extent 63.335 -135 deg
      --radius 2000 2000 --units km --no-save
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]


.. note::

    **center**'s units default to degrees and are not affected by the **units** option.


Shuffling order of arguments/options::


    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds

    $ pywinds/wind_info.sh --center 90 0 --j 0 --i 0
      --no-save --pixel-size 4000 --i 0 60 90 0 100
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]
    $ pywinds/wind_info.sh --center 90 0 60 --j 0 90 --i 0
      0 --no-save --pixel-size 4000 4000 100 --i 0
    [63.36, -135.0, 51.8, 315.24, 36.78, -36.47]


.. note::

    For **pixel-size** to have positional arguments after it, it must be specified using two numbers
    (or else **pixel-size** would interpret the second number as input since **pixel-size**
    can take one or two numbers as arguments).

**displacement-data** can also be a list::


    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --j 0 --i 0 --pixel-size 4000
      --center 90 0 --displacement-data [[[1,2],[3,4]],[[5,6],[7,8]]] --no-save
    [89.97, -135.0, 3.76, 341.58, 3.57, -1.19]

.. _content_of_wind_info.nc:

Content of wind_info.nc
-----------------------

::

    $ pwd
    /Desktop/pywinds/in.flo_output
    $ ls
    angle.txt		    new_latitude.txt	old_longitude.txt	    u.txt			   wind_info.txt
    i_displacement.txt	new_longitude.txt	polar_stereographic.txt	v.txt
    j_displacement.txt	old_latitude.txt	speed.txt		        wind_info.nc
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
            angle:standard_name = "wind_from_direction" ;
            angle:grid_mapping = "polar_stereographic" ;
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
    300.92,399.48,494.96
    589.80,681.97,771.00


u.txt::

    0.00,-39.86,-158.31
    118.10,467.99,-579.49
    458.61,791.67,1188.80


speed.txt::

    0.00,108.36,255.45
    323.26,615.31,762.10
    747.11,1044.90,1416.93


angle.txt::

    90.00,338.42,321.70
    21.43,49.52,310.50
    37.87,49.26,57.03


wind_info.txt::

    89.95,-135.00,0.00,90.00,0.00,0.00
    89.96,180.00,108.36,338.42,100.76,-39.86
    89.95,135.00,255.45,321.70,200.48,-158.31
    89.96,-90.00,323.26,21.43,300.92,118.10
    90.00,0.00,615.31,49.52,399.48,467.99
    89.96,90.00,762.10,310.50,494.96,-579.49
    89.95,-45.00,747.11,37.87,589.80,458.61
    89.96,0.00,1044.90,49.26,681.97,791.67
    89.95,45.00,1416.93,57.03,771.00,1188.80


.. _advanced_examples:

Advanced examples
-----------------

Getting shape of displacement file using area.sh::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/area.py 60 90 0
    projection: stere
    lat-ts: 60
    lat-0: 90
    long-0: 0
    equatorial-radius: 6378137.0
    eccentricity: 0.081819
    inverse-flattening: 298.26
    shape: [1000, 1000]
    area-extent: None
    pixel-size: None
    center: None


.. _error_messages:

Error and usage messages
------------------------

If not enough information is provided to a script, this kind of error will be displayed::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/wind_info.sh 60 90 0 100 --center 90 0 --i 0 --j 0 --no-save

    Traceback (most recent call last):
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wrapper_utils.py",
    line 184, in run_script
        output = output_format(func(*args, **kwargs), kwargs)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py",
    line 867, in wind_info
        earth_spheroid=earth_spheroid, no_save=no_save)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py",
    line 414, in _compute_velocity
        no_save=no_save)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py",
    line 379, in _compute_vu
        no_save=no_save)
      File "pywinds/env/lib/python3.7/site-packages/pywinds/wind_functions.py",
    line 327, in _compute_lat_long
        raise ValueError('Not enough information provided to create an area for projection')
    ValueError: Not enough information provided to create an area for projection


If incorrect commands were given::

    $ pywinds/wind_info.sh 60 90 0 --pixel-size 4000 --center 90 0
    usage: wind_info.py [-h] [--center y x [units]] [--pixel-size dy [dx] [units]]
                        [--displacement-data filename] [--j int] [--i int]
                        [--no-save] [--units str]
                        [--upper-left-extent y x [units]]
                        [--radius dy dx [units]]
                        [--area-extent y_ll x_ll y_ur x_ur [units]]
                        [--shape height width] [--projection str]
                        [--projection-spheroid str] [--earth-spheroid str]
                        lat-ts lat-0 long-0 delta-time
    wind_info.py: error: the following arguments are required: delta-time


The help message for wind_info.sh::

    $ pywinds/wind_info.sh -h
    usage: wind_info.py [-h] [--center y x [units]] [--pixel-size dy [dx] [units]]
                        [--displacement-data filename] [--j int] [--i int]
                        [--no-save] [--units str]
                        [--upper-left-extent y x [units]]
                        [--radius dy dx [units]]
                        [--area-extent y_ll x_ll y_ur x_ur [units]]
                        [--shape height width] [--projection str]
                        [--projection-spheroid str] [--earth-spheroid str]
                        lat-ts lat-0 long-0 delta-time

    positional arguments:
      lat-ts                projection latitude of true scale
      lat-0                 projection latitude of origin
      long-0                projection central meridian
      delta-time            amount of time that separates both files in minutes

    optional arguments:
      -h, --help            show this help message and exit
      --center y x [units]
                            projection y and x coordinate of the center of area.
                            Default: lat long
      --pixel-size dy [dx] [units]
                            projection size of pixels in the y and x direction.If
                            pixels are square, i.e. dy = dx, then only one value
                            needs to be entered
      --displacement-data filename
                            filename or list containing displacements
      --j int               row to run calculations on
      --i int               column to run calculations on
      --no-save             print data to shell without saving
      --units str           units that all provided arguments that take units
                            (except center) should be interpreted as
      --upper-left-extent y x [units]
                            projection y and x coordinates of the upper left
                            corner of the upper left pixel
      --radius dy dx [units]
                            projection length from the center to the left/rightand
                            top/bottom outer edges
      --area-extent y_ll x_ll y_ur x_ur [units]
                            area extent in projection space:
                            lower_left_y,lower_left_x, upper_right_y,
                            upper_right_x
      --shape height width  number of pixels in the y and x direction
      --projection str      name of projection that the image is in
      --projection-spheroid str
                            spheroid of projection
      --earth-spheroid str  spheroid of Earth


.. note::
    Brackets around an argument means that argument is optional.
