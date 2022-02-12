import argparse
import concurrent.futures
import csv
import datetime
import os
import re
import subprocess
import sys

import ale


class Processor:

    def __init__(self, my_input_ale: str, options: dict, manager=None):

        self.options = options
        self.manager = manager

        self.my_input_ale = my_input_ale
        self.my_input_dir = os.path.dirname(my_input_ale)
        self.my_output_dir = os.path.join(os.path.dirname(self.my_input_dir), "H264")

        logs = [f"New job started at {datetime.datetime.now()}"]

        # initialise output dir
        if not os.path.isdir(self.my_output_dir):
            try:
                os.mkdir(self.my_output_dir)
            except:
                raise NotADirectoryError("Could not initialise output directory")

        # load the ale
        try:
            df = load_ale_as_df(my_input_ale)
        except:
            print("ALE loading failed for some reason *shrug*")

            sys.exit(1)

        # verify the options and ale
        verified, errors = verify_options(self.options, df)
        if not verified:
            for error in errors:
                print(error)
            sys.exit(1)

        # do font stuff
        font = get_font_path_mac(self.options["font"])
        if font is None:
            raise FileNotFoundError("Font file not found")
        self.options["font"] = font

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
                logs.append(f"No data found for {value.strip('.mov')}")
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

            futures = {executor.submit(process_video, process): process for process in processes_list}

            print_progress_bar(complete_files, total_files, suffix="")
            if manager:
                manager.update_progress(complete_files / total_files * 100)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.returncode != 0:
                    print("There may have been some issues....", "\n", result.stderr)
                complete_files = complete_files + 1

                print_progress_bar(complete_files, total_files)

                if manager:
                    manager.update_progress(complete_files / total_files * 100)

                logs.append(result)

        with open("sasen_logs.txt", 'a') as log_file:

            for log_line in logs:
                log_file.write(f'\n{log_line}')
            log_file.write("\nProcess complete")

        if __name__ == "__main__":
            print("\x07")

    def compile_process(self, ale_data: dict):

        ffmpeg_filters = []

        # create output blanking
        if self.options["blanking"]:

            if self.options["blanking"] == "NONE" or self.options["blanking"] == "0":

                pass

            else:

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

            # parse though each dynamic
            for matched_text in re.findall(r'{.*?}', this_data):

                ale_col_name = matched_text.strip('{').strip('}')

                this_data = this_data.replace(matched_text, ale_data[ale_col_name])

                # override sound timcodes when clip is MOS
                if ale_col_name in ["Sound TC", "Auxiliary TC1"]:

                    if not re.search(r"([0-9]{2}:){3}[0-9]{2}", this_data):
                        this_data = self.options["mos_tc_replacement"]

            # special case for timecode elements
            timecode_match = re.search(r"([0-9]{2}:){3}[0-9]{2}", this_data)
            if timecode_match:
                tc_start = escaped(timecode_match.group())
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

            ffmpeg_filters.append(filter_string)

        # watermark
        if self.options["watermark"]:
            watermark_text = self.options["watermark"]

            for matched_text in re.findall(r'{.*?}', watermark_text):
                ale_col_name = matched_text.strip('{').strip('}')

                watermark_text = watermark_text.replace(matched_text, ale_data[ale_col_name])

            watermark_text = escaped(watermark_text)

            watermark_string = "".join(["drawtext=fontfile=",
                                        self.options["font"],
                                        ":", watermark_text,
                                        ":fontsize=", self.options["watermark_size"],
                                        ":x=(w/2)-(tw/2):y=h*", self.options["watermark_y_position"],
                                        ":fontcolor=White@", self.options["watermark_opacity"]
                                        ])

            ffmpeg_filters.append(watermark_string)

        bitrate = self.options["bitrate"]

        if self.options["limit_audio_tracks"] == "True":
            mapping = ["-map", "0:v",
                       "-map", "0:a:0?"]

        else:
            mapping = []

        export_process = ["ffmpeg",
                          "-y",
                          "-i", ale_data["file_in"],
                          "-loglevel", "warning",
                          ] + mapping + [
                             "-filter_complex", ",".join(ffmpeg_filters),
                             "-codec:v", "libx264",
                             "-preset", self.options["encoding_speed"],
                             "-b:v", f'{bitrate}k',
                             "-minrate", f'{int(bitrate) * 0.8}k',
                             "-maxrate", f'{bitrate}k',
                             "-bufsize", f'{int(bitrate) * 1.5}k',
                             "-threads", "4",
                             "-movflags", "+faststart",
                             "-s", self.options["resolution"],
                             "-pix_fmt", "yuv420p",
                             "-codec:a", "aac",
                             ale_data["file_out"]]

        return export_process


