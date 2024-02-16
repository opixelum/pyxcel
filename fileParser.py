import json
import xml.etree.ElementTree as ET
import yaml


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def str_to_type(string):
    if string[0] == "-" or string[0] == "+" or string[0].isdigit():
        if string.isdigit():
            return int(string)
        if isfloat(string):
            return float(string)

    if string == "True" or string == "true":
        return True

    if string == "False" or string == "false":
        return False

    return string


def json_to_data(name):
    with open(name, "r") as f:
        return json.load(f)


def data_to_json(arr, name):
    with open(name, "w") as f:
        json.dump(arr, f)


def is_csv_parser(i, separator):
    if not i.isdigit() and not i.isalpha() and i != separator and i != "\n" and i != "\r" and i != "\"" and i != "'" and i != "." and i != "!" and i != "?" and i != "@":
        return True
    return False

def csv_to_data(name):
    res = []

    with open(name, "r") as f:
        t = f.read().split("\n")
        separator = ";"
        for i in t[0]:
            if is_csv_parser(i, separator):
                separator = i
                break

        header = t[0].split(separator)
        separator2 = ""
        for i in t[1]:
            if is_csv_parser(i, separator):
                separator2 = i
                break
        for i in t[1:]:
            if i == "":
                break

            d = {}
            for j, value in enumerate(i.split(separator)):
                if separator2 == "":
                    d[header[j]] = str_to_type(value)
                else:
                    if separator2 in value:
                        d[header[j]] = [str_to_type(k) for k in value.split(separator2)]
            res.append(d)

        return res


def data_to_csv(array, name):
    header = [i for i in array[0]]
    r = ";".join(header)
    for i in array:
        line = []
        for j in header:
            if isinstance(i[j], list):
                line.append(",".join([str(k) for k in i[j]]))
            else:
                line.append(str(i[j]))
        r += "\n" + ";".join(line)
    with open(name, "w") as f:
        f.write(r)


def data_to_xml(array, name):
    root = ET.Element("root")
    for i in array:
        child = ET.Element("row")
        root.append(child)
        for j in i:
            child2 = ET.Element(j)
            child2.text = str(i[j])
            child.append(child2)
    tree = ET.ElementTree(root)
    tree.write(name)


def xml_to_data(name):
    root = ET.parse(name).getroot()
    res = []
    for i in root:
        d = {}
        for j in i:
            d[j.tag] = str_to_type(j.text)
        res.append(d)
    return res


def yaml_to_data(name):
    with open(name, "r") as f:
        arr = yaml.safe_load(f)
    return arr


def data_to_yaml(array, name):
    with open(name, "w") as f:
        yaml.dump(array, f)


def column_type(array, column):
    has_bool = False
    has_int = False
    has_float = False

    for row in array:
        row[column] = str_to_type(str(row[column]))
        if isinstance(row[column], str):
            return str
        if isinstance(row[column], bool):
            has_bool = True
        if isinstance(row[column], int):
            has_int = True
        if isinstance(row[column], float):
            has_float = True

    if has_bool and not has_int and not has_float:
        return bool

    if has_float:
        return float

    if has_int:
        return int

    return str


def unify_column_type(array, column):
    """
    Set all the values in a column to the same type:
    - If there it contains only "true" or "false" then it will be converted to boolean;
    - If it contains only digits then it will be converted to int or float (depending if it has a dot or not);
    - Else, it will be left as a string.
    """
    if column_type(array, column) == str:
        for row in array:
            row[column] = str(row[column])
    elif column_type(array, column) == bool:
        for row in array:
            row[column] = bool(row[column])
    elif column_type(array, column) == float:
        for row in array:
            row[column] = float(row[column])
    elif column_type(array, column) == int:
        for row in array:
            row[column] = int(row[column])

    return array
