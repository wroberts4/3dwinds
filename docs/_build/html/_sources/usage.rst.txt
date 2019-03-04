How to use pywinds
==================

velocity.sh
-----------

When saved to a file, the output is in row-column format as data-type float32.

Required arguments:

* **lat_0**: Normal latitude of projection
* **lon_0**: Normal longitude of projection

optional arguments:

* **units**: Units that provided arguments should be interpreted as
* **shape**: Number of pixels in the y and x direction following row-column format (height, width)
* **area_extent**: Area extent as a tuple (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
* **upper_left_extent**: y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **center**: y and x coordinate of the center of projection (y, x)
* **resolution**: Size of pixels in the y and x direction (dy, dx)
* **radius**: Length from the center to the top/bottom and left/right outer edges (dy, dx)
* **displacement_data**: File or list containing displacements
* **j**: y pixel to compute displacements at
* **i**: x pixel to compute displacements at
* **save_data**: When true, saves velocity to "speed" and "angle" under a new output
  directory by the name of the displacement file_name appended with "output"

::

    (pywinds) ella:pywinds/velocity.py 60 0 100 --j 0 --i 0
     --pixel_size 4:km --center 90,0 --no_save
    [42.33, 317.58]

    (pywinds) ella:pywinds/velocity.py 60 0 100
     --pixel_size 4:km --center 90,0

vu.sh
-----

Finds vu

Required arguments:

* **lat_0**: Normal latitude of projection
* **lon_0**: Normal longitude of projection

optional arguments:

* **units**: Units that provided arguments should be interpreted as
* **shape**: Number of pixels in the y and x direction following row-column format (height, width)
* **area_extent**: Area extent as a tuple (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
* **upper_left_extent**: y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **center**: y and x coordinate of the center of projection (y, x)
* **resolution**: Size of pixels in the y and x direction (dy, dx)
* **radius**: Length from the center to the top/bottom and left/right outer edges (dy, dx)
* **displacement_data**: File or list containing displacements
* **j**: y pixel to compute displacements at
* **i**: x pixel to compute displacements at
* **save_data**: When true, saves vu to "v" and "u" under a new output
  directory by the name of the displacement file_name appended with "output"

::

    (pywinds) ella:pywinds/vu.py 60 0 100 --j 0 --i 0
     --pixel_size 4:km --center 90,0 --no_save
    [31.25, -28.55]

    (pywinds) ella:pywinds/vu.py 60 0 100
     --pixel_size 4:km --center 90,0

lat_long.sh
-----------

Finds lat_long

Required arguments:

* **lat_0**: Normal latitude of projection
* **lon_0**: Normal longitude of projection

optional arguments:

* **units**: Units that provided arguments should be interpreted as
* **shape**: Number of pixels in the y and x direction following row-column format (height, width)
* **area_extent**: Area extent as a tuple (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
* **upper_left_extent**: y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **center**: y and x coordinate of the center of projection (y, x)
* **resolution**: Size of pixels in the y and x direction (dy, dx)
* **radius**: Length from the center to the top/bottom and left/right outer edges (dy, dx)
* **displacement_data**: File or list containing displacements
* **j**: y pixel to compute displacements at
* **i**: x pixel to compute displacements at
* **save_data**: When true, saves lat_long to "latitude" and "longitude" under a new output
  directory by the name of the displacement file_name appended with "output"

::

    (pywinds) ella:pywinds/lat_long.py 60 0 --j 0 --i 0
     --pixel_size 4:km --center 90,0 --shape 1000,1000 --no_save
    [67.62, -137.17]

    (pywinds) ella:pywinds/lat_long.py 60 0 --j 0 --i 0
     --pixel_size 4:km --center 90,0 --displacement_data "'*.flo'" --no_save
    [65.94, -133.28]

    (pywinds) ella:pywinds/lat_long.py 60 0
     --pixel_size 4:km --center 90,0 --displacement_data "'*.flo'"

displacements.sh
----------------

Finds displacements

optional arguments:

* **lat_0**: Normal latitude of projection
* **lon_0**: Normal longitude of projection
* **units**: Units that provided arguments should be interpreted as
* **shape**: Number of pixels in the y and x direction following row-column format (height, width)
* **area_extent**: Area extent as a tuple (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
* **upper_left_extent**: y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **center**: y and x coordinate of the center of projection (y, x)
* **resolution**: Size of pixels in the y and x direction (dy, dx)
* **radius**: Length from the center to the top/bottom and left/right outer edges (dy, dx)
* **displacement_data**: File or list containing displacements
* **j**: y pixel to compute displacements at
* **i**: x pixel to compute displacements at
* **save_data**: When true, saves displacements to "j_displacements" and "i_displacements"
  under a new output directory by the name of the displacement file_name appended with "output"

::

    (pywinds) ella:pywinds/displacements.py --j 0 --i 0 --no_save
     [-2.53, 76.8]

    (pywinds) ella:pywinds/displacements.py --j 1 --i 0 --no_save --shape 100,10000
     [-3.03, 79.19]

    (pywinds) ella:pywinds/displacements.py --j 1 --i 0 --no_save --pixel_size 4
     --center 90,0 --radius 200,20000 --units km
     [-3.03, 79.19]

    (pywinds) ella:pywinds/displacements.py

area.sh
-------

Finds area

Required arguments:

* **lat_0**: Normal latitude of projection
* **lon_0**: Normal longitude of projection

optional arguments:

* **units**: Units that provided arguments should be interpreted as
* **shape**: Number of pixels in the y and x direction following row-column format (height, width)
* **area_extent**: Area extent as a tuple (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
* **upper_left_extent**: y and x coordinates of the upper left corner of the upper left pixel (y, x)
* **center**: y and x coordinate of the center of projection (y, x)
* **resolution**: Size of pixels in the y and x direction (dy, dx)
* **radius**: Length from the center to the top/bottom and left/right outer edges (dy, dx)
* **displacement_data**: File or list containing displacements

::

    (pywinds) ella:pywinds/area.py 60 0 --pixel_size 4:km --center 90,0
    projection data: {'lat_0': 60.0, 'lon_0': 0.0, 'proj': 'stere', 'a': 6378137.0, 'f': 0.0033528106647474805}
    area_extent: (5429327.917104956, 2000000.0000000785, 1429327.9172506747, -2000000.0000000785)
    shape: (1000, 1000)
    pixel_size: (3999.999999854281, 4000.000000000157)
    center: (3429327.917177815, 0.0)
