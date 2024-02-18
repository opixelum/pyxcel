import tkinter as tk
from tkinter import filedialog

import file_parser
import filters
import main


def open_window(size, title):
    w = tk.Tk()
    w.geometry(size)
    w.title(title)
    return w


def default_value(column_name):
    if file_parser.column_type(main.context["data"], column_name) == int:
        return 0
    elif file_parser.column_type(main.context["data"], column_name) == float:
        return 0.0
    elif file_parser.column_type(main.context["data"], column_name) == bool:
        return False
    elif file_parser.column_type(main.context["data"], column_name) == list:
        return []
    else:
        return ""


def update_value(row_number, column_name, value_string_var):
    new_value = value_string_var.get()

    if new_value == "":
        new_value = default_value(column_name)

    main.context["history"].append((row_number, column_name, main.context["data"][row_number][column_name]))
    main.context["data"][row_number][column_name] = new_value
    main.context["data"] = file_parser.unify_column_type(main.context["data"], column_name)

def revert_to_original():
    """
    Reverts the array to its original state (before any modification).
    """
    file_type = main.context["file_path"].split(".")[-1]
    main.context["file_path"] = main.context["file_path"]
    if file_type == "csv":
        main.context["data"] = file_parser.csv_to_data(main.context["file_path"])
    elif file_type == "json":
        main.context["data"] = file_parser.json_to_data(main.context["file_path"])
    elif file_type == "xml":
        main.context["data"] = file_parser.xml_to_data(main.context["file_path"])
    elif file_type == "yaml":
        main.context["data"] = file_parser.yaml_to_data(main.context["file_path"])
    display_data()


def undo():
    """
    Reverts the array to its previous state (before the last modification).
    """
    if len(main.context["history"]) == 0:
        return
    row_number, column_name, previous_value = main.context["history"].pop()
    main.context["data"][row_number][column_name] = previous_value
    main.context["data"] = file_parser.unify_column_type(main.context["data"], column_name)
    display_data()


def create_table():
    number_of_rows = max(len(main.context["data"]) + 1, 10)
    number_of_columns = len(main.context["data"][0])

    for i in range(number_of_columns):
        main.window.grid_columnconfigure(i, weight=1)
    for i in range(number_of_rows):
        main.window.grid_rowconfigure(i, weight=1)

    # Keep track of the column_names stringvars to update them on change
    for column_number, column_name in enumerate(main.context["data"][0]):
        column_name_sv = tk.StringVar(value=column_name)
        column_name_entry = tk.Entry(main.window, textvariable=column_name_sv)
        column_name_entry.bind(
            "<FocusOut>",
            lambda _, previous=column_name, sv=column_name_sv,: update_column_name(previous, sv),
        )
        column_name_entry.grid(row=0, column=column_number)
        column_name_entry.bind("<Button-3>", lambda _, x=column_name: column_name_right_click_menu(x))

    for row_number, row in enumerate(main.context["data"]):
        for column_number, (column_name, value) in enumerate(row.items()):
            # If the value is a number ending with .0, display it as an integer
            if str(value)[-2:] == ".0":
                value = str(value)[:-2]

            # If value are boolean, display it as True or False
            if str(value).lower() == "true":
                value = "True"
            elif str(value).lower() == "false":
                value = "False"

            value_string_var = tk.StringVar(value=value)
            value_entry = tk.Entry(main.window, textvariable=value_string_var)
            value_entry.grid(row=row_number + 1, column=column_number)
            value_entry.bind(
                "<Button-3>",
                lambda _, a=row_number, b=column_name, c=value_string_var: value_right_click_menu(a, b, c),
            )
            value_entry.bind(
                "<FocusOut>",
                lambda _, a=row_number, b=column_name, c=value_string_var: update_value(a, b, c),
            )
            value_entry.bind(
                "<Return>",
                lambda _, a=row_number, b=column_name, c=value_string_var: update_value(a, b, c),
            )
            value_entry.bind(
                "<Control-z>",
                lambda _, a=row_number, b=column_name, c=value_string_var: update_value(a, b, c),
            )


