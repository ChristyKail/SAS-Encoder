import concurrent.futures

import value as value

import ale_p
import subprocess
import os
import sys
import argparse
import re
import csv_loader

parser = argparse.ArgumentParser()

args = parser.parse_args()


class Processor:

    def __init__(self, my_input_ale: str, options: dict):

        self.options = options

        if not self.verify_options():
            sys.exit(1)

        self.my_input_ale = my_input_ale
        self.my_input_dir = os.path.dirname(my_input_ale)
        self.my_output_dir = os.path.join(os.path.dirname(self.my_input_dir), "H264")

        # initialise output dir
        if not os.path.isdir(self.my_output_dir):
            try:
                os.mkdir(self.my_output_dir)
            except:
                raise NotADirectoryError("Could not initialise output directory")

        # do font stuff
        font = get_font_path_mac(self.options["font"])
        if font is None:
            raise FileNotFoundError("Font file not found")
        self.options["font"] = font

        try:
            df = load_ale_as_df(my_input_ale)
        except:
            print("ALE loading failed for some reason *shrug*")

        processes_list = []
        files_in_dir = []

        # get a list of MOV files in the source directory
        for file in os.listdir(self.my_input_dir):

            if file.endswith(".mov"):
                files_in_dir.append(file)

        df["file_in"], df["file_out"] = "", ""

        for index, value in enumerate(df["Name"]):
            if value + ".mov" in files_in_dir:

                print(f"Found {value}")
                df["file_in"][index] = os.path.join(self.my_input_dir, value + ".mov")
                df["file_out"][index] = os.path.join(self.my_output_dir, value + ".mov")
            else:
                print(f"No data found for {value.strip('.mov')}")
                df.drop(index)

        burnin_names = ["top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right"]
        pad = self.options["padding"]
        burnin_positions = [
            "x=" + pad + ":y=" + pad,
            "x=(w/2)-(tw/2):y=" + pad,
            "x=w-tw-" + pad + ":y=" + pad,
            "x=" + pad + ":y=h-th-" + pad,
            "x=(w/2)-(tw/2):y=h-th-" + pad,
            "x=w-tw-" + pad + ":y=h-th-" + pad
        ]

        self.burnin_positions_map = dict(zip(burnin_names, burnin_positions))
        self.burnin_data_map = {key: value for key, value in self.options.items() if key in burnin_names}

        for index, values in df.iterrows():
            this_process = self.compile_process(values)
            processes_list.append(this_process)

        complete_files = 0
        total_files = len(processes_list)

        with concurrent.futures.ProcessPoolExecutor(max_workers=int(self.options["threads"])) as executor:

            futures = {executor.submit(self.process_video, process): process for process in processes_list}

            print_progress_bar(complete_files, total_files, suffix="")

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                complete_files = complete_files + 1

                print_progress_bar(complete_files, total_files)

    def verify_options(self):

        for pair in self.options.items():
            print(pair)

        return True

    def compile_process(self, ale_data: dict):

        ffmpeg_filters = []

        # create output blanking
        if self.options["blanking"]:
            aspect_ratio = float(self.options["blanking"])
            blanking_height = (1080 - (1920 / aspect_ratio)) / 2
            blanking_top_string = "drawbox=x=0:y=0:h=" + str(blanking_height) + ":thickness=fill:color=black"
            blanking_bottom_string = "drawbox=x=0:y=" + str(1080 - blanking_height) + ":h=" + str(
                blanking_height) + ":thickness=fill:color=black"
            ffmpeg_filters.append(blanking_top_string)
            ffmpeg_filters.append(blanking_bottom_string)

        # create a filter for each burnin position
        for this_position, this_data in self.burnin_data_map.items():

            if not this_data:
                continue

            print(f"\n{this_position}", this_data)

            # parse though each dynamic
            for matched_text in re.findall(r'{[\w \-]*}', this_data):
                this_data = this_data.replace(matched_text, ale_data[matched_text.strip('{').strip('}')])

            print(this_position, this_data)

            # special case for timecode elements
            timecode_match = re.search(r"([0-9]{2}:){3}[0-9]{2}", this_data)
            if timecode_match:
                tc_start = escaped(timecode_match.group().replace(":", "\\:"))
                tc_prefix = this_data.replace(timecode_match.group(), "")

                filter_string = "".join(["drawtext=fontfile=",
                                         self.options["font"],
                                         ":", escaped(tc_prefix),
                                         ":timecode=", tc_start,
                                         ":rate=24",
                                         ":fontsize=", self.options["text_size"],
                                         ":", self.burnin_positions_map[this_position],
                                         ":fontcolor=DarkGray"
                                         ])
            # if it's not a timecode element, or if the timecode is blank
            else:
                filter_string = "".join(["drawtext=fontfile=",
                                         self.options["font"],
                                         ":", escaped(this_data),
                                         ":fontsize=", self.options["text_size"],
                                         ":", self.burnin_positions_map[this_position],
                                         ":fontcolor=DarkGray"
                                         ])

            ffmpeg_filters.append(filter_string.replace(" ", "\ "))

        # watermark
        if self.options["watermark"]:
            watermark_text = self.options["watermark"]

            watermark_string = "".join(["drawtext=fontfile=",
                                        self.options["font"],
                                        ":", watermark_text,
                                        ":fontsize=", self.options["watermark_size"],
                                        ":x=(w/2)-(tw/2):y=h*", self.options["watermark_y_position"],
                                        ":fontcolor=White@", self.options["watermark_opacity"]
                                        ])

            ffmpeg_filters.append(watermark_string.replace(" ", "\ "))

        export_process = ["ffmpeg",
                          "-y",
                          "-i", ale_data["file_in"],
                          "-loglevel", "warning",
                          "-filter_complex", ",".join(ffmpeg_filters),
                          "-codec:v", "libx264",
                          "-preset", self.options["encoding_speed"],
                          "-b:v", "10000k",
                          "-minrate", "8000k",
                          "-maxrate", "10000k",
                          "-bufsize", "4800k",
                          "-threads", "0",
                          "-movflags", "+faststart",
                          "-s", "1920x1080",
                          "-pix_fmt", "yuv420p",
                          "-codec:a", "aac",
                          ale_data["file_out"]]

        return export_process

    def process_video(self, process_data: list):

        print(" ".join(process_data))
        process_result = subprocess.run(process_data, capture_output=False)

        return process_result


