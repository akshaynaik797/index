from multiprocessing import Process

def f(x):
    flag = True
    for i in range(2, x):
        if x%i == 0:
            flag = False
            break
    return flag

if __name__ == '__main__':
    p = Process(target=f, args=(23213,))
    p.start()
    p.join()


# if __name__ == '__main__':
#     with Pool(5) as p:
#         print(p.apply(f, [9576890767, 2860486313, 3367900313]))
        # print(p.map(f, [34, 44, 67]))
    # print(f(9576890767))