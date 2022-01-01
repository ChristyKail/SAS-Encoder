import sassy
import csv_loader
import tkinter as tk


# TODO all the UI stuff!

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        label_input_file = tk.Label(self, text="Input ALE")
        entry_input_file = tk.Entry(self, )

        label_input_file.grid(column=0, row=1, sticky="EW")


# processor = SASSY.Processor("/Users/christykail/Desktop/SAS/_WORKING.ALE", csv_loader.load_csv("default.sassy"))
