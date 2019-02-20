Examples of using pywinds
=========================

.. |test| image:: ../_build/html/_images/base_examples.png

|test|

::

    ella:pywinds wroberts$ pwd
    /Users/wroberts/Documents/pywinds/pywinds
    ella:pywinds wroberts$ source activate pywinds
    (pywinds) ella:pywinds wroberts$ ./velocity.sh 60 0 test/test_files/test_data_one.flo --j 0 --i 0 --pixel_size 4000 --center 90,0
    [42.57496915645635, 312.6840984969709]
    (pywinds) ella:pywinds wroberts$ ./vu.sh 60 0 test/test_files/test_data_one.flo --j 0 --i 0 --pixel_size 4000 --center 90,0
    [28.863942177010685, -31.296978139676572]
    (pywinds) ella:pywinds wroberts$ ./lat_long.sh 60 0 --shape 1000,1000 --j 0 --i 0 --pixel_size 4000 --center 90,0
    [67.62332747031272, -137.1736645853314]
    (pywinds) ella:pywinds wroberts$ ./lat_long.sh 60 0 --displacement_data test/test_files/test_data_one.flo --j 0 --i 0 --pixel_size 4000 --center 90,0
    [69.1759713115284, -141.7426590655602]
    (pywinds) ella:pywinds wroberts$ ./displacements.sh test/test_files/test_data_one.flo --j 0 --i 0
    [-2.529944896697998, 76.80111694335938]
    (pywinds) ella:pywinds wroberts$ ./area.sh 60 0 --center 90,0 --pixel_size 4000 --shape 1000,1000
    Area ID: pywinds
    Description: pywinds
    Projection: {'a': '6378137.0', 'f': '0.0033528106647474805', 'lat_0': '60.0', 'lon_0': '0.0', 'proj': 'stere'}
    Number of columns: 1000
    Number of rows: 1000
    Area extent: (5429327.9172, 2000000.0, 1429327.9172, -2000000.0)

