import tkinter as tk
from tkinter import filedialog

import file_parser
import Main


def OpenWindow(size, title):
    w = tk.Tk()
    w.geometry(size)
    w.title(title)
    return w


def updateContextOnCellChange(row, column, sv):
    """
    Update the context array when a cell is modified

    Parameters
    ----------
    row: int
        The number of the cell's row
    column: int
        The number of the cell's column
    sv: StringVar
        The value of the cell
    """
    Main.context["array"][row][column] = file_parser.stringToTypeOfValue(sv.get())


def createTable():
    numRows = max(len(Main.context["array"]) + 1, 10)
    numColumns = len(Main.context["array"][0])

    # Contains the reference to each cell entry
    Main.context["cell_vars"] = []

    for i in range(numColumns):
        Main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        Main.window.grid_rowconfigure(i, weight=1)

    for i, header in enumerate(Main.context["array"][0]):
        tmp = header
        if tmp == Main.context["sortKey"]:
            if Main.context["sortReverse"]:
                tmp += " ▼"
            else:
                tmp += " ▲"
        label = tk.Label(Main.window, text=tmp)
        label.grid(row=0, column=i)
        label.bind("<Button-1>", lambda _, x=header: sortArray(x))
        if not isinstance(Main.context["array"][0][header], str):
            label.bind("<Button-3>", lambda _, x=header: makeRightClickMenu(x))

    for i, row in enumerate(Main.context["array"]):
        row_vars = {}
        for j, (key, value) in enumerate(row.items()):
            cell_content = tk.StringVar(value=value)
            cell_content.trace_add(
                "write",
                lambda *_, row=i, column=key, sv=cell_content: updateContextOnCellChange(row, column, sv),
            )
            cell = tk.Entry(Main.window, textvariable=cell_content)
            cell.grid(row=i + 1, column=j)
            row_vars[key] = cell_content

        Main.context["cell_vars"].append(row_vars)


