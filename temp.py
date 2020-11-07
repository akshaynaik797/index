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
    with Pool(5) as p:
        print(p.map(write, [(1, 10), (2, 2), (3, 1)]))
