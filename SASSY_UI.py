import sassy
import csv_loader
import tkinter as tk
import os


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
        self.title("Cinelab Film & Digital - SASSY")

        self.columnconfigure(tuple(range(4)), weight=1, minsize=5, pad=10)
        self.rowconfigure(tuple(range(8)), weight=1, pad=5)

        try:
            self.logo_image = tk.PhotoImage(file="/Users/christykail/Cinelab_dev/CFD-Icon_Standard.png")

        except Exception as x:
            print("Logo failed to load")

        else:
            self.label_logo = tk.Label(self, image=self.logo_image, pady=10)
            self.label_logo.grid(column=0, row=0, columnspan=4, sticky="EW")

        # input file
        self.label_input_file = tk.Label(self, text="Input ALE")
        self.entry_input_file = tk.Entry(self, width=35)
        self.entry_input_file.insert(0, "")
        self.label_input_file.grid(column=0, row=1, sticky="E")
        self.entry_input_file.grid(columnspan=3, column=1, row=1, sticky="W")

        # font
        self.label_font = tk.Label(self, text="Font")

        self.items_font = get_all_fonts()
        self.var_font = tk.StringVar()
        self.var_font.set(self.items_font[0])
        self.option_font = tk.OptionMenu(self, self.var_font, *self.items_font)
        self.option_font.config(width=30)
        self.label_font.grid(column=0, row=2, sticky="E")
        self.option_font.grid(columnspan=3, column=1, row=2, sticky="W")

        # blanking and text size
        self.label_blanking = tk.Label(self, text="Blanking")
        self.entry_blanking = tk.Entry(self, width=6)
        self.entry_blanking.insert(0, "2.39")
        self.label_blanking.grid(column=0, row=3, sticky="E")
        self.entry_blanking.grid(column=1, row=3, sticky="W")

        self.label_text_size = tk.Label(self, text="Text Size")
        self.entry_text_size = tk.Entry(self, width=6)
        self.entry_text_size.insert(0, "20")
        self.label_text_size.grid(column=2, row=3, sticky="E")
        self.entry_text_size.grid(column=3, row=3, sticky="W")

        # bitrate and padding
        self.label_bitrate = tk.Label(self, text="Bitrate")
        self.entry_bitrate = tk.Entry(self, width=6)
        self.entry_bitrate.insert(0, "10000")
        self.label_bitrate.grid(column=0, row=4, sticky="E")
        self.entry_bitrate.grid(column=1, row=4, sticky="W")

        self.label_padding = tk.Label(self, text="Padding")
        self.entry_padding = tk.Entry(self, width=6)
        self.entry_padding.insert(0, "5")
        self.label_padding.grid(column=2, row=4, sticky="E")
        self.entry_padding.grid(column=3, row=4, sticky="W")

        # the burnin frame
        self.frame_burnins = tk.LabelFrame(self, text="Burnin layout")

        # burnin_frame.columnconfigure(tuple(range(3)), weight=1, minsize=5, pad=10)
        # burnin_frame.rowconfigure(tuple(range(8)), weight=1, pad=5)

        self.entry_top_left = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_left.grid(column=0, row=0, sticky="EW")
        self.entry_top_center = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_center.grid(column=1, row=0, sticky="EW")
        self.entry_top_right = tk.Entry(self.frame_burnins, width=14)
        self.entry_top_right.grid(column=2, row=0, sticky="EW")

        self.label_watermark = tk.Label(self.frame_burnins, text="Watermark")
        self.entry_watermark = tk.Entry(self.frame_burnins, width=20)

        self.label_watermark.grid(column=1, row=1, sticky="EW", pady=(10, 0))
        self.entry_watermark.grid(columnspan=3, column=0, row=2, sticky="EW", pady=(0, 10))

        self.entry_bottom_left = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_left.grid(column=0, row=4, sticky="EW")
        self.entry_bottom_center = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_center.grid(column=1, row=4, sticky="EW")
        self.entry_bottom_right = tk.Entry(self.frame_burnins, width=14)
        self.entry_bottom_right.grid(column=2, row=4, sticky="EW")

        self.frame_burnins.grid(columnspan=4, column=0, row=5)

        # watermark options
        self.label_watermark_y_pos = tk.Label(self, text="Watermark position")
        self.entry_watermark_y_pos = tk.Entry(self, width=6)
        self.entry_watermark_y_pos.insert(0, "0.7")
        self.label_watermark_y_pos.grid(column=0, row=6, sticky="E")
        self.entry_watermark_y_pos.grid(column=1, row=6, sticky="W")

        self.label_watermark_opacity = tk.Label(self, text="Watermark opacity")
        self.entry_watermark_opacity = tk.Entry(self, width=6)
        self.entry_watermark_opacity.insert(0, "0.2")
        self.label_watermark_opacity.grid(column=0, row=7, sticky="E")
        self.entry_watermark_opacity.grid(column=1, row=7, sticky="W")

        self.label_watermark_size = tk.Label(self, text="Watermark size")
        self.entry_watermark_size = tk.Entry(self, width=6)
        self.entry_watermark_size.insert(0, "128")
        self.label_watermark_size.grid(column=0, row=8, sticky="E")
        self.entry_watermark_size.grid(column=1, row=8, sticky="W")

        # encoder settings
        self.label_mos_replacement = tk.Label(self, text="MOS TC replacement")
        self.entry_mos_replacement = tk.Entry(self, width=6)
        self.entry_mos_replacement.insert(0, "MOS")
        self.label_mos_replacement.grid(column=2, row=6, sticky="E")
        self.entry_mos_replacement.grid(column=3, row=6, sticky="W")

        # encoder settings
        self.label_processes = tk.Label(self, text="Simultaneous processes")
        self.entry_processes = tk.Entry(self, width=6)
        self.entry_processes.insert(0, "8")
        self.label_processes.grid(column=2, row=7, sticky="E")
        self.entry_processes.grid(column=3, row=7, sticky="W")

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

        # the buttons at the bottom

        self.frame_buttons = tk.Frame(self)

        self.btn_load = tk.Button(self.frame_buttons, text="Load preset", width=6, command=lambda: self.load_preset())
        self.btn_generate = tk.Button(self.frame_buttons, text="Generate", width=6, command=lambda: self.generate())
        self.btn_execute = tk.Button(self.frame_buttons, text="Execute", width=6, command=lambda: self.execute())
        self.btn_load.grid(column=0, row=0, sticky="EW")
        self.btn_generate.grid(column=1, row=0, sticky="EW")
        self.btn_execute.grid(column=2, row=0, sticky="EW")

        self.frame_buttons.grid(columnspan=4, column=0, row=9)

    def load_preset(self):
        pass

    def generate(self):

        my_dict = self.compile_dict()


    def execute(self):
        pass

    def compile_dict(self):

        options_dict = {

            "resolution": "1920x1080",
            "blanking": self.entry_blanking.get(),
            "bitrate": self.entry_bitrate.get(),

            "text_size": self.entry_text_size.get(),
            "padding": self.entry_padding.get(),

            "font": self.var_font,
            "top_left": self.entry_top_left.get(),
            "top_center": self.entry_top_center.get(),
            "top_right": self.entry_top_right.get(),
            "bottom_left": self.entry_bottom_left.get(),
            "bottom_center": self.entry_bottom_center.get(),
            "bottom_right": self.entry_bottom_right.get(),

            "mos_tc_replacement": self.entry_mos_replacement.get(),

            "threads": self.entry_processes.get(),
            "encoding_speed": self.var_encoding_speed,

            "watermark": self.entry_watermark.get(),
            "watermark_y_position": self.entry_watermark_y_pos.get(),
            "watermark_size": self.entry_watermark_size.get(),
            "watermark_opacity": self.entry_watermark_opacity.get(),
        }
        return


if __name__ == "__main__":
    app = App()
    app.mainloop()