def open_file():
    main.context = {
        "data": [],
        "sort_key": "",
        "sort_reverse": False,
        "history": [],
    }

    file = filedialog.askopenfile()

    if file:
        # get type of file csv, json, xml, yaml
        file_type = file.name.split(".")[-1]

        main.context["file_path"] = file.name

        # Update window title
        file_name = file.name.split("/")[-1]
        main.window.title(file_name + " - Pyxcel")

        if file_type == "csv":
            main.context["data"] = file_parser.csv_to_data(file.name)
        elif file_type == "json":
            main.context["data"] = file_parser.json_to_data(file.name)
        elif file_type == "xml":
            main.context["data"] = file_parser.xml_to_data(file.name)
        elif file_type == "yaml":
            main.context["data"] = file_parser.yaml_to_data(file.name)
        else:
            print("ERROR: File type not supported")
            main.context["data"] = []

        display_data()


def save_as():
    file = filedialog.asksaveasfile(
        defaultextension=".csv",
        filetypes=[
            ("CSV file", ".csv"),
            ("JSON file", ".json"),
            ("XML file", ".xml"),
            ("YAML file", ".yaml"),
        ],
    )
    if file is None:
        return
    file_type = file.name.split(".")[-1]

    main.context["file_path"] = file.name

    if file_type == "csv":
        file_parser.data_to_csv(main.context["data"], file.name)
    elif file_type == "json":
        file_parser.data_to_json(main.context["data"], file.name)
    elif file_type == "xml":
        file_parser.data_to_xml(main.context["data"], file.name)
    elif file_type == "yaml":
        file_parser.data_to_yaml(main.context["data"], file.name)
    else:
        print("ERROR: File type not supported")
        main.context["data"] = []

    display_data()


def save():
    if main.context["file_path"] == "":
        save_as()
        return

    file_type = main.context["file_path"].split(".")[-1]

    if file_type == "csv":
        file_parser.data_to_csv(main.context["data"], main.context["file_path"])
    elif file_type == "json":
        file_parser.data_to_json(main.context["data"], main.context["file_path"])
    elif file_type == "xml":
        file_parser.data_to_xml(main.context["data"], main.context["file_path"])
    elif file_type == "yaml":
        file_parser.data_to_yaml(main.context["data"], main.context["file_path"])
    else:
        print("ERROR: File type not supported")


def create_menus():
    menubar = tk.Menu(main.window)
    main.window.config(menu=menubar)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: new_file())
    filemenu.add_command(label="Open...", command=lambda: open_file())
    filemenu.add_command(label="Save", command=lambda: save())
    filemenu.add_command(label="Save As...", command=lambda: save_as())
    filemenu.add_separator()
    filemenu.add_command(label="Exit Pyxcel", command=main.window.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    sortmenu = tk.Menu(menubar, tearoff=0)
    sortmenu.add_command(label="Reset", command=lambda: reset_sort())
    menubar.add_cascade(label="Sort", menu=sortmenu)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Revert to Original", command=lambda: revert_to_original())
    editmenu.add_command(label="Add Row", command=lambda: add_row())
    editmenu.add_command(label="Add Column", command=lambda: add_column())
    menubar.add_cascade(label="Edit", menu=editmenu)
    filtermenu = tk.Menu(menubar, tearoff=0)
    filtermenu.add_command(label="Add filter", command=lambda: add_search_bar(None))
    filtermenu.add_command(label="Undo filters", command=lambda: undo_filters())
    filtermenu.add_command(label="Reset filters", command=lambda: reset_filters())
    menubar.add_cascade(label="Filter", menu=filtermenu)


def column_name_right_click_menu(column_name):
    rightClickMenu = tk.Menu(main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: show_stats(column_name))
    rightClickMenu.add_command(label="Sort", command=lambda: sort_data(column_name))
    rightClickMenu.add_command(label="Delete Column", command=lambda: delete_column(column_name))
    rightClickMenu.post(main.window.winfo_pointerx(), main.window.winfo_pointery())


def value_right_click_menu(row_number, column_name, value_string_var):
    update_value(row_number, column_name, value_string_var)

    rightClickMenu = tk.Menu(main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: show_stats(column_name))
    rightClickMenu.add_command(label="Sort", command=lambda: sort_data(column_name))
    rightClickMenu.add_command(label="Delete Row", command=lambda: delete_row(row_number))
    rightClickMenu.add_command(label="Delete Column", command=lambda: delete_column(column_name))
    rightClickMenu.post(main.window.winfo_pointerx(), main.window.winfo_pointery())


def init_window():
    main.window = open_window("1000x500", "Pyxcel")
    main.context = {
        "data": [],
        "sort_key": "",
        "sort_reverse": False,
        "file_path": "",
        "history": [],
    }

    # Shortcuts
    main.window.bind("<Control-s>", lambda _: save())
    main.window.bind("<Control-z>", lambda _: undo())

    display_data()
    main.window.mainloop()


def clear_window():
    for widget in main.window.winfo_children():
        widget.destroy()
    main.window.update()


def display_data():
    clear_window()
    create_menus()
    if len(main.context["data"]) == 0:
        text = tk.Label(main.window, text="No data to display.")
        text.place(relx=0.5, rely=0.5, anchor="center")
    else:
        create_table()
    main.window.update()


def sort_data(column):
    if main.context["sort_key"] == column:
        main.context["data"].sort(key=lambda x: x[column], reverse=not main.context["sort_reverse"])
        main.context["sort_reverse"] = not main.context["sort_reverse"]
    else:
        main.context["data"].sort(key=lambda x: x[column])
        main.context["sort_reverse"] = False
    main.context["sort_key"] = column
    display_data()


def reset_sort():
    main.context["sort_key"] = ""
    main.context["sort_reverse"] = False
    display_data()


def show_stats(column):
    display_data()
    windowStats = open_window("300x300", "Stats")

    column_type = file_parser.column_type(main.context["data"], column)

    # Numbers
    if column_type == int or column_type == float:
        min = main.context["data"][0][column]
        max = main.context["data"][0][column]
        avg = 0

        for i in main.context["data"]:
            if min > i[column]:
                min = i[column]
            if max < i[column]:
                max = i[column]
            avg += i[column]

        avg /= len(main.context["data"])

        if str(min)[-2:] == ".0":
            min = int(str(min)[:-2])

        if str(max)[-2:] == ".0":
            max = int(str(max)[:-2])

        if str(avg)[-2:] == ".0":
            avg = int(str(avg)[:-2])

        text = tk.Label(
            windowStats,
            text="Min: " + str(min) + "\nMax: " + str(max) + "\nAvg: " + str(avg),
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()

    # Booleans
    elif column_type == bool:
        true = 0
        false = 0

        for i in main.context["data"]:
            if i[column]:
                true += 1
            else:
                false += 1

        text = tk.Label(
            windowStats,
            text="True: " + str(true / len(main.context["data"]) * 100) + "%\nFalse: " + str(false / len(main.context["data"]) * 100) + "%",
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()

    # Lists and strings
    elif column_type == list or column_type == str:
        min = len(main.context["data"][0][column])
        max = len(main.context["data"][0][column])
        avg = 0

        for i in main.context["data"]:
            if min > len(i[column]):
                min = len(i[column])
            if max < len(i[column]):
                max = len(i[column])
            avg += len(i[column])

        avg /= len(main.context["data"])

        if str(min)[-2:] == ".0":
            min = int(str(min)[:-2])

        if str(max)[-2:] == ".0":
            max = int(str(max)[:-2])

        if str(avg)[-2:] == ".0":
            avg = int(str(avg)[:-2])

        min_text = "Min " + ("list" if column_type == list else "string") + " size: " + str(min)
        max_text = "\nMax " + ("list" if column_type == list else "string") + " size: " + str(max)
        avg_text = "\nAvg " + ("list" if column_type == list else "string") + " size: " + str(avg)
        text = tk.Label(windowStats, text=min_text + max_text + avg_text)
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()


def add_row():
    main.context["data"].append({key: "" for key in main.context["data"][0]})
    display_data()


def add_column():
    for row in main.context["data"]:
        row["New column"] = ""
    display_data()


def update_column_name(previous, sv):
    for row in main.context["data"]:
        row[sv.get()] = row.pop(previous)

    # Need to update the column_name name on the frontend
    display_data()


def delete_row(row_number):
    main.context["data"].pop(row_number)
    display_data()


def delete_column(column_name):
    for row in main.context["data"]:
        row.pop(column_name)
    display_data()


def new_file():
    main.context = {
        "data": [{"New column": ""}],
        "sort_key": "",
        "sort_reverse": False,
        "file_path": "",
        "history": [],
    }
    display_data()


def add_search_bar(new_field_var):
    new_window = open_window("300x300", "Search")

    search_frame = tk.Frame(new_window)
    search_frame.grid(row=0, column=len(main.context["columns"]))

    # Field dropdown
    field_label = tk.Label(search_frame, text="Field:")
    field_label.grid(row=0, column=0, padx=5, pady=5)
    field_options = main.context["columns"] if main.context["columns"] else ["all"]
    if new_field_var != None:
        field_var = tk.StringVar(search_frame)
        field_var.set(new_field_var)
    else:
        field_var = tk.StringVar(search_frame)
        field_var.set(field_options[0])  # Set a default value
    field_var.trace_add("write", lambda *_, x=field_var: update_dropdown(x, new_window))
    field_dropdown = tk.OptionMenu(search_frame, field_var, *field_options)
    field_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Operator dropdown
    operator_label = tk.Label(search_frame, text="Operator:")
    operator_label.grid(row=1, column=0, padx=5, pady=5)
    if field_var.get() != "all":
        if type(main.context["array"][0][field_var.get()]) == int or type(main.context["array"][0][field_var.get()]) == float:
            operator_options = ["=", ">", "<", ">=", "<=", "!="]
        else:
            operator_options = ["contains", "starts with", "ends with", "list contains", "list min", "list max", "list avg eq", "list avg lt", "list avg gt"]
    else:
        operator_options = ["contains", "starts with", "ends with", "list contains", "list min", "list max", "list avg eq", "list avg lt", "list avg gt"]

    operator_var = tk.StringVar(search_frame)
    operator_var.set(operator_options[0])  # Set a default value
    operator_dropdown = tk.OptionMenu(search_frame, operator_var, *operator_options)
    operator_dropdown.grid(row=1, column=1, padx=5, pady=5)

    # Value entry
    value_label = tk.Label(search_frame, text="Value:")
    value_label.grid(row=2, column=0, padx=5, pady=5)
    value_entry = tk.Entry(search_frame)
    value_entry.grid(row=2, column=1, padx=5, pady=5)

    # Send button
    send_button = tk.Button(search_frame, text="Send", command=lambda: apply_search(field_var.get(), operator_var.get(), value_entry.get()))
    send_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    new_window.mainloop()


def update_dropdown(x, window):
    window.destroy()
    add_search_bar(x.get())


def apply_search(field, operator, value):
    main.save_array_filters.append(main.context["array"].copy())
    main.context["array"] = filters.filter_data(main.context["array"], field, operator, value)
    display_data()


def reset_filters():
    if main.save_array_filters == []:
        return
    main.context["array"] = main.save_array_filters[0]
    main.save_array_filters = []
    display_data()


def undo_filters():
    if main.save_array_filters == []:
        return
    main.context["array"] = main.save_array_filters.pop()
    display_data()
