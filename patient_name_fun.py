import re


def pname_fun(text, regex_list):
    pname, badchars = "", [':', ","]
    for i in regex_list:
        temp = re.compile(i).search(text)
        if temp is not None:
            pname = temp.group().strip()
            for i in badchars:
                pname = pname.replace(i, '').strip()
            break
    return pname

if __name__ == "__main__":
    f = "patient name: akshay naik hjadsg"
    # text = "patient name: akshay naik"
    regex_list = [r"(?<=Patient Name).*(?=Age)"]
    pname = pname_fun(f, regex_list)
    pass