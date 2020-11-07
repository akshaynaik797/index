from multiprocessing import Pool
from temp1 import write


def f(x):
    # flag = True
    # x = x[0]
    # for i in range(2, x):
    #     if x%i == 0:
    #         flag = False
    #         break
    # return flag
    return x[0], x[1]


if __name__ == '__main__':
    with Pool(9) as p:
        print(p.map_async(write, [(1, 10), (2, 1), (3, 1), (4, 1), (5, 11), (6, 1), (7, 1), (8, 3), (9, 1)]))
        p.close()
        p.join()
