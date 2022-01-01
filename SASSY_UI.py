import sassy
import csv_loader
import tkinter as tk


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.attributes("-alpha", 0.9)
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
        label_input_file = tk.Label(self, text="Input ALE")
        entry_input_file = tk.Entry(self, width=25)
        entry_input_file.insert(0, "")
        label_input_file.grid(column=0, row=1, sticky="E")
        entry_input_file.grid(columnspan=3, column=1, row=1, sticky="W")

        # font
        label_font = tk.Label(self, text="Font")
        entry_font = tk.Entry(self, width=25)
        entry_font.insert(0, "Franklin Gothic Medium.ttc")
        label_font.grid(column=0, row=2, sticky="E")
        entry_font.grid(columnspan=3, column=1, row=2, sticky="W")

        # blanking and text size
        label_blanking = tk.Label(self, text="Blanking")
        entry_blanking = tk.Entry(self, width=6)
        entry_blanking.insert(0, "2.39")
        label_blanking.grid(column=0, row=3, sticky="E")
        entry_blanking.grid(column=1, row=3, sticky="W")

        label_text_size = tk.Label(self, text="Text Size")
        entry_text_size = tk.Entry(self, width=6)
        entry_text_size.insert(0, "20")
        label_text_size.grid(column=2, row=3, sticky="E")
        entry_text_size.grid(column=3, row=3, sticky="W")

        # bitrate and padding
        label_bitrate = tk.Label(self, text="Bitrate")
        entry_bitrate = tk.Entry(self, width=6)
        entry_bitrate.insert(0, "10000")
        label_bitrate.grid(column=0, row=4, sticky="E")
        entry_bitrate.grid(column=1, row=4, sticky="W")

        label_padding = tk.Label(self, text="Padding")
        entry_padding = tk.Entry(self, width=6)
        entry_padding.insert(0, "5")
        label_padding.grid(column=2, row=4, sticky="E")
        entry_padding.grid(column=3, row=4, sticky="W")

        # the burnin frame
        frame_burnins = tk.LabelFrame(self, text="Burnin layout")

        # burnin_frame.columnconfigure(tuple(range(3)), weight=1, minsize=5, pad=10)
        # burnin_frame.rowconfigure(tuple(range(8)), weight=1, pad=5)

        entry_top_left = tk.Entry(frame_burnins, width=14)
        entry_top_left.grid(column=0, row=0, sticky="EW")
        entry_top_center = tk.Entry(frame_burnins, width=14)
        entry_top_center.grid(column=1, row=0, sticky="EW")
        entry_top_right = tk.Entry(frame_burnins, width=14)
        entry_top_right.grid(column=2, row=0, sticky="EW")

        label_watermark = tk.Label(frame_burnins, text="Watermark")
        entry_watermark = tk.Entry(frame_burnins, width=20)

        label_watermark.grid(column=1, row=1, sticky="EW", pady=(10, 0))
        entry_watermark.grid(columnspan=3, column=0, row=2, sticky="EW", pady=(0, 10))

        entry_bottom_left = tk.Entry(frame_burnins, width=14)
        entry_bottom_left.grid(column=0, row=4, sticky="EW")
        entry_bottom_center = tk.Entry(frame_burnins, width=14)
        entry_bottom_center.grid(column=1, row=4, sticky="EW")
        entry_bottom_right = tk.Entry(frame_burnins, width=14)
        entry_bottom_right.grid(column=2, row=4, sticky="EW")

        frame_burnins.grid(columnspan=4, column=0, row=5)

        # watermark options
        label_watermark_y_pos = tk.Label(self, text="Watermark position")
        entry_watermark_y_pos = tk.Entry(self, width=6)
        entry_watermark_y_pos.insert(0, "0.7")
        label_watermark_y_pos.grid(column=0, row=6, sticky="E")
        entry_watermark_y_pos.grid(column=1, row=6, sticky="W")

        label_opacity = tk.Label(self, text="Watermark opacity")
        entry_opacity = tk.Entry(self, width=6)
        entry_opacity.insert(0, "0.2")
        label_opacity.grid(column=0, row=7, sticky="E")
        entry_opacity.grid(column=1, row=7, sticky="W")

        label_size = tk.Label(self, text="Watermark size")
        entry_size = tk.Entry(self, width=6)
        entry_size.insert(0, "128")
        label_size.grid(column=0, row=8, sticky="E")
        entry_size.grid(column=1, row=8, sticky="W")

        # encoder settings
        label_size = tk.Label(self, text="Simultaneous processes")
        entry_size = tk.Entry(self, width=6)
        entry_size.insert(0, "8")
        label_size.grid(column=2, row=6, sticky="E")
        entry_size.grid(column=3, row=6, sticky="W")

        label_encoding_speed = tk.Label(self, text="Encoding speed")
        items_encoding_speed = ["ultrafast",
                                "superfast",
                                "veryfast",
                                "faster",
                                "fast",
                                "medium",
                                "slow",
                                "slower",
                                "veryslow"]

        var_encoding_speed = tk.StringVar()
        var_encoding_speed.set("veryfast")
        option_encoding_speed = tk.OptionMenu(self, var_encoding_speed, *items_encoding_speed)
        option_encoding_speed.config(width=4)

        label_encoding_speed.grid(column=2, row=7, sticky="E")
        option_encoding_speed.grid(column=3, row=7, sticky="W")

        # the buttons at the bottom
        
        frame_buttons = tk.Frame(self)
        
        self.btn_load = tk.Button(frame_buttons, text="Load", width=6, command=lambda: self.load())
        self.btn_generate = tk.Button(frame_buttons, text="Generate", width=6, command=lambda: self.generate())
        self.btn_execute = tk.Button(frame_buttons, text="Execute", width=6, command=lambda: self.execute())
        self.btn_load.grid(column=0, row=0, sticky="EW")
        self.btn_generate.grid(column=1, row=0, sticky="EW")
        self.btn_execute.grid(column=2, row=0, sticky="EW")

        frame_buttons.grid(columnspan=4, column=0, row=9)


if __name__ == "__main__":
    app = App()
    app.mainloop()
