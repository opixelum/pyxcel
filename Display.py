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

    for i, header in enumerate(Main.context["array"][0]):
        tmp = header
        if tmp == Main.context["sortKey"]:
            tmp += " ▼" if Main.context["sortReverse"] else " ▲"
        button = tk.Button(Main.window, text=tmp, command=lambda x=header: sortArray(x))
        button.grid(row=0, column=i)

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


def initWindow():
    Main.window = OpenWindow("1000x500", "Pyxcel")
    Main.context = {
        "array": [],
        "sortKey": "",
        "sortReverse": False,
        "file": "",
        "columns": [],
    }
    # Menu
    makeMenu()

    # Listbox
    displayArray()

    Main.window.mainloop()


def clearWindow():
    # don t clear the menu
    for widget in Main.window.winfo_children():
        if type(widget) != tk.Menu:
            widget.destroy()
    Main.window.update()


def displayArray():
    clearWindow()
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
