import os
import sys



def main():


    dirName = sys.argv[1]

    # Create target directory & all intermediate directories if don't exists
    try:
        os.makedirs(dirName)
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")




if __name__ == '__main__':
    main()
