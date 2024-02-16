import tkinter as tk
from tkinter import filedialog
import fileParser
import Main


def OpenWindow(size, title):
    w = tk.Tk()
    w.geometry(size)
    w.title(title)
    return w


def update_value(row_number, column_name, value_string_var):
    Main.context["data"][row_number][column_name] = value_string_var.get()


def revertToOriginal():
    """
    Reverts the array to its original state (before any modification).
    """
    # get type of file csv, json, xml, yaml
    ext = Main.context["file"].split(".")[-1]
    Main.context["file"] = Main.context["file"]
    if ext == "csv":
        Main.context["data"] = fileParser.csvToArray(Main.context["file"])
    elif ext == "json":
        Main.context["data"] = fileParser.jsonFileToArray(Main.context["file"])
    elif ext == "xml":
        Main.context["data"] = fileParser.xmlToArray(Main.context["file"])
    elif ext == "yaml":
        Main.context["data"] = fileParser.yamlToArray(Main.context["file"])
    displayArray()


def createTable():
    numRows = max(len(Main.context["data"]) + 1, 10)
    numColumns = len(Main.context["data"][0])

    for i in range(numColumns):
        Main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        Main.window.grid_rowconfigure(i, weight=1)

    # Keep track of the headers stringvars to update them on change
    for column_number, column_name in enumerate(Main.context["data"][0]):
        header_sv = tk.StringVar(value=column_name)
        header_entry = tk.Entry(Main.window, textvariable=header_sv)
        header_entry.bind(
            "<FocusOut>",
            lambda *_, previous=column_name, sv=header_sv,: updateHeaderCellOnFocusOut(
                previous, sv
            ),
        )
        header_entry.grid(row=0, column=column_number)
        header_entry.bind(
            "<Button-3>", lambda _, x=column_name: headerRightClickMenu(x)
        )

    for row_number, row in enumerate(Main.context["data"]):
        for column_number, (column_name, value) in enumerate(row.items()):
            value_string_var = tk.StringVar(value=value)
            value_string_var.trace_add(
                "write",
                lambda *_,
                a=row_number,
                b=column_name,
                c=value_string_var: update_value(a, b, c),
            )
            cell = tk.Entry(Main.window, textvariable=value_string_var)
            cell.grid(row=row_number + 1, column=column_number)
            cell.bind(
                "<Button-3>",
                lambda _, x=column_name, row=row_number: cellRightClickMenu(x, row),
            )


def openFile():
    file = filedialog.askopenfile()
    Main.context = {
        "data": [],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
    }
    if file:
        # get type of file csv, json, xml, yaml
        ext = file.name.split(".")[-1]
        Main.context["file"] = file.name
        if ext == "csv":
            Main.context["data"] = fileParser.csvToArray(file.name)
        elif ext == "json":
            Main.context["data"] = fileParser.jsonFileToArray(file.name)
        elif ext == "xml":
            Main.context["data"] = fileParser.xmlToArray(file.name)
        elif ext == "yaml":
            Main.context["data"] = fileParser.yamlToArray(file.name)
        else:
            print("ERROR : File type not supported")
            Main.context["data"] = []
        displayArray()


