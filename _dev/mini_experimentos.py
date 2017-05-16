# Pablo Carreira - 12/05/17

import numpy as np

class Listosa:
    def __getitem__(self, item):
        print(item)
        return 10

block_data = np.asarray([
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [5, 5, 5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7, 7]
    ], np.uint8)

if __name__ == '__main__':
    l = Listosa()
    print(l[10:20])

    padding = 2
    print(block_data[padding:-padding, padding:-padding])
