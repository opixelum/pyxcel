import json
import Main
import xml.etree.ElementTree as ET
import yaml


def stringToTypeOfValue(string):
    if string.isdigit():
        if "." in string:
            return float(string)
        else:
            return int(string)
    if string == 'True' or string == 'true':
        return True
    if string == 'False' or string == 'false':
        return False
    return string


def jsonFileToArray(name):
    with open(name, "r") as f:
        return json.load(f)


def arrayToJson(arr, name):
    with open(name, "w") as f:
        json.dump(arr, f)


def csvToArray(name):
    res = []

    with open(name, "r") as f:
        t = f.read().split("\n")
        header = t[0].split(";")

        for i in t[1:]:
            if i == "":
                break

            d = {}
            for j, value in enumerate(i.split(';')):
                if ',' in value:
                    d[header[j]] = [stringToTypeOfValue(k) for k in value.split(',')]
                else:
                    d[header[j]] = stringToTypeOfValue(value)
            res.append(d)

        return res


def arrayToCsv(array, name):
    header = [i for i in array[0]]
    r = ';'.join(header)
    for i in array:
        line = []
        for j in header:
            if type(i[j]) == list:
                line.append(','.join([str(k) for k in i[j]]))
            else:
                line.append(str(i[j]))
        r += '\n' + ';'.join(line)
    with open(name, 'w') as f:
        f.write(r)


def arrayToXml(array, name):
    root = ET.Element('root')
    for i in array:
        child = ET.Element('row')
        root.append(child)
        for j in i:
            child2 = ET.Element(j)
            child2.text = str(i[j])
            child.append(child2)
    tree = ET.ElementTree(root)
    tree.write(name)


def xmlToArray(name):
    root = ET.parse(name).getroot()
    res = []
    for i in root:
        d = {}
        for j in i:
            d[j.tag] = stringToTypeOfValue(j.text)
        res.append(d)
    return res


def yamlToArray(name):
    with open(name, "r") as f:
        arr = yaml.safe_load(f)
    return arr


def arrayToYaml(array, name):
    with open(name, "w") as f:
        yaml.dump(array, f)


def getColumns(array):
    res = []
    for i in array:
        for j in i:
            if j not in res:
                res.append(j)
    Main.context["columns"] = res
