import json


def stringToValue(string):
    if string.isdigit():
        if '.' in string:
            return float(string)
        else:
            return int(string)
    if string == 'True':
        return True
    if string == 'False':
        return False
    return string


def jsonFileToArray(name):
    f = open(name, 'r')
    arr = json.load(f)
    return arr


def arrayToJson(arr, name):
    f = open(name, 'w')
    json.dump(arr, f)


def csvToArray(name):
    res = []
    f = open(name, 'r')
    t = f.read().split('\n')
    l = t[0].split(';')
    for i in t[1:]:
        if i == '': break
        d = {}
        for j, value in enumerate(i.split(';')):
            d[l[j]] = stringToValue(value)
        res.append(d)
    return res


def isValue(array):
    for i in array:
        for j in i:
            if type(i[j]) == list or type(i[j]) == dict:
                return False
    return True

def arrayToCsv(array, name):
    l = [i for i in array[0]]
    if not isValue(array):
        print("ERROR : Values can t be a csv file")
        return
    r = ';'.join(l)
    for i in array:
        line = []
        for j in l:
            line.append(str(i[j]))
        r += '\n' + ';'.join(line)
    f = open(name, 'w')
    f.write(r)