#! /usr/local/bin/python3

import csv
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar

import sas_encoder
from first_run import first_run


def get_all_fonts():
    font_list = []
    directory_list = [
        os.path.join(os.path.expanduser('~'), "Library/Fonts"),
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental"
    ]

    for directory in directory_list:
        font_list = font_list + (os.listdir(directory))

    font_list = [x for x in font_list if not x.startswith(".")]

    return sorted(font_list)


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.attributes("-alpha", 1)
        self.title(f"Cinelab Film & Digital - SAS encoder - version {sas_encoder.__version__}")

        self.progress_bar_shown = False

        # noinspection PyTypeChecker
        self.columnconfigure(tuple(range(4)), weight=1, minsize=5, pad=10)
        # noinspection PyTypeChecker
        self.rowconfigure(tuple(range(8)), weight=1, pad=5)

        try:
            self.logo_image = tk.PhotoImage(file="CFD-Icon_Standard.png")
            self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(file="CFD-Icon_Standard.png"))

        except Exception as exception:
            print("Logo failed to load. Reason:", exception)

        else:
            self.label_logo = tk.Label(self, image=self.logo_image, pady=10)
            self.label_logo.grid(column=0, row=0, columnspan=4, sticky="EW")

        # the burnin frame
        self.frame_burnins = tk.LabelFrame(self, text="Burnin layout", padx=10, pady=10)

        self.entry_top_left = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_left.grid(column=0, row=1, sticky="EW")
        self.entry_top_center = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_center.grid(column=1, row=1, sticky="EW")
        self.entry_top_right = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_right.grid(column=2, row=1, sticky="EW")

        self.label_watermark = tk.Label(self.frame_burnins, text="Watermark")
        self.entry_watermark = tk.Entry(self.frame_burnins, width=20)

        self.label_watermark.grid(column=1, row=2, sticky="EW", pady=(10, 0))
        self.entry_watermark.grid(columnspan=3, column=0, row=3, sticky="EW", pady=(0, 10))

        self.entry_bottom_left = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_left.grid(column=0, row=4, sticky="EW")
        self.entry_bottom_center = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_center.grid(column=1, row=4, sticky="EW")
        self.entry_bottom_right = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_right.grid(column=2, row=4, sticky="EW")

        self.frame_burnins.grid(columnspan=4, column=0, row=1)

        # font
        self.label_font = tk.Label(self, text="Font")
        self.items_font = get_all_fonts()
        self.var_font = tk.StringVar()
        self.var_font.set(self.items_font[0])
        self.option_font = tk.OptionMenu(self, self.var_font, *self.items_font)
        self.label_font.grid(column=0, row=2, sticky="E")
        self.option_font.grid(columnspan=2, column=1, row=2, sticky="EW")

        # blanking
        self.label_blanking = tk.Label(self, text="Blanking (0 for none)")
        self.entry_blanking = tk.Entry(self, width=8)
        self.entry_blanking.insert(0, "2.39")
        self.label_blanking.grid(column=0, row=3, sticky="E")
        self.entry_blanking.grid(column=1, row=3, sticky="W")

        # text size
        self.label_text_size = tk.Label(self, text="Text Size")
        self.entry_text_size = tk.Entry(self, width=8)
        self.entry_text_size.insert(0, "20")
        self.label_text_size.grid(column=2, row=3, sticky="E")
        self.entry_text_size.grid(column=3, row=3, sticky="W")

        # bitrate
        self.label_bitrate = tk.Label(self, text="Bitrate")
        self.entry_bitrate = tk.Entry(self, width=8)
        self.entry_bitrate.insert(0, "10000")
        self.label_bitrate.grid(column=0, row=4, sticky="E")
        self.entry_bitrate.grid(column=1, row=4, sticky="W")

        # padding
        self.label_padding = tk.Label(self, text="Padding")
        self.entry_padding = tk.Entry(self, width=8)
        self.entry_padding.insert(0, "5")
        self.label_padding.grid(column=2, row=4, sticky="E")
        self.entry_padding.grid(column=3, row=4, sticky="W")

        # watermark options
        # watermark position
        self.label_watermark_y_pos = tk.Label(self, text="Watermark position")
        self.entry_watermark_y_pos = tk.Entry(self, width=8)
        self.entry_watermark_y_pos.insert(0, "0.7")
        self.label_watermark_y_pos.grid(column=0, row=6, sticky="E")
        self.entry_watermark_y_pos.grid(column=1, row=6, sticky="W")

        # watermark opacity
        self.label_watermark_opacity = tk.Label(self, text="Watermark opacity")
        self.entry_watermark_opacity = tk.Entry(self, width=8)
        self.entry_watermark_opacity.insert(0, "0.2")
        self.label_watermark_opacity.grid(column=0, row=7, sticky="E")
        self.entry_watermark_opacity.grid(column=1, row=7, sticky="W")

        # watermark size
        self.label_watermark_size = tk.Label(self, text="Watermark size")
        self.entry_watermark_size = tk.Entry(self, width=8)
        self.entry_watermark_size.insert(0, "128")
        self.label_watermark_size.grid(column=0, row=8, sticky="E")
        self.entry_watermark_size.grid(column=1, row=8, sticky="W")

        # resolution
        self.label_resolution = tk.Label(self, text="Resolution")
        self.entry_resolution = tk.Entry(self, width=8)
        self.entry_resolution.insert(0, "1920x1080")
        self.label_resolution.grid(column=0, row=9, sticky="E")
        self.entry_resolution.grid(column=1, row=9, sticky="W")

        # MOS text
        self.label_mos_replacement = tk.Label(self, text="MOS TC")
        self.entry_mos_replacement = tk.Entry(self, width=8)
        self.entry_mos_replacement.insert(0, "MOS")
        self.label_mos_replacement.grid(column=2, row=6, sticky="E")
        self.entry_mos_replacement.grid(column=3, row=6, sticky="W")

        # processes
        self.label_processes = tk.Label(self, text="Processes")
        self.entry_processes = tk.Entry(self, width=8)
        self.entry_processes.insert(0, "8")
        self.label_processes.grid(column=2, row=7, sticky="E")
        self.entry_processes.grid(column=3, row=7, sticky="W")

        # encoding speed
        self.label_encoding_speed = tk.Label(self, text="Encoding speed")
        self.items_encoding_speed = ["ultrafast",
                                     "superfast",
                                     "veryfast",
                                     "faster",
                                     "fast",
                                     "medium",
                                     "slow",
                                     "slower",
                                     "veryslow"]
        self.var_encoding_speed = tk.StringVar()
        self.var_encoding_speed.set("veryfast")
        self.option_encoding_speed = tk.OptionMenu(self, self.var_encoding_speed, *self.items_encoding_speed)
        self.option_encoding_speed.config(width=4)
        self.label_encoding_speed.grid(column=2, row=8, sticky="E")
        self.option_encoding_speed.grid(column=3, row=8, sticky="W")

        # limit audio tracks
        self.label_limit_audio = tk.Label(self, text="Audio track limit")
        self.entry_limit_audio = tk.Entry(self, width=8)
        self.label_limit_audio.grid(column=2, row=9, sticky="E")
        self.entry_limit_audio.grid(column=3, row=9, sticky="W")

        # buttons frame
        self.frame_buttons = tk.Frame(self, pady=15)

        self.btn_load = tk.Button(self.frame_buttons, text="Load preset", command=lambda: self.load_preset())
        self.btn_generate = tk.Button(self.frame_buttons, text="Save preset", command=lambda: self.generate_preset())
        self.btn_execute = tk.Button(self.frame_buttons, text="Convert files", command=lambda: self.run_process())
        self.btn_load.grid(column=0, row=0, sticky="EW")
        self.btn_generate.grid(column=1, row=0, sticky="EW")
        self.btn_execute.grid(column=2, row=0, sticky="EW")

        self.frame_buttons.grid(columnspan=4, column=0, row=10)

        # progress bar
        self.progress_bar = Progressbar(self, orient="horizontal", length=100, mode='determinate')
        # self.progress_bar.grid(column=0, row=15, columnspan=4, sticky="EW", padx=10, pady=10)

        # load default preset
        if os.path.isdir("presets"):
            if os.path.isfile("presets/default.sasen"):
                self.load_preset("presets/default.sasen")

        else:
            os.mkdir("presets")

    def load_preset(self, filename=None):

        if not filename:
            file_name = filedialog.askopenfilename(parent=self, title="Select preset file",
                                                   initialdir="presets",
                                                   filetypes=[("SAS Encoder presets", "*.sasen")])
        else:
            file_name = filename

        if not file_name:
            return

        options_dict = sas_encoder.load_csv(file_name)

        self.entry_blanking.delete(0, 'end')
        self.entry_blanking.insert(0, options_dict["blanking"])

        self.entry_bitrate.delete(0, 'end')
        self.entry_bitrate.insert(0, options_dict["bitrate"])

        self.entry_text_size.delete(0, 'end')
        self.entry_text_size.insert(0, options_dict["text_size"])

        self.entry_padding.delete(0, 'end')
        self.entry_padding.insert(0, options_dict["padding"])

        self.var_font.set(options_dict["font"])

        self.entry_top_left.delete(0, 'end')
        self.entry_top_left.insert(0, options_dict["top_left"])

        self.entry_top_center.delete(0, 'end')
        self.entry_top_center.insert(0, options_dict["top_center"])

        self.entry_top_right.delete(0, 'end')
        self.entry_top_right.insert(0, options_dict["top_right"])

        self.entry_bottom_left.delete(0, 'end')
        self.entry_bottom_left.insert(0, options_dict["bottom_left"])

        self.entry_bottom_center.delete(0, 'end')
        self.entry_bottom_center.insert(0, options_dict["bottom_center"])

        self.entry_bottom_right.delete(0, 'end')
        self.entry_bottom_right.insert(0, options_dict["bottom_right"])

        self.entry_mos_replacement.delete(0, 'end')
        self.entry_mos_replacement.insert(0, options_dict["mos_tc_replacement"])

        self.entry_processes.delete(0, 'end')
        self.entry_processes.insert(0, options_dict["threads"])

        self.var_encoding_speed.set(options_dict["encoding_speed"])

        self.entry_limit_audio.delete(0, 'end')
        self.entry_limit_audio.insert(0, options_dict["limit_audio_tracks"])

        self.entry_watermark.delete(0, 'end')
        self.entry_watermark.insert(0, options_dict["watermark"])
        self.entry_watermark_y_pos.delete(0, 'end')
        self.entry_watermark_y_pos.insert(0, options_dict["watermark_y_position"])
        self.entry_watermark_size.delete(0, 'end')
        self.entry_watermark_size.insert(0, options_dict["watermark_size"])
        self.entry_watermark_opacity.delete(0, 'end')
        self.entry_watermark_opacity.insert(0, options_dict["watermark_opacity"])

        self.entry_resolution.delete(0, 'end')
        self.entry_resolution.insert(0, options_dict["resolution"])

    def generate_preset(self):

        options_dict = self.compile_dict_from_ui()

        is_good, errors = sas_encoder.verify_options(options_dict)

        if not is_good:
            message = "\n\n".join([x for x in errors])
            messagebox.showwarning(title="Some errors occurred", message=message)
            return

        file_name = filedialog.asksaveasfilename(defaultextension='.sasen', initialdir="presets")
        if file_name:
            with open(file_name, "w") as file_handler:
                writer = csv.writer(file_handler)
                for key, value in options_dict.items():
                    writer.writerow([key, value])

    def run_process(self):
        file_name = filedialog.askopenfilename(parent=self, title="Select metadata ALE",
                                               filetypes=[("ALE files", "*.ale")])

        options_dict = self.compile_dict_from_ui()

        ale_data = sas_encoder.load_ale_as_df(file_name)

        is_good, errors = sas_encoder.verify_options(options_dict, ale_data)

        if not is_good:
            message = "\n\n".join([x for x in errors])
            messagebox.showwarning(title="Some errors occurred", message=message)
            return

        self.update()
        try:
            sas_encoder.Processor(file_name, options_dict, manager=self)
        except Exception as e:
            messagebox.showwarning(title="Some errors occurred", message=str(e))
        self.lift()

    def compile_dict_from_ui(self):

        options_dict = {

            "resolution": self.entry_resolution.get(),
            "blanking": self.entry_blanking.get(),
            "bitrate": self.entry_bitrate.get(),

            "text_size": self.entry_text_size.get(),
            "padding": self.entry_padding.get(),

            "font": self.var_font.get(),
            "top_left": self.entry_top_left.get(),
            "top_center": self.entry_top_center.get(),
            "top_right": self.entry_top_right.get(),
            "bottom_left": self.entry_bottom_left.get(),
            "bottom_center": self.entry_bottom_center.get(),
            "bottom_right": self.entry_bottom_right.get(),

            "mos_tc_replacement": self.entry_mos_replacement.get(),

            "threads": self.entry_processes.get(),
            "encoding_speed": self.var_encoding_speed.get(),

            "limit_audio_tracks": self.entry_limit_audio.get(),

            "watermark": self.entry_watermark.get(),
            "watermark_y_position": self.entry_watermark_y_pos.get(),
            "watermark_size": self.entry_watermark_size.get(),
            "watermark_opacity": self.entry_watermark_opacity.get(),
        }

        return options_dict

    def update_progress(self, percent, suffix=""):

        if not self.progress_bar_shown:
            self.progress_bar_shown = True
            self.progress_bar.grid(column=0, row=15, columnspan=4, sticky="EW", padx=10, pady=10)

        self.progress_bar["value"] = percent
        self.update()

        if percent >= 100:
            self.progress_bar.grid_remove()
            self.progress_bar_shown = False


if __name__ == "__main__":
    first_run()

    app = App()
    app.mainloop()