def openFile():
    file = filedialog.askopenfile()
    Main.context = {
        "original": [],
        "array": [],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
        "columns": [],
    }
    if file:
        # get type of file csv, json, xml, yaml
        ext = file.name.split(".")[-1]
        Main.context["file"] = file.name
        if ext == "csv":
            Main.context["array"] = file_parser.csvToArray(file.name)
        elif ext == "json":
            Main.context["array"] = file_parser.jsonFileToArray(file.name)
        elif ext == "xml":
            Main.context["array"] = file_parser.xmlToArray(file.name)
        elif ext == "yaml":
            Main.context["array"] = file_parser.yamlToArray(file.name)
        else:
            print("ERROR : File type not supported")
            Main.context["array"] = []

        Main.context["original"] = Main.context["array"]

        file_parser.getColumns(Main.context)
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

    for i, row in enumerate(Main.context["array"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = Main.context["cell_vars"][i][key].get()

    Main.context["file"] = file.name
    if ext == "csv":
        file_parser.arrayToCsv(Main.context["array"], file.name)
    elif ext == "json":
        file_parser.arrayToJson(Main.context["array"], file.name)
    elif ext == "xml":
        file_parser.arrayToXml(Main.context["array"], file.name)
    elif ext == "yaml":
        file_parser.arrayToYaml(Main.context["array"], file.name)
    else:
        print("ERROR : File type not supported")
        Main.context["array"] = []
    file_parser.getColumns(Main.context)
    displayArray()


def save():
    if Main.context["file"] == "":
        saveAs()
        return
    ext = Main.context["file"].split(".")[-1]

    for i, row in enumerate(Main.context["array"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = Main.context["cell_vars"][i][key].get()

    if ext == "csv":
        file_parser.arrayToCsv(Main.context["array"], Main.context["file"])
    elif ext == "json":
        file_parser.arrayToJson(Main.context["array"], Main.context["file"])
    elif ext == "xml":
        file_parser.arrayToXml(Main.context["array"], Main.context["file"])
    elif ext == "yaml":
        file_parser.arrayToYaml(Main.context["array"], Main.context["file"])
    else:
        print("ERROR : File type not supported")


def makeMenu():
    menubar = tk.Menu(Main.window)
    Main.window.config(menu=menubar)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: print("New"))
    filemenu.add_command(label="Open", command=lambda: openFile())
    filemenu.add_command(label="Save", command=lambda: save())
    filemenu.add_command(label="Save as...", command=lambda: saveAs())
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=Main.window.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    sortmenu = tk.Menu(menubar, tearoff=0)
    sortmenu.add_command(label="reset", command=lambda: resetSort())
    menubar.add_cascade(label="Sort", menu=sortmenu)
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Add column", command=lambda: print("Add column"))
    editmenu.add_command(label="Add row", command=lambda: addRow())
    menubar.add_cascade(label="Edit", menu=editmenu)


def makeRightClickMenu(column):
    rightClickMenu = tk.Menu(Main.window, tearoff=0)
    rightClickMenu.add_command(label="Show stats", command=lambda: showStats(column))
    rightClickMenu.post(Main.window.winfo_pointerx(), Main.window.winfo_pointery())


def initWindow():
    Main.window = OpenWindow("1000x500", "Pyxcel")
    Main.context = {
        "array": [],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
        "columns": [],
    }
    # put save if ctrl + s is pressed
    Main.window.bind("<Control-s>", lambda _: save())
    displayArray()
    Main.window.mainloop()


def clearWindow():
    # don t clear the menu
    for widget in Main.window.winfo_children():
        widget.destroy()
    Main.window.update()


def displayArray():
    clearWindow()
    makeMenu()
    if len(Main.context["array"]) == 0:
        text = tk.Label(Main.window, text="No data to display")
        text.place(relx=0.5, rely=0.5, anchor="center")
    else:
        createTable()
    Main.window.update()


def sortArray(column):
    if Main.context["sortKey"] == column:
        Main.context["array"].sort(key=lambda x: x[column], reverse=not Main.context["sortReverse"])
        Main.context["sortReverse"] = not Main.context["sortReverse"]
    else:
        Main.context["array"].sort(key=lambda x: x[column])
        Main.context["sortReverse"] = False
    Main.context["sortKey"] = column
    displayArray()


def resetSort():
    Main.context["sortKey"] = ""
    Main.context["sortReverse"] = False
    displayArray()


def addRow():
    Main.context["array"].append({})
    print(Main.context["array"])
    displayArray()


def showStats(column):
    displayArray()
    windowStats = OpenWindow("300x300", "Stats")
    # get type of column
    typeStat = type(Main.context["array"][0][column])
    if typeStat == int or typeStat == float:
        min = Main.context["array"][0][column]
        max = Main.context["array"][0][column]
        avg = 0
        for i in Main.context["array"]:
            if min > i[column]:
                min = i[column]
            if max < i[column]:
                max = i[column]
            avg += i[column]
        avg /= len(Main.context["array"])
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
        for i in Main.context["array"]:
            if i[column]:
                true += 1
            else:
                false += 1
        text = tk.Label(
            windowStats,
            text="True : " + str(true / len(Main.context["array"]) * 100) + "%\nFalse : " + str(false / len(Main.context["array"]) * 100) + "%",
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()
    elif typeStat == list:
        min = len(Main.context["array"][0][column])
        max = len(Main.context["array"][0][column])
        avg = 0
        for i in Main.context["array"]:
            if min > len(i[column]):
                min = len(i[column])
            if max < len(i[column]):
                max = len(i[column])
            avg += len(i[column])
        avg /= len(Main.context["array"])
        text = tk.Label(
            windowStats,
            text="Min list size : " + str(min) + "\nMax list size: " + str(max) + "\nAvg list size: " + str(avg),
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()