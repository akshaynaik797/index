s = ['preid', 'polno', 'amount', 'memid', 'pname']

datadict = {}
regexdict = {'': [[r"", ], r"^\w+$", ['-', ]],
             '': [[r"", ], r"^\w+$", ['-', ]],}

for i in regexdict:
    for j in regexdict[i][0]:
        data = re.compile(j).search(f)
        if data is not None:
            temp = data.group().strip()
            for k in regexdict[i][2]:
                temp = temp.replace(k, "")
            temp = temp.strip()
            if bool(re.compile(regexdict[i][1]).match(temp))
                datadict[i] = temp
                break
        datadict[i] = ""