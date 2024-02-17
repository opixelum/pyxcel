import tkinter as tk
from tkinter import filedialog
import file_parser
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

    main.context["history"].append(
        (row_number, column_name, main.context["data"][row_number][column_name])
    )
    main.context["data"][row_number][column_name] = new_value
    main.context["data"] = file_parser.unify_column_type(
        main.context["data"], column_name
    )


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


def revert_to_previous():
    """
    Reverts the array to its previous state (before the last modification).
    """
    if len(main.context["history"]) == 0:
        return
    row_number, column_name, previous_value = main.context["history"].pop()
    main.context["data"][row_number][column_name] = previous_value
    main.context["data"] = file_parser.unify_column_type(
        main.context["data"], column_name
    )
    display_data()


def create_table():
    number_of_rows = max(len(main.context["data"]) + 1, 10)
    number_of_columns = len(main.context["data"][0])

    for i in range(number_of_columns):
        main.window.grid_columnconfigure(i, weight=1)
    for i in range(number_of_rows):
        main.window.grid_rowconfigure(i, weight=1)

    # Keep track of the headers stringvars to update them on change
    for column_number, column_name in enumerate(main.context["data"][0]):
        header_sv = tk.StringVar(value=column_name)
        header_entry = tk.Entry(main.window, textvariable=header_sv)
        header_entry.bind(
            "<FocusOut>",
            lambda _, previous=column_name, sv=header_sv,: update_column_name(
                previous, sv
            ),
        )
        header_entry.grid(row=0, column=column_number)
        header_entry.bind(
            "<Button-3>", lambda _, x=column_name: column_name_right_click_menu(x)
        )

    for row_number, row in enumerate(main.context["data"]):
        for column_number, (column_name, value) in enumerate(row.items()):
            # If the value is a number ending with .0, display it as an integer
            if str(value)[-2:] == ".0":
                value = str(value)[:-2]

            value_string_var = tk.StringVar(value=value)
            cell = tk.Entry(main.window, textvariable=value_string_var)
            cell.grid(row=row_number + 1, column=column_number)
            cell.bind(
                "<Button-3>",
                lambda _, x=column_name, row=row_number: value_right_click_menu(x, row),
            )
            cell.bind(
                "<FocusOut>",
                lambda _, a=row_number, b=column_name, c=value_string_var: update_value(
                    a, b, c
                ),
            )
            cell.bind(
                "<Return>",
                lambda _, a=row_number, b=column_name, c=value_string_var: update_value(
                    a, b, c
                ),
            )


def open_file():
    main.context = {
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
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml"),
            ("YAML files", "*.yaml"),
        ],
    )
    if file is None:
        return
    file_type = file.name.split(".")[-1]

    for i, row in enumerate(main.context["data"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = main.context["cell_vars"][i][key].get()

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
    editmenu.add_command(
        label="Revert to Original", command=lambda: revert_to_original()
    )
    editmenu.add_command(label="Add Row", command=lambda: add_row())
    editmenu.add_command(label="Add Column", command=lambda: add_column())
    menubar.add_cascade(label="Edit", menu=editmenu)


def column_name_right_click_menu(header):
    rightClickMenu = tk.Menu(main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: show_stats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sort_data(header))
    rightClickMenu.add_command(
        label="Delete Column", command=lambda: delete_column(header)
    )
    rightClickMenu.post(main.window.winfo_pointerx(), main.window.winfo_pointery())


def value_right_click_menu(header, row_number):
    rightClickMenu = tk.Menu(main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: show_stats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sort_data(header))
    rightClickMenu.add_command(
        label="Delete Row", command=lambda: delete_row(row_number)
    )
    rightClickMenu.add_command(
        label="Delete Column", command=lambda: delete_column(header)
    )
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
    main.window.bind("<Control-z>", lambda _: revert_to_previous())

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
        main.context["data"].sort(
            key=lambda x: x[column], reverse=not main.context["sort_reverse"]
        )
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
            text="True: "
            + str(true / len(main.context["data"]) * 100)
            + "%\nFalse: "
            + str(false / len(main.context["data"]) * 100)
            + "%",
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

        min_text = (
            "Min "
            + ("list" if column_type == list else "string")
            + " size: "
            + str(min)
        )
        max_text = (
            "\nMax "
            + ("list" if column_type == list else "string")
            + " size: "
            + str(max)
        )
        avg_text = (
            "\nAvg "
            + ("list" if column_type == list else "string")
            + " size: "
            + str(avg)
        )
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

    # Need to update the header name on the frontend
    display_data()


def delete_row(row_number):
    main.context["data"].pop(row_number)
    display_data()


def delete_column(header):
    for row in main.context["data"]:
        row.pop(header)
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
