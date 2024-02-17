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
    if string == "":
        return string

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


def json_to_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def data_to_json(arr, file_path):
    with open(file_path, "w") as f:
        json.dump(arr, f)


def is_csv_parser(character, separator):
    special_chars = {"\n", "\r", '"', "'", ".", "!", "?", "@"}
    return (
        not character.isdigit()
        and not character.isalpha()
        and character not in special_chars.union({separator})
    )


def csv_to_data(file_path):
    res = []

    with open(file_path, "r") as f:
        t = f.read().split("\n")
        separator = ";"
        for character in t[0]:
            if is_csv_parser(character, separator):
                separator = character
                break

        header = t[0].split(separator)
        separator2 = ""
        for character in t[1]:
            if is_csv_parser(character, separator):
                separator2 = character
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


def data_to_csv(data, file_path):
    header = [i for i in data[0]]
    r = ";".join(header)
    for i in data:
        line = []
        for j in header:
            if isinstance(i[j], list):
                line.append(",".join([str(k) for k in i[j]]))
            else:
                line.append(str(i[j]))
        r += "\n" + ";".join(line)
    with open(file_path, "w") as f:
        f.write(r)


def data_to_xml(data, file_path):
    root = ET.Element("root")
    for i in data:
        child = ET.Element("row")
        root.append(child)
        for j in i:
            child2 = ET.Element(j)
            child2.text = str(i[j])
            child.append(child2)
    tree = ET.ElementTree(root)
    tree.write(file_path)


def xml_to_data(file_path):
    root = ET.parse(file_path).getroot()
    res = []
    for i in root:
        d = {}
        for j in i:
            d[j.tag] = str_to_type(j.text)
        res.append(d)
    return res


def yaml_to_data(file_path):
    with open(file_path, "r") as f:
        arr = yaml.safe_load(f)
    return arr


def data_to_yaml(data, file_path):
    with open(file_path, "w") as f:
        yaml.dump(data, f)


def column_type(data, column_name):
    has_bool = False
    has_int = False
    has_float = False

    for row in data:
        row[column_name] = str_to_type(str(row[column_name]))
        if isinstance(row[column_name], str):
            return str
        if isinstance(row[column_name], bool):
            has_bool = True
        if isinstance(row[column_name], int):
            has_int = True
        if isinstance(row[column_name], float):
            has_float = True

    if has_bool and not has_int and not has_float:
        return bool

    if has_float:
        return float

    if has_int:
        return int

    return str


def unify_column_type(data, column_name):
    """
    Set all the values in a column to the same type:
    - If there it contains only "true" or "false" then it will be converted to boolean;
    - If it contains only digits then it will be converted to int or float (depending if it has a dot or not);
    - Else, it will be left as a string.
    """
    if column_type(data, column_name) == str:
        for row in data:
            row[column_name] = str(row[column_name])
    elif column_type(data, column_name) == bool:
        for row in data:
            row[column_name] = bool(row[column_name])
    elif column_type(data, column_name) == float:
        for row in data:
            row[column_name] = float(row[column_name])
    elif column_type(data, column_name) == int:
        for row in data:
            row[column_name] = int(row[column_name])

    return data
