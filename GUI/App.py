from tkinter import *

MAIN_WIDTH = 1000
MAIN_HEIGHT = 550

root = Tk()
root.title("Covid tracker")
root.geometry("{}x{}".format(MAIN_WIDTH, MAIN_HEIGHT))
root.resizable(False, False)

top_frame = Frame(root, bg='cyan', width=1000, height=50, pady=3)
main_frame = Frame(root, bg='yellow', width=600, height=500, padx=3, pady=3)
cmd_frame = Frame(root, bg='red', width=400, height=250, pady=3)
query_frame = Frame(root, bg='pink', width=400, height=250, pady=3)

# layout all of the main containers

top_frame.grid(row=0, columnspan=2, sticky="ew")
main_frame.grid(row=1, rowspan=2, column=1, sticky="nsew")
cmd_frame.grid(row=1, column=0, sticky="ew")
query_frame.grid(row=2, column=0, sticky="ew")

# layout query frame

l_box_frm_query = Frame(query_frame, bg="black", width=150, height=200, padx=5, pady=5)
button_frm_query = Frame(query_frame, bg="green", width=150, height=50, padx=5, pady=5)
parameters_frm_query = Frame(query_frame, bg="blue", width=250, height=250, padx=5, pady=5)

l_box_frm_query.grid(row=0, column=0)
button_frm_query.grid(row=1, column=0)
parameters_frm_query.grid(column=1, row=0, rowspan=2)

# layout commands frame
l_box_frm_cmd = Frame(cmd_frame, bg="black", width=150, height=200, padx=5, pady=5)
button_frm_cmd = Frame(cmd_frame, bg="green", width=150, height=50, padx=5, pady=5)
parameters_frm_cmd = Frame(cmd_frame, bg="blue", width=250, height=250, padx=5, pady=5)

l_box_frm_cmd.grid(row=0, column=0)
button_frm_cmd.grid(row=1, column=0)
parameters_frm_cmd.grid(column=1, row=0, rowspan=2)

root.mainloop()

