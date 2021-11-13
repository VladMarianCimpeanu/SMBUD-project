from tkinter import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sys
import neo4j
sys.path.insert(0, '../neo4jDB-populator')
from main import PopulateDB as pop

MAIN_WIDTH = 1000
MAIN_HEIGHT = 550

root = Tk()
root.title("Covid tracker")
root.geometry("{}x{}".format(MAIN_WIDTH, MAIN_HEIGHT))
root.resizable(False, False)

top_frame = Frame(root, width=1000, height=50)
main_frame = Frame(root, bg='yellow', width=600, height=500)
cmd_frame = Frame(root, bg='red', width=400, height=250)
query_frame = Frame(root, bg='pink', width=400, height=250)

# layout all of the main containers

top_frame.grid(row=0, columnspan=2, sticky="ew")
main_frame.grid(row=1, rowspan=2, column=1, sticky="nsew")
cmd_frame.grid(row=1, column=0, sticky="ew")
query_frame.grid(row=2, column=0, sticky="ew")

# layout query frame

l_box_frm_query = Frame(query_frame, bg = "black", width=150, height=200, padx=5, pady=5)
button_frm_query = Frame(query_frame, bg="green", width=150, height=50, padx=5, pady=5)
parameters_frm_query = Frame(query_frame, bg="blue", width=250, height=250, padx=5, pady=5)

l_box_frm_query.grid(row=0, column=0)
button_frm_query.grid(row=1, column=0)
parameters_frm_query.grid(column=1, row=0, rowspan=2)

# layout commands frame
l_box_frm_cmd = Frame(cmd_frame, bg="black", width=150, height=200)
button_frm_cmd = Frame(cmd_frame, bg="green", width=150, height=50)
parameters_frm_cmd = Frame(cmd_frame, bg="blue", width=250, height=250)
l_box_frm_cmd.grid(row=0, column=0)
button_frm_cmd.grid(row=1, column=0)
parameters_frm_cmd.grid(column=1, row=0, rowspan=2)

# label on top_frame
label_title = Label(top_frame, text = "Welcome to the TrackingAPP. Please select a list of options below :")#,font = ('Default', 12))
label_title.grid()

# objects for l_box_frm_cmd
label_cmd = Label(l_box_frm_cmd, text = "List of available commands:")
label_cmd.grid(row=0,column=0)

listbox_cmd = Listbox(l_box_frm_cmd, selectmode=SINGLE)
listbox_cmd.insert(1, "Cmd 1")
listbox_cmd.insert(2, "Cmd 2")
listbox_cmd.insert(3, ".... 3")
listbox_cmd.insert(4, "Query 4")
listbox_cmd.insert(5, "Query 5")
listbox_cmd.grid(row=1,column=0)


def select_item_cmd():
    for i in listbox_cmd.curselection():
        print(listbox_cmd.get(i))


btn_cmd = Button(button_frm_cmd, text='Execute', command=select_item_cmd)
btn_cmd.grid()

# objects for l_box_frm_query
label_query = Label(l_box_frm_query, text = "List of available queries:")
label_query.grid(row=0, column=0)

listbox_query = Listbox(l_box_frm_query, selectmode=SINGLE)
listbox_query.insert(1, "Trend covid")
listbox_query.insert(2, "Vaccine efficacy")
listbox_query.insert(3, "Dangerous places")
listbox_query.insert(4, "Query 4")
listbox_query.insert(5, "Query 5")
listbox_query.grid(row=1, column=0)


def select_item_query():
    with open("../neo4jDB-populator/password.txt", "r") as pass_reader:
        neo4j_password = pass_reader.readline().split()[0]
        populator = pop("bolt://localhost:7687", "neo4j", neo4j_password)
    for item in listbox_query.curselection():
        if item == 0:
            execute_trend_covid(populator)
        elif item == 1:
            execute_vaccine_efficacy(populator)
        elif item == 2:
            select_place(populator)
    populator.close()
    
def select_place(populator):
    options = ['Roma','Milano','Napoli']
    variable = StringVar(parameters_frm_query)
    variable.set(options[2])
    w = OptionMenu(parameters_frm_query, variable, *options)
    w.grid(row = 0, column = 0)
    def selection():
        city = None
        city = variable.get()
        execute_dangerous_places(populator,city)
    button = Button(parameters_frm_query, text="OK", command=selection)
    button.grid(row = 1, column = 0)

def execute_dangerous_places(db_object,city):
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    result = db_object.query_dangerous_places(db_object, city)
    


def execute_vaccine_efficacy(db_object):
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    result = db_object.query_vaccines_efficacy(db_object)
    result_converted = {}
    result_converted["vaccines"] = []
    result_converted["efficacy"] = []
    for vaccine in result:
        result_converted["vaccines"].append(vaccine.split("Efficacy")[0])
        result_converted["efficacy"].append(result[vaccine])
    data_to_plot = pd.DataFrame(result_converted, columns=["vaccines", "efficacy"])
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax1 = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, main_frame)
    canvas.get_tk_widget().grid(sticky="nsew")
    data_to_plot = data_to_plot[['vaccines', 'efficacy']].groupby('vaccines').sum()
    data_to_plot.plot(kind='bar', legend=True, ax=ax1)
    ax1.set_title('efficacy of vaccines')


def execute_trend_covid(db_object):
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    result = db_object.query_trend_covid(db_object)
    data_from_query = {"month": [str(index[1]) + "/" + str(index[2]) for index in result],
                       "infection ratio": [index[0] for index in result]}
    data_to_plot = pd.DataFrame(data_from_query, columns=["month", "infection ratio"])
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax1 = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, main_frame)
    canvas.get_tk_widget().grid(sticky="nsew")
    data_to_plot = data_to_plot[['month', 'infection ratio']].groupby('month').sum()
    data_to_plot.plot(kind='line', legend=True, ax=ax1)
    ax1.set_title('month vs infection ratio')

canvas = None
btn_query = Button(button_frm_query, text='Execute', command=select_item_query)
btn_query.grid()

plt.rcParams.update({'font.size': 8})
root.mainloop()

