import tkinter as tk
from tkinter import filedialog

import file_parser
import main


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
    main.context["array"][row][column] = file_parser.stringToTypeOfValue(sv.get())


def createTable():
    numRows = max(len(main.context["array"]) + 1, 10)
    numColumns = len(main.context["array"][0])

    # Contains the reference to each cell entry
    main.context["cell_vars"] = []

    for i in range(numColumns):
        main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        main.window.grid_rowconfigure(i, weight=1)

    for i, header in enumerate(main.context["array"][0]):
        tmp = header
        if tmp == main.context["sortKey"]:
            if main.context["sortReverse"]:
                tmp += " ▼"
            else:
                tmp += " ▲"
        label = tk.Label(main.window, text=tmp)
        label.grid(row=0, column=i)
        label.bind("<Button-1>", lambda _, x=header: sortArray(x))
        if not isinstance(main.context["array"][0][header], str):
            label.bind("<Button-3>", lambda _, x=header: makeRightClickMenu(x))

    for i, row in enumerate(main.context["array"]):
        row_vars = {}
        for j, (key, value) in enumerate(row.items()):
            cell_content = tk.StringVar(value=value)
            cell_content.trace_add(
                "write",
                lambda *_, row=i, column=key, sv=cell_content: updateContextOnCellChange(row, column, sv),
            )
            cell = tk.Entry(main.window, textvariable=cell_content)
            cell.grid(row=i + 1, column=j)
            row_vars[key] = cell_content

        main.context["cell_vars"].append(row_vars)


def openFile():
    file = filedialog.askopenfile()
    main.context = {
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
        main.context["file"] = file.name
        if ext == "csv":
            main.context["array"] = file_parser.csvToArray(file.name)
        elif ext == "json":
            main.context["array"] = file_parser.jsonFileToArray(file.name)
        elif ext == "xml":
            main.context["array"] = file_parser.xmlToArray(file.name)
        elif ext == "yaml":
            main.context["array"] = file_parser.yamlToArray(file.name)
        else:
            print("ERROR : File type not supported")
            main.context["array"] = []

        main.context["original"] = main.context["array"]

        file_parser.getColumns(main.context)
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

    for i, row in enumerate(main.context["array"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = main.context["cell_vars"][i][key].get()

    main.context["file"] = file.name
    if ext == "csv":
        file_parser.arrayToCsv(main.context["array"], file.name)
    elif ext == "json":
        file_parser.arrayToJson(main.context["array"], file.name)
    elif ext == "xml":
        file_parser.arrayToXml(main.context["array"], file.name)
    elif ext == "yaml":
        file_parser.arrayToYaml(main.context["array"], file.name)
    else:
        print("ERROR : File type not supported")
        main.context["array"] = []
    file_parser.getColumns(main.context)
    displayArray()


def save():
    if main.context["file"] == "":
        saveAs()
        return
    ext = main.context["file"].split(".")[-1]

    for i, row in enumerate(main.context["array"]):
        for _, (key, _) in enumerate(row.items()):
            row[key] = main.context["cell_vars"][i][key].get()

    if ext == "csv":
        file_parser.arrayToCsv(main.context["array"], main.context["file"])
    elif ext == "json":
        file_parser.arrayToJson(main.context["array"], main.context["file"])
    elif ext == "xml":
        file_parser.arrayToXml(main.context["array"], main.context["file"])
    elif ext == "yaml":
        file_parser.arrayToYaml(main.context["array"], main.context["file"])
    else:
        print("ERROR : File type not supported")


def makeMenu():
    menubar = tk.Menu(main.window)
    main.window.config(menu=menubar)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: print("New"))
    filemenu.add_command(label="Open", command=lambda: openFile())
    filemenu.add_command(label="Save", command=lambda: save())
    filemenu.add_command(label="Save as...", command=lambda: saveAs())
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=main.window.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    sortmenu = tk.Menu(menubar, tearoff=0)
    sortmenu.add_command(label="reset", command=lambda: resetSort())
    menubar.add_cascade(label="Sort", menu=sortmenu)
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Add column", command=lambda: print("Add column"))
    editmenu.add_command(label="Add row", command=lambda: addRow())
    menubar.add_cascade(label="Edit", menu=editmenu)


def makeRightClickMenu(column):
    rightClickMenu = tk.Menu(main.window, tearoff=0)
    rightClickMenu.add_command(label="Show stats", command=lambda: showStats(column))
    rightClickMenu.post(main.window.winfo_pointerx(), main.window.winfo_pointery())


def initWindow():
    main.window = OpenWindow("1000x500", "Pyxcel")
    main.context = {
        "array": [],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
        "columns": [],
    }
    # put save if ctrl + s is pressed
    main.window.bind("<Control-s>", lambda _: save())
    displayArray()
    main.window.mainloop()


def clearWindow():
    # don t clear the menu
    for widget in main.window.winfo_children():
        widget.destroy()
    main.window.update()


def displayArray():
    clearWindow()
    makeMenu()
    if len(main.context["array"]) == 0:
        text = tk.Label(main.window, text="No data to display")
        text.place(relx=0.5, rely=0.5, anchor="center")
    else:
        createTable()
    main.window.update()


def sortArray(column):
    if main.context["sortKey"] == column:
        main.context["array"].sort(key=lambda x: x[column], reverse=not main.context["sortReverse"])
        main.context["sortReverse"] = not main.context["sortReverse"]
    else:
        main.context["array"].sort(key=lambda x: x[column])
        main.context["sortReverse"] = False
    main.context["sortKey"] = column
    displayArray()


def resetSort():
    main.context["sortKey"] = ""
    main.context["sortReverse"] = False
    displayArray()


def addRow():
    main.context["array"].append({})
    print(main.context["array"])
    displayArray()


def showStats(column):
    displayArray()
    windowStats = OpenWindow("300x300", "Stats")
    # get type of column
    typeStat = type(main.context["array"][0][column])
    if typeStat == int or typeStat == float:
        min = main.context["array"][0][column]
        max = main.context["array"][0][column]
        avg = 0
        for i in main.context["array"]:
            if min > i[column]:
                min = i[column]
            if max < i[column]:
                max = i[column]
            avg += i[column]
        avg /= len(main.context["array"])
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
        for i in main.context["array"]:
            if i[column]:
                true += 1
            else:
                false += 1
        text = tk.Label(
            windowStats,
            text="True : " + str(true / len(main.context["array"]) * 100) + "%\nFalse : " + str(false / len(main.context["array"]) * 100) + "%",
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()
    elif typeStat == list:
        min = len(main.context["array"][0][column])
        max = len(main.context["array"][0][column])
        avg = 0
        for i in main.context["array"]:
            if min > len(i[column]):
                min = len(i[column])
            if max < len(i[column]):
                max = len(i[column])
            avg += len(i[column])
        avg /= len(main.context["array"])
        text = tk.Label(
            windowStats,
            text="Min list size : " + str(min) + "\nMax list size: " + str(max) + "\nAvg list size: " + str(avg),
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
