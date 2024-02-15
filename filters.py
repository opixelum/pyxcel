def filter_data(data, field, operator, value):
    comparison_functions = {
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "contains": lambda x, y: y in x,
        "startswith": lambda x, y: x.startswith(y),
        "endswith": lambda x, y: x.endswith(y),
        "list_contains": lambda x, y: y in x,
        "list_min": lambda x, y: min(x) == y,
        "list_max": lambda x, y: max(x) == y,
        "list_avg_eq": lambda x, y: sum(x) / len(x) == y,
        "list_avg_lt": lambda x, y: sum(x) / len(x) < y,
        "list_avg_gt": lambda x, y: sum(x) / len(x) > y,
    }

    if field is None:
        filter_data = [entry for entry in data if any(comparison_functions[operator](value, entry[field]) for field in entry)]
    else:
        filter_data = [entry for entry in data if comparison_functions[operator](entry[field], value)]
    return filter_data
