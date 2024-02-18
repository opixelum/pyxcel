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
        "list contains": lambda x, y: x in y,
        "list min": lambda x, y: min(y) == x,
        "list max": lambda x, y: max(y) == x,
        "list avg eq": lambda x, y: sum(y) / len(y) == x,
        "list avg lt": lambda x, y: sum(y) / len(y) < x,
        "list avg gt": lambda x, y: sum(y) / len(y) > x,
    }

    filter_data = []

    if field == "all":
        for entry in data:
            for new_field in entry:
                if comparison_functions[operator](value, entry[new_field]):
                    filter_data.append(entry)
                    break
    else:
        for entry in data:
            if comparison_functions[operator](value, entry[field]):
                filter_data.append(entry)

    return filter_data
