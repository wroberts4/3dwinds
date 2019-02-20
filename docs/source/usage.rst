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