def get_input():
    input_text = input("Drop ALE here...")

    input_text = input_text.replace("\\", "").strip()

    return input_text


def load_ale_as_df(path_to_ale: str):
    ale_object = ale_p.Ale()
    ale_object.load_from_file(path_to_ale)

    return ale_object.df


def print_progress_bar(iteration, total, prefix='', suffix='', length=25, fill='#'):
    percent = iteration / total * 100
    bar_count = (int(length * (iteration / total)))
    empty_count = length - bar_count
    bar = (fill * bar_count) + "-" * empty_count

    print(f'\r{prefix}|{bar}| {round(percent)}% complete {suffix}', end="", flush=True)


def get_font_path_mac(name: str):
    font_user = os.path.join(os.path.expanduser('~'), "Library/Fonts", name)
    font_global = os.path.join("/System/Library/Fonts", name)
    font_supplemental = os.path.join("/System/Library/Fonts/Supplemental", name)

    if os.path.isfile(font_global):
        return font_global

    elif os.path.isfile(font_supplemental):
        return font_supplemental

    elif os.path.isfile(font_user):
        return font_user

    else:
        return None


def escaped(string: str):
    return "\'" + string + "\'"


if __name__ == "__main__":
    processor = Processor("/Users/christykail/Desktop/SAS/_WORKING.ALE", csv_loader.load_csv("default.sassy"))
