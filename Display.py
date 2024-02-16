import tkinter as tk
from tkinter import filedialog
import fileParser
import Main


def OpenWindow(size, title):
    w = tk.Tk()
    w.geometry(size)
    w.title(title)
    return w


def updateContextOnCellChange(row, column, sv):
    """
    Updates the context array when a cell is modified.

    Parameters
    ----------
    row: int
        The number of the cell's row.
    column: int
        The number of the cell's column.
    sv: StringVar
        The value of the cell.
    """
    Main.context["array"][row][column] = fileParser.stringToTypeOfValue(sv.get())


def revertToOriginal():
    """
    Reverts the array to its original state (before any modification).
    """
    # get type of file csv, json, xml, yaml
    ext = Main.context["file"].split(".")[-1]
    Main.context["file"] = Main.context["file"]
    if ext == "csv":
        Main.context["array"] = fileParser.csvToArray(Main.context["file"])
    elif ext == "json":
        Main.context["array"] = fileParser.jsonFileToArray(Main.context["file"])
    elif ext == "xml":
        Main.context["array"] = fileParser.xmlToArray(Main.context["file"])
    elif ext == "yaml":
        Main.context["array"] = fileParser.yamlToArray(Main.context["file"])
    displayArray()


def createTable():
    # copy the original array to be able to revert to it without linking the two arrays
    Main.context["original"] = Main.context["array"].copy()

    numRows = max(len(Main.context["array"]) + 1, 10)
    numColumns = len(Main.context["array"][0])

    # Contains the reference to each cell entry
    Main.context["cell_vars"] = []

    for i in range(numColumns):
        Main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        Main.window.grid_rowconfigure(i, weight=1)

    # Keep track of the headers stringvars to update them on change
    for i, header in enumerate(Main.context["array"][0]):
        tmp = header
        # TODO: add sort icons with entries (maybe with a button on the right of the header?)
        # if tmp == Main.context["sortKey"]:
        #    if Main.context["sortReverse"]:
        #        tmp += " ▼"
        #    else:
        #        tmp += " ▲"
        header_sv = tk.StringVar(value=tmp)
        header_entry = tk.Entry(Main.window, textvariable=header_sv)
        header_entry.bind(
            "<FocusOut>",
            lambda *_, previous=header, sv=header_sv,: updateHeaderCellOnFocusOut(
                previous, sv
            ),
        )
        header_entry.grid(row=0, column=i)
        header_entry.bind("<Button-3>", lambda _, x=header: headerRightClickMenu(x))

    for i, row in enumerate(Main.context["array"]):
        row_vars = {}
        for j, (key, value) in enumerate(row.items()):
            cell_content = tk.StringVar(value=value)
            cell_content.trace_add(
                "write",
                lambda *_,
                row=i,
                column=key,
                sv=cell_content: updateContextOnCellChange(row, column, sv),
            )
            cell = tk.Entry(Main.window, textvariable=cell_content)
            cell.grid(row=i + 1, column=j)
            cell.bind("<Button-3>", lambda _, x=key, row=i: cellRightClickMenu(x, row))
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
    }
    if file:
        # get type of file csv, json, xml, yaml
        ext = file.name.split(".")[-1]
        Main.context["file"] = file.name
        if ext == "csv":
            Main.context["array"] = fileParser.csvToArray(file.name)
        elif ext == "json":
            Main.context["array"] = fileParser.jsonFileToArray(file.name)
        elif ext == "xml":
            Main.context["array"] = fileParser.xmlToArray(file.name)
        elif ext == "yaml":
            Main.context["array"] = fileParser.yamlToArray(file.name)
        else:
            print("ERROR : File type not supported")
            Main.context["array"] = []
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
        fileParser.arrayToCsv(Main.context["array"], file.name)
    elif ext == "json":
        fileParser.arrayToJson(Main.context["array"], file.name)
    elif ext == "xml":
        fileParser.arrayToXml(Main.context["array"], file.name)
    elif ext == "yaml":
        fileParser.arrayToYaml(Main.context["array"], file.name)
    else:
        print("ERROR : File type not supported")
        Main.context["array"] = []
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
        fileParser.arrayToCsv(Main.context["array"], Main.context["file"])
    elif ext == "json":
        fileParser.arrayToJson(Main.context["array"], Main.context["file"])
    elif ext == "xml":
        fileParser.arrayToXml(Main.context["array"], Main.context["file"])
    elif ext == "yaml":
        fileParser.arrayToYaml(Main.context["array"], Main.context["file"])
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
    editmenu.add_command(label="Revert to original", command=lambda: revertToOriginal())
    editmenu.add_command(label="Add row", command=lambda: addRow())
    editmenu.add_command(label="Add column", command=lambda: addColumn())
    menubar.add_cascade(label="Edit", menu=editmenu)


def headerRightClickMenu(header):
    rightClickMenu = tk.Menu(Main.window, tearoff=0)
    rightClickMenu.add_command(label="Show stats", command=lambda: showStats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sortArray(header))
    rightClickMenu.post(Main.window.winfo_pointerx(), Main.window.winfo_pointery())


def cellRightClickMenu(header, row_number):
    rightClickMenu = tk.Menu(Main.window, tearoff=0)
    rightClickMenu.add_command(label="Show stats", command=lambda: showStats(header))
    rightClickMenu.add_command(label="Sort", command=lambda: sortArray(header))
    rightClickMenu.add_command(
        label="Delete row", command=lambda: deleteRow(row_number)
    )
    rightClickMenu.post(Main.window.winfo_pointerx(), Main.window.winfo_pointery())


def initWindow():
    Main.window = OpenWindow("1000x500", "Pyxcel")
    Main.context = {"array": [], "sortKey": "", "sortReverse": False, "file": ""}
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
        Main.context["array"].sort(
            key=lambda x: x[column], reverse=not Main.context["sortReverse"]
        )
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
            text="True : "
            + str(true / len(Main.context["array"]) * 100)
            + "%\nFalse : "
            + str(false / len(Main.context["array"]) * 100)
            + "%",
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
        windowStats.mainloop()
    elif typeStat == list or typeStat == str:
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
    Main.context["array"].append({key: "" for key in Main.context["array"][0]})
    displayArray()


def addColumn():
    """Adds a column to the table."""
    for row in Main.context["array"]:
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
    for row in Main.context["array"]:
        row[sv.get()] = row.pop(previous)

    # Need to update the header name on the frontend
    displayArray()


def deleteRow(row_number):
    Main.context["array"].pop(row_number)
    displayArray()
