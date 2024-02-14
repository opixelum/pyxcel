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
    numRows = len(Main.context['array']) + 1 if len(Main.context['array']) + 1 > 10 else 10
    numColumns = len(Main.context['array'][0])
    for i in range(numColumns):
        Main.window.grid_columnconfigure(i, weight=1)
    for i in range(numRows):
        Main.window.grid_rowconfigure(i, weight=1)

    for i, value in enumerate(Main.context['array'][0]):
        tmp = value
        if tmp == Main.context['sortKey']:
            if Main.context['sortReverse']:
                tmp += ' ▼'
            else:
                tmp += ' ▲'
        button = tk.Button(Main.window, text=tmp, command=lambda x=value: sortArray(x))
        button.grid(row=0, column=i)

    for i in range(0, len(Main.context['array'])):
        for j, value in enumerate(Main.context['array'][i]):
            label = tk.Label(Main.window, text=str(Main.context['array'][i][value]))
            label.grid(row=i + 1, column=j)


def openFile():
    file = tk.filedialog.askopenfile()
    Main.context = {'array': [], 'sortKey': '', 'sortReverse': False}
    if file:
        # get type of file csv, json, xml, yaml
        ext = file.name.split('.')[-1]
        Main.context['file'] = file.name
        if ext == 'csv':
            Main.context['array'] = fileParser.csvToArray(file.name)
        elif ext == 'json':
            Main.context['array'] = fileParser.jsonFileToArray(file.name)
        elif ext == 'xml':
            Main.context['array'] = fileParser.xmlToArray(file.name)
        elif ext == 'yaml':
            # rajouter yaml
            Main.context['array'] = []
        else:
            print('ERROR : File type not supported')
            Main.context['array'] = []
        displayArray()


def makeMenu():
    menubar = tk.Menu(Main.window)
    Main.window.config(menu=menubar)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: print('New'))
    filemenu.add_command(label="Open", command=lambda: openFile())
    filemenu.add_command(label="Save", command=lambda: print('Save'))
    filemenu.add_command(label="Save as...", command=lambda: print('Save as...'))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=Main.window.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    sortmenu = tk.Menu(menubar, tearoff=0)
    sortmenu.add_command(label="reset", command=lambda: resetSort())
    menubar.add_cascade(label="Sort", menu=sortmenu)
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Add column", command=lambda: print('Add column'))
    editmenu.add_command(label="Add row", command=lambda: addRow())
    menubar.add_cascade(label="Edit", menu=editmenu)


def initWindow():
    Main.window = OpenWindow('1000x500', 'Pyxcel')
    Main.context = {'array': [], 'sortKey': '', 'sortReverse': False, 'file': '', 'columns': []}
    fileParser.getColumns(Main.context)
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
    if len(Main.context['array']) == 0:
        text = tk.Label(Main.window, text="No data to display")
        text.place(relx=0.5, rely=0.5, anchor='center')
    else:
        createTable()
    Main.window.update()


def sortArray(column):
    if Main.context['sortKey'] == column:
        Main.context['array'].sort(key=lambda x: x[column], reverse=not Main.context['sortReverse'])
        Main.context['sortReverse'] = not Main.context['sortReverse']
    else:
        Main.context['array'].sort(key=lambda x: x[column])
        Main.context['sortReverse'] = False
    Main.context['sortKey'] = column
    displayArray()


def resetSort():
    Main.context['sortKey'] = ''
    Main.context['sortReverse'] = False
    displayArray()


def addRow():
    Main.context['array'].append({})
    print(Main.context['array'])
    displayArray()
