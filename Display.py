import tkinter as tk
from tkinter import filedialog
import fileParser
import Main


def OpenWindow(size, title):
    w = tk.Tk()
    w.geometry(size)
    w.title(title)
    return w


def createTable():
    numRows = max(len(Main.context["array"]) + 1, 10)
    numColumns = len(Main.context["array"][0])
    Main.context["cell_vars"] = []  # Contains the value of each cell

    for i in range(numColumns):
        Main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        Main.window.grid_rowconfigure(i, weight=1)

    for i, value in enumerate(Main.context["array"][0]):
        tmp = value
        if tmp == Main.context["sortKey"]:
            if Main.context["sortReverse"]:
                tmp += " ▼"
            else:
                tmp += " ▲"
        label = tk.Label(Main.window, text=tmp)
        label.grid(row=0, column=i)
        label.bind("<Button-1>", lambda e, x=value: sortArray(x))
        if type(Main.context["array"][0][value]) != str:
            label.bind("<Button-3>", lambda e, x=value: makeRightClickMenu(x))

    for i, row in enumerate(Main.context["array"]):
        row_vars = {}
        for j, (key, value) in enumerate(row.items()):
            cell_content = tk.StringVar(value=value)
            cell = tk.Entry(Main.window, textvariable=cell_content)
            cell.grid(row=i + 1, column=j)
            row_vars[key] = cell_content

        Main.context["cell_vars"].append(row_vars)


def openFile():
    file = filedialog.askopenfile()
    Main.context = {
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
        fileParser.getColumns(Main.context)
        displayArray()


def makeMenu():
    menubar = tk.Menu(Main.window)
    Main.window.config(menu=menubar)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: print("New"))
    filemenu.add_command(label="Open", command=lambda: openFile())
    filemenu.add_command(label="Save", command=lambda: fileParser.save())
    filemenu.add_command(label="Save as...", command=lambda: print("Save as..."))
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
            text="True : "
            + str(true / len(Main.context["array"]) * 100)
            + "%\nFalse : "
            + str(false / len(Main.context["array"]) * 100)
            + "%",
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
            text="Taille min : "
            + str(min)
            + "\nTaille max : "
            + str(max)
            + "\nTaille moyenne : "
            + str(avg),
        )
        text.place(relx=0.5, rely=0.5, anchor="center")
        text.pack()
