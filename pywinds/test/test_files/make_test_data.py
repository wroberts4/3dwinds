import numpy as np


filename = 'test_data_four'
test_data = None
test_data_shape = (3, 3)

if test_data is None:
    test_data = []
    for x in range(test_data_shape[0] * test_data_shape[1]):
        test_data.append(100 * x)
        test_data.append(100 * x)
# Can be any list of 3 integers: Does not affect data
header = [0, 0, 0]
filename = '/Users/wroberts/Documents/pywinds/pywinds/test/test_files/' + str(filename) + '.flo'
test_data = test_data
np.ndarray.tofile(np.array(header + test_data, dtype=np.float32), filename)
# file = open(filename, 'r+b')
# file.seek(0)
# file.write(bytes([10]))
# file.seek(4)
# file.write(bytes([test_data_shape[1]]))
# file.seek(8)
# file.write(bytes([test_data_shape[0]]))
# file.close()
