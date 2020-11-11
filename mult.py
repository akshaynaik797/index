from multiprocessing import Pool
from mult1 import run_ins_process
if __name__ == '__main__':
    with Pool(4) as p:
        print(p.map_async(run_ins_process,
                          [('liberty', 'query', '/home/akshay/Downloads/Ram_PREAUTHQUERYREM.pdf', 'sub1', '09/11/2020', 'max'),
                           ('tata', 'preauth', '/home/akshay/Downloads/8_AL_SHANU_AHLUWALIA__1602909425_initial Approval.pdf', 'sub2', '09/11/2020', 'max'),
                           ('tata', 'query', '/home/akshay/Downloads/8_Query_EAL_SHANU_AHLUWALIA__1603192980_Query.pdf', 'sub3', '09/11/2020', 'max'),
                           ('tata', 'final', '/home/akshay/Downloads/2020101600008.pdf', 'sub4', '09/11/2020', 'max'),]))
        p.close()
        p.join()
    # run_ins_process(('liberty', 'query', '/home/akshay/Downloads/Ram_PREAUTHQUERYREM.pdf', 'sub1', '09/11/2020', 'max'))