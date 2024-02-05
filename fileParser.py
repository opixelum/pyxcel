import json
import xml.etree.ElementTree as ET
import yaml


def stringToTypeOfValue(string):
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
    with open(name, 'r') as f:
        return json.load(f)


def arrayToJson(arr, name):
    with open(name, 'w') as f:
        json.dump(arr, f)


def csvToArray(name):
    res = []
    with open(name, 'r') as f:
        t = f.read().split('\n')
        l = t[0].split(';')
        for i in t[1:]:
            if i == '': break
            d = {}
            for j, value in enumerate(i.split(';')):
                d[l[j]] = stringToTypeOfValue(value)
            res.append(d)
        return res


def isAllValue(array):
    for i in array:
        for j in i:
            if type(i[j]) == list or type(i[j]) == dict:
                return False
    return True


def arrayToCsv(array, name):
    l = [i for i in array[0]]
    if not isAllValue(array):
        print("ERROR : Values can't be a csv file")
        return
    r = ';'.join(l)
    for i in array:
        line = []
        for j in l:
            line.append(str(i[j]))
        r += '\n' + ';'.join(line)
    with open(name, 'w') as f:
        f.write(r)


def recuXml(root):
    d = {}
    for i in root:
        if len(i) == 0:
            d[i.tag] = stringToTypeOfValue(i.text)
        else:
            d[i.tag] = recuXml(i)
    return d


def xmlToArray(name):
    tree = ET.parse(name)
    root = tree.getroot()
    res = []
    for i in root:
        res.append(recuXml(i))
    return res


def dictToXml(element, dictionary):
    for key, value in dictionary.items():
        subElement = ET.SubElement(element, key)
        if isinstance(value, dict):
            dictToXml(subElement, value)
        else:
            subElement.text = str(value)


def arrayToXml(array, r='root'):
    root = ET.Element(r)

    for item in array:
        dictToXml(root, item)

    tree = ET.ElementTree(root)
    return tree


def saveXml(tree, name):
    with open(name, 'wb') as f:
        tree.write(f)


def yamlToArray(name):
    with open(name, 'r') as f:
        arr = yaml.safe_load(f)
    return arr


def arrayToYaml(array, name):
    with open(name, 'w') as f:
        yaml.dump(array, f)