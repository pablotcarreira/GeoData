# Pablo Carreira - 15/05/17


import numpy as np
from _dev.experimentos import mirror_block, MIRROR_TOP, MIRROR_BOTTOM, MIRROR_LEFT, MIRROR_RIGHT


def mirroring():
    padding = 3
    block_data = np.asarray([
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [5, 5, 5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7, 7]
    ], np.uint8)
    tblr = [mirror_block(block_data, padding, MIRROR_TOP),
            mirror_block(block_data, padding, MIRROR_BOTTOM),
            mirror_block(block_data, padding, MIRROR_LEFT),
            mirror_block(block_data, padding, MIRROR_RIGHT)]
    resultados_experados =[
        [[3, 3, 3, 3, 3, 3, 3],
         [2, 2, 2, 2, 2, 2, 2],
         [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7]],
        [[1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7],
         [7, 7, 7, 7, 7, 7, 7],
         [6, 6, 6, 6, 6, 6, 6],
         [5, 5, 5, 5, 5, 5, 5]],
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
         [3, 2, 1, 1, 2, 3, 4, 5, 6, 7],
         [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7, 7, 7, 7]],
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
         [1, 2, 3, 4, 5, 6, 7, 7, 6, 5],
         [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
         [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
         [7, 7, 7, 7, 7, 7, 7, 7, 7, 7]]]
    for resultado, experado in zip(tblr, resultados_experados):
        assert resultado.tolist() == experado


if __name__ == '__main__':
    mirroring()