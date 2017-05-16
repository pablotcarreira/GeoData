# Pablo Carreira - 12/05/17

import numpy as np

class Listosa:
    def __getitem__(self, item):
        print(item)
        return 10



if __name__ == '__main__':
    l = Listosa()
    print(l[10:20])