def verify_options(options: dict, ale_data=None):
    print("Verifying options")
    errors = []

    required_options = [
        "resolution",
        "blanking",
        "bitrate",
        "text_size",
        "padding",
        "font",
        "mos_tc_replacement",
        "threads",
        "encoding_speed",
    ]

    dependencies = {

        "watermark": ["watermark_y_position", "watermark_size", "watermark_opacity"]

    }

    option_patterns = {

        "resolution": r'\d{3,4}x\d{3,4}',
        "blanking": r'[\d\.]+|NONE|^$',
        "bitrate": r'\d+',
        "text_size": r'\d+',
        "padding": r'\d+',
        "font": r'[\w .]+',
        "top_left": r'.+',
        "top_center": r'.+',
        "top_right": r'.+',
        "bottom_left": r'.+',
        "bottom_center": r'.+',
        "bottom_right": r'.+',
        "mos_tc_replacement": r'[\w .-]+',
        "threads": r'\d+',
        "encoding_speed": r'ultrafast|superfast|veryfast|faster|fast|medium|slow|slower|veryslow',
        "watermark": r'.+',
        "watermark_y_position": r'[\d\.]+',
        "watermark_size": r'\d+',
        "watermark_opacity": r'[\d\.]+',

    }

    for option in required_options:
        if not options[option]:
            errors.append(f'{option} is not defined in the preset file')
        else:
            if not re.match(option_patterns[option], options[option]):
                errors.append(f'{options[option]} is not a valid value for {option}')

    for parent, children in dependencies.items():

        if options[parent]:

            for child in children:

                if not options[child]:
                    errors.append(f'{child} is not defined in the preset file - required by {parent}')

    #  check all requested data is present in the ale

    if ale_data is not None:

        if ale_data.empty:
            errors.append("Invalid ALE")

        else:
            for string in options.values():
                for element in re.findall(r'(?<={).*?(?=})', string):
                    if element not in ale_data.columns:
                        errors.append(f'No data for \'{element}\' in ALE')
    else:
        print("No ALE provided, could not check")

    if len(errors) > 0:
        return False, errors

    else:
        return True, errors


def process_video(process_data: list):
    process_result = subprocess.run(process_data, capture_output=True)
    process_result.check_returncode()
    return process_result


def get_input():
    input_text = input("Drop ALE here...")
    input_text = input_text.replace("\\", "").strip()
    return input_text


def load_ale_as_df(path_to_ale: str):
    ale_object = ale.Ale(path_to_ale)

    return ale_object.dataframe


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
    characters = [":", " ", ","]

    for c in characters:
        string = string.replace(c, f'\\{c}')

    return "\'" + string + "\'"


def load_csv(file_name):

    if not os.path.isfile(file_name):

        return None

    with open(file_name) as file_handler:

        file_reader = csv.reader(file_handler)
        dictionary = {rows[0]: rows[1] for rows in file_reader if rows[0]}

    return dictionary


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--preset", type=str, default="default.sasen")
    parser.add_argument("-i", "--input", type=str, default="")

    args = parser.parse_args()

    if args.input == "":
        input_filename = get_input()
    else:
        input_filename = args.input

    processor = Processor(input_filename, load_csv("presets/default.sasen"))
