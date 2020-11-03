import os, sys, zipfile, time, shutil
from datetime import datetime


# def clean_f(insurer_name):
#     pathname = os.path.dirname(sys.argv[0])
#     fullp = os.path.abspath(pathname) + '/'
#     src_directory = fullp + insurer_name + '/'
#     dst_directory = src_directory + 'backups/'
#     ts = time.time()
#
#     def zipdir(path, ziph):
#         # ziph is zipfile handle
#         for root, dirs, files in os.walk(path):
#             for file in files:
#                 if 'zip' not in file:
#                     ziph.write(os.path.join(root, file))
#
#     if not os.path.exists(dst_directory):
#         try:
#             os.mkdir(dst_directory)
#         except FileNotFoundError:
#             print('invalid insurer_name')
#             return False
#
#     zipf = zipfile.ZipFile(dst_directory + insurer_name + '_' + str(ts) + '.zip', 'w', zipfile.ZIP_DEFLATED)
#     zipdir(src_directory, zipf)
#     zipf.close()
#     return True


def clean_f(insurer_name, hosp_name):

    pathname = os.path.dirname(sys.argv[0])
    fullp = os.path.abspath(pathname) + '/'
    src_directory = fullp + insurer_name + '/'
    dst_directory = 'backups/'
    date_time = datetime.now().strftime("%m%d%Y%H%M%S")
    finaldirectory = dst_directory+insurer_name+'_'+date_time

    if not os.path.exists(dst_directory):
        try:
            os.mkdir(dst_directory)
        except FileNotFoundError:
            print('invalid insurer_name')
            return False

    if not os.path.exists(finaldirectory):
        try:
            os.mkdir(finaldirectory)
        except FileNotFoundError:
            print('invalid insurer_name')
            return False

    filelist = []
    fileext = ['pdf', 'xls', 'xlsx', 'html', 'txt']

    # for i in fileext:
    #     for root, dirs, files in os.walk(fullp+insurer_name):
    #         for file in files:
    #             if file.endswith(i):
    #                 filelist.append(os.path.join(root, file))

    for root, dirs, files in os.walk(fullp+insurer_name):
        for file in files:
            # fpath = os.path.abspath(file)
            if file.endswith('pdf') and hosp_name in str(os.path.join(root, file)):
                with open('flist.txt', 'a+') as f:
                    f.write(str(os.path.join(root, file))+'\n')
                filelist.append(os.path.join(root, file))
            elif file.endswith('xls') or file.endswith('xlsx'):
                with open('flist.txt', 'a+') as f:
                    f.write(str(os.path.join(root, file))+'\n')
                filelist.append(os.path.join(root, file))



    for i in filelist:
        # shutil.move(i, os.path.join(finaldirectory, i))
        try:
            shutil.move(i, finaldirectory)
        except Exception as e:
            #gives error if file already exists hence commented this part
            # print('error in clean file.py', e)
            pass
    return True

if __name__ == '__main__':
    print(clean_f('icici_lombard', 'Max'))
