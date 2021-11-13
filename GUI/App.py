from datetime import date
from tkinter import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sys
import neo4j
sys.path.insert(0, '../neo4jDB-populator')
from main import PopulateDB as pop

MAIN_WIDTH = 1000
MAIN_HEIGHT = 650

root = Tk()
root.title("Covid tracker")
root.geometry("{}x{}".format(MAIN_WIDTH, MAIN_HEIGHT))
root.resizable(False, False)

top_frame = Frame(root, width=1000, height=50)
main_frame = Frame(root, width=600, height=600)
query_frame = Frame(root, width=400, height=600)

# layout all of the main containers

top_frame.grid(row=0, columnspan=2, sticky="ew")
main_frame.grid(row=1, column=1, sticky="nsew")
query_frame.grid(row=1, column=0, sticky="ew")

# layout query frame

l_box_frm_query = Frame(query_frame, width=150, height=200, padx=5, pady=5)
button_frm_query = Frame(query_frame, width=150, height=50, padx=5, pady=5)
parameters_frm_query = Frame(query_frame, width=250, height=250, padx=5, pady=5)

l_box_frm_query.grid(row=0, column=0)
button_frm_query.grid(row=1, column=0)
parameters_frm_query.grid(row=0, column=1)
additional_widgets = []

# label on top_frame
label_title = Label(top_frame, text="Welcome to the TrackingAPP.")
label_title.grid(rowspan=2, row=0, column=0)

# objects for l_box_frm_query
label_query = Label(l_box_frm_query, text="List of available queries:")
label_query.grid(row=0, column=0)

listbox_query = Listbox(l_box_frm_query, selectmode=SINGLE)
listbox_query.insert(1, "Trend covid")
listbox_query.insert(2, "Vaccine efficacy")
listbox_query.insert(3, "Dangerous places")
listbox_query.insert(4, "Vaccinates per age")

listbox_query.grid(row=1, column=0)


def select_item_query():
    for item in additional_widgets:
        item.destroy()
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
        elif item == 3:
            execute_vaccinates_per_age(populator)
    populator.close()


def execute_vaccinates_per_age(db_object):
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    result = db_object.query_vaccinates_per_age(db_object)
    data_from_query = {"ages": [element for element in result],
                       "vaccination ratios": [result[element] for element in result]}
    data_to_plot = pd.DataFrame(data_from_query, columns=["ages", "vaccination ratios"])
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax1 = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, main_frame)
    canvas.get_tk_widget().grid(sticky="nsew")
    data_to_plot = data_to_plot[['ages', 'vaccination ratios']].groupby("ages").sum()
    data_to_plot.plot(kind='bar', legend=True, ax=ax1)
    ax1.set_title('percentage of people vaccinated per age range')


def select_place(populator):
    options = ['Roma','Milano','Napoli']
    variable = StringVar(parameters_frm_query)
    variable.set(options[2])
    w = OptionMenu(parameters_frm_query, variable, *options)
    w.grid(row=0, column=0)
    additional_widgets.append(w)

    def selection():
        city = variable.get()
        execute_dangerous_places(populator, city)
    button = Button(parameters_frm_query, text="OK", command=selection)
    button.grid(row = 1, column = 0)
    additional_widgets.append(button)


def perc_normalization(percentages):
    max_perc = max(percentages) if max(percentages) != 0 else 1
    new_percentages = [item / max_perc for item in percentages]
    return new_percentages


def execute_dangerous_places(db_object, city):
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
    result = db_object.query_dangerous_places(db_object, city)
    infected_places = {}
    infected_places["name_space"] = []
    infected_places["danger level"] = []
    for element in result:
        infected_places["name_space"].append(element[1])
        infected_places["danger level"].append(element[0])
    infected_places["danger level"] = perc_normalization(infected_places["danger level"])
    data_to_plot = pd.DataFrame(infected_places, columns=["name_space", "danger level"])
    figure = plt.Figure(figsize=(6, 6), dpi=100, constrained_layout=True)
    ax1 = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, main_frame)
    canvas.get_tk_widget().grid(sticky="nsew")
    data_to_plot = data_to_plot[['name_space', 'danger level']].groupby('name_space').sum()
    data_to_plot.plot(kind='bar', legend=True, ax=ax1)
    ax1.set_title('dangerous places')


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
    data_from_query = {"month": [date(day=1, month=index[1], year=index[2]) for index in result],
                       "infection ratio": [index[0] for index in result]}
    data_to_plot = pd.DataFrame(data_from_query, columns=["month", "infection ratio"])
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax1 = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, main_frame)
    canvas.get_tk_widget().grid(sticky="nsew")
    data_to_plot = data_to_plot[['month', 'infection ratio']].groupby("month").sum()
    print(data_to_plot.head())
    data_to_plot.plot(kind='line', legend=True, ax=ax1)
    ax1.set_title('month vs infection ratio')


canvas = None
btn_query = Button(button_frm_query, text='Execute', command=select_item_query)
btn_query.grid()

plt.rcParams.update({'font.size': 7})
root.mainloop()

