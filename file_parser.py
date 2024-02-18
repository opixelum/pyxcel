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
    special_chars = {"\n", "\r", '"', "'", ".", "!", "?", "@", " "}
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
                    else:
                        d[header[j]] = str_to_type(value)
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
    has_numeric = False
    has_float = False
    has_strictly_bool = False
    has_non_numeric_or_bool = False  # Flag for any non-numeric and non-boolean string

    for row in data:
        value = str(
            row[column_name]
        ).strip()  # Convert value to string and strip whitespace
        lower_value = value.lower()

        # Check if the string is a boolean value
        if lower_value in ["true", "false"]:
            has_strictly_bool = True
        else:
            try:
                # Attempt to convert the string to a float
                float(value)
                has_numeric = True
                if "." in value or "e" in lower_value or "E" in value:
                    has_float = True
            except ValueError:
                # If conversion fails, it's not a valid numeric string
                has_non_numeric_or_bool = True

    # Decision logic for determining column type
    if has_non_numeric_or_bool:
        return str  # Any non-numeric/non-boolean string forces the whole column to be strings
    elif has_numeric:
        return (
            float if has_float else int
        )  # Numeric values, prefer float if any decimal points
    elif has_strictly_bool:
        return bool  # Only boolean values
    else:
        return str  # Default to string if none of the above conditions are met


def unify_column_type(data, column_name):
    target_type = column_type(data, column_name)
    updated_data = []

    for row in data:
        updated_row = row.copy()
        original_value = row[column_name]

        # Ensure the conversion logic checks for string type before calling .lower()
        if target_type == str:
            converted_value = str(original_value)
        elif target_type == int:
            try:
                converted_value = int(
                    float(original_value)
                )  # Convert via float for cases like '3.0'
            except ValueError:
                converted_value = (
                    original_value  # Preserve original in case of conversion error
                )
        elif target_type == float:
            try:
                converted_value = float(original_value)
            except ValueError:
                converted_value = original_value
        elif target_type == bool:
            # Correctly handle boolean conversion by first ensuring it's a string
            if isinstance(original_value, str):
                converted_value = original_value.lower() == "true"
            else:
                # If it's already a boolean, no conversion is needed; otherwise, it cannot be a boolean
                converted_value = (
                    original_value
                    if isinstance(original_value, bool)
                    else str(original_value)
                )

        updated_row[column_name] = converted_value
        updated_data.append(updated_row)

    return updated_data