def saveAs():
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
    ext = file.name.split(".")[-1]

    for i, row in enumerate(Main.context["data"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = Main.context["cell_vars"][i][key].get()

    Main.context["file"] = file.name
    if ext == "csv":
        fileParser.arrayToCsv(Main.context["data"], file.name)
    elif ext == "json":
        fileParser.arrayToJson(Main.context["data"], file.name)
    elif ext == "xml":
        fileParser.arrayToXml(Main.context["data"], file.name)
    elif ext == "yaml":
        fileParser.arrayToYaml(Main.context["data"], file.name)
    else:
        print("ERROR : File type not supported")
        Main.context["data"] = []
    displayArray()


def save():
    if Main.context["file"] == "":
        saveAs()
        return
    ext = Main.context["file"].split(".")[-1]

    for i, row in enumerate(Main.context["data"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = Main.context["cell_vars"][i][key].get()

    if ext == "csv":
        fileParser.arrayToCsv(Main.context["data"], Main.context["file"])
    elif ext == "json":
        fileParser.arrayToJson(Main.context["data"], Main.context["file"])
    elif ext == "xml":
        fileParser.arrayToXml(Main.context["data"], Main.context["file"])
    elif ext == "yaml":
        fileParser.arrayToYaml(Main.context["data"], Main.context["file"])
    else:
        print("ERROR : File type not supported")


def makeMenu():
    menubar = tk.Menu(Main.window)
    Main.window.config(menu=menubar)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: newFile())
    filemenu.add_command(label="Open...", command=lambda: openFile())
    filemenu.add_command(label="Save", command=lambda: save())
    filemenu.add_command(label="Save As...", command=lambda: saveAs())
    filemenu.add_separator()
    filemenu.add_command(label="Exit Pyxcel", command=Main.window.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    sortmenu = tk.Menu(menubar, tearoff=0)
    sortmenu.add_command(label="Reset", command=lambda: resetSort())
    menubar.add_cascade(label="Sort", menu=sortmenu)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Revert to Original", command=lambda: revertToOriginal())
    editmenu.add_command(label="Add Row", command=lambda: addRow())
    editmenu.add_command(label="Add Column", command=lambda: addColumn())
    menubar.add_cascade(label="Edit", menu=editmenu)


def headerRightClickMenu(header):
    rightClickMenu = tk.Menu(Main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: showStats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sortArray(header))
    rightClickMenu.add_command(
        label="Delete Column", command=lambda: deleteColumn(header)
    )
    rightClickMenu.post(Main.window.winfo_pointerx(), Main.window.winfo_pointery())


def cellRightClickMenu(header, row_number):
    rightClickMenu = tk.Menu(Main.window, tearoff=0)
    rightClickMenu.add_command(label="Show Stats", command=lambda: showStats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sortArray(header))
    rightClickMenu.add_command(
        label="Delete Row", command=lambda: deleteRow(row_number)
    )
    rightClickMenu.add_command(
        label="Delete Column", command=lambda: deleteColumn(header)
    )
    rightClickMenu.post(Main.window.winfo_pointerx(), Main.window.winfo_pointery())


def initWindow():
    Main.window = OpenWindow("1000x500", "Pyxcel")
    Main.context = {"data": [], "sortKey": "", "sortReverse": False, "file": ""}
    # put save if ctrl + s is pressed
    Main.window.bind("<Control-s>", lambda _: save())
    displayArray()
    Main.window.mainloop()


def clearWindow():
    for widget in Main.window.winfo_children():
        widget.destroy()
    Main.window.update()


def displayArray():
    clearWindow()
    makeMenu()
    if len(Main.context["data"]) == 0:
        text = tk.Label(Main.window, text="No data to display.")
        text.place(relx=0.5, rely=0.5, anchor="center")
    else:
        createTable()
    Main.window.update()


def sortArray(column):
    if Main.context["sortKey"] == column:
        Main.context["data"].sort(
            key=lambda x: x[column], reverse=not Main.context["sortReverse"]
        )
        Main.context["sortReverse"] = not Main.context["sortReverse"]
    else:
        Main.context["data"].sort(key=lambda x: x[column])
        Main.context["sortReverse"] = False
    Main.context["sortKey"] = column
    displayArray()


def resetSort():
    Main.context["sortKey"] = ""
    Main.context["sortReverse"] = False
    displayArray()


def showStats(column):
    displayArray()
    windowStats = OpenWindow("300x300", "Stats")
    # get type of column
    typeStat = fileParser.columnType(Main.context["data"], column)
    print(typeStat)
    if typeStat == int or typeStat == float:
        min = Main.context["data"][0][column]
        max = Main.context["data"][0][column]
        avg = 0
        for i in Main.context["data"]:
            if min > i[column]:
                min = i[column]
            if max < i[column]:
                max = i[column]
            avg += i[column]
        avg /= len(Main.context["data"])
        text = tk.Label(
            windowStats,
            text="Min : " + str(min) + "\nMax : " + str(max) + "\nAvg : " + str(avg),
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()
    elif typeStat == bool:
        true = 0
        false = 0
        for i in Main.context["data"]:
            if i[column]:
                true += 1
            else:
                false += 1
        text = tk.Label(
            windowStats,
            text="True : "
            + str(true / len(Main.context["data"]) * 100)
            + "%\nFalse : "
            + str(false / len(Main.context["data"]) * 100)
            + "%",
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()
    elif typeStat == list or typeStat == str:
        min = len(Main.context["data"][0][column])
        max = len(Main.context["data"][0][column])
        avg = 0
        for i in Main.context["data"]:
            if min > len(i[column]):
                min = len(i[column])
            if max < len(i[column]):
                max = len(i[column])
            avg += len(i[column])
        avg /= len(Main.context["data"])
        min_text = (
            "Min " + ("list" if typeStat == list else "string") + " size: " + str(min)
        )
        max_text = (
            "\nMax " + ("list" if typeStat == list else "string") + " size: " + str(max)
        )
        avg_text = (
            "\nAvg " + ("list" if typeStat == list else "string") + " size: " + str(avg)
        )
        text = tk.Label(windowStats, text=min_text + max_text + avg_text)
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()


def addRow():
    """Adds a row to the table."""
    Main.context["data"].append({key: "" for key in Main.context["data"][0]})
    displayArray()


def addColumn():
    """Adds a column to the table."""
    for row in Main.context["data"]:
        row["new_column"] = ""
    displayArray()


def updateHeaderCellOnFocusOut(previous, sv):
    """
    Updates the context array when a header cell is modified.

    parameters
    ----------
    previous: str
        The previous value of the header.
    sv: StringVar
        The Tkinter StringVar object containing the new header name.
    """
    for row in Main.context["data"]:
        row[sv.get()] = row.pop(previous)

    # Need to update the header name on the frontend
    displayArray()


def deleteRow(row_number):
    Main.context["data"].pop(row_number)
    displayArray()


def deleteColumn(header):
    for row in Main.context["data"]:
        row.pop(header)
    displayArray()


def newFile():
    Main.context = {
        "data": [{"New column": ""}],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
    }
    displayArray()
