def filter_data(data, field, operator, value):
    comparison_functions = {
        "=": lambda x, y: float(x) == float(y),
        "!=": lambda x, y: float(x) != float(y),
        "<": lambda x, y: float(y) < float(x),
        "<=": lambda x, y: float(y) <= float(x),
        ">": lambda x, y: float(y) > float(x),
        ">=": lambda x, y: float(y) >= float(x),
        "contains": lambda x, y: x in y,
        "starts with": lambda x, y: str.startswith(y, x),
        "ends with": lambda x, y: str.endswith(y, x),
        "list contains": lambda x, y: x in [str(z) for z in y],
        "list min size": lambda x, y: len(y) >= int(x),
        "list max size": lambda x, y: len(y) <= int(x),
    }

    filter_data = []

    if field == "all":
        for entry in data:
            for new_field in entry:
                if operator == "contains" or operator == "starts with" or operator == "ends with":
                    if isinstance(entry[new_field], str):
                        if comparison_functions[operator](value, entry[new_field]):
                            filter_data.append(entry)
                            break
                elif (
                    operator == "list contains"
                    or operator == "list min"
                    or operator == "list max"
                    or operator == "list avg eq"
                    or operator == "list avg lt"
                    or operator == "list avg gt"
                ):
                    if isinstance(entry[new_field], list):
                        if comparison_functions[operator](value, entry[new_field]):
                            filter_data.append(entry)
                            break
                else:
                    if isinstance(entry[new_field], (int, float)):
                        if comparison_functions[operator](value, entry[new_field]):
                            filter_data.append(entry)
                            break

    else:
        for entry in data:
            if comparison_functions[operator](value, entry[field]):
                filter_data.append(entry)

    return filter_data
