import numpy as np


filename = 'test_data_two'
test_data = None
test_data_shape = (10, 10)

if test_data is None:
    test_data = []
    for x in range(test_data_shape[0] * test_data_shape[1]):
        test_data.append(10 * x)
        test_data.append(10 * x)
# Can be any list of 3 integers: Does not affect data
header = [0, 0, 0]
filename = 'C:/Users/William/Documents/pywinds/pywinds/test/test_files/' + str(filename) + '.flo'
np.ndarray.tofile(np.array(header + test_data, dtype=np.float32), filename)
