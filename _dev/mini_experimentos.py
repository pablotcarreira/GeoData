# Pablo Carreira - 12/05/17

import numpy as np

def mirroring():
    padding = 3

    block_data = [
        [1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3],
        [4, 4, 4, 4, 4, 4],
        [5, 5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7]
    ]

    flip = np.flipud(block_data[:padding])
    print(flip)
    print("================")
    print(np.vstack((flip, block_data)))

if __name__ == '__main__':
    mirroring()