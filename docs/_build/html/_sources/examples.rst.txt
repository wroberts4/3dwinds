Examples
========

Having multiple file in run directory::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --pixel_size 4000
      --center 90,0 --no_save
    Reading displacements from: /Desktop/test.flo
    [67.62, -137.17, 42.33, 317.58, 31.25, -28.55]
    Reading displacements from: /Desktop/in.flo
    [67.62, -137.17, 42.33, 317.58, 31.25, -28.55]
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --shape 100,10000
      --pixel_size 4000 --center 90,0 --no_save
    Reading displacements from: /Desktop/test.flo
    [-17.39, -112.04, 14.3, 19.19, 13.51, 4.7]
    Reading displacements from: /Desktop/in.flo
    [-17.39, -112.04, 14.3, 19.19, 13.51, 4.7]
    $ pywinds/wind_info.sh 60 0 100 --pixel_size 4000 --center 90,0
    Reading displacements from: /Desktop/test.flo
    Saving wind_info to:
    /Desktop/test.flo_output/wind_info.txt
    /Desktop/test.flo_output/wind_info.hdf5
    Reading displacements from: /Desktop/test.flo
    Saving wind_info to:
    /Desktop/in.flo_output/wind_info.txt
    /Desktop/in.flo_output/wind_info.hdf5

Specifying one file to run::

    $ pwd
    /Desktop
    $ ls
    in.flo        test.flo        pywinds
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0
      --displacement_data in.flo --no_save
    [67.62, -137.17, 42.33, 317.58, 31.25, -28.55]

Altering spheroids::

    $ pwd
    /Desktop
    $ ls
    in.flo        pywinds
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0
      --image_geod sphere --no_save
    [67.5, -137.16, 42.54, 317.54, 31.38, -28.72]
    $ pywinds/velocity.sh 60 0 100 --j 0 --i 0 --pixel_size 4000 --center 90,0
      --image_geod sphere --earth_geod sphere --no_save
    [67.5, -137.16, 42.4, 317.57, 31.29, -28.61]


