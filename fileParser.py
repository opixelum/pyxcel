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

            for j, value in enumerate(i.split(";")):
                d[header[j]] = stringToTypeOfValue(value)

            res.append(d)

        return res


def isAllValue(array):
    for i in array:
        for j in i:
            if isinstance(i[j], list) or isinstance(i[j], dict):
                return False
    return True


def arrayToCsv(array, name):
    header = [i for i in array[0]]

    if not isAllValue(array):
        print("ERROR: Values cannot be a CSV file.")
        return

    csv_content = ";".join(header)

    for i in array:
        line = []

        for j in header:
            line.append(str(i[j]))

        csv_content += "\n" + ";".join(line)

    with open(name, "w") as f:
        f.write(csv_content)


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


def arrayToXml(array, name, r="root"):
    root = ET.Element(r)

    for item in array:
        dictToXml(root, item)

    tree = ET.ElementTree(root)
    saveXml(tree, name)


def saveXml(tree, name):
    with open(name, "wb") as f:
        tree.write(f)


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


def save():
    if Main.context["file"] == "":
        print("ERROR : No file to save")
        # TODO: change by saveAs
        return

    ext = Main.context["file"].split(".")[-1]

    # Save the content of the cells in the array
    for i, row in enumerate(Main.context["array"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = Main.context["cell_vars"][i][key].get()

    if ext == "csv":
        arrayToCsv(Main.context["array"], Main.context["file"])
    elif ext == "json":
        arrayToJson(Main.context["array"], Main.context["file"])
    elif ext == "xml":
        arrayToXml(Main.context["array"], Main.context["file"])
    elif ext == "yaml":
        arrayToYaml(Main.context["array"], Main.context["file"])
    else:
        print("ERROR : File type not supported")
