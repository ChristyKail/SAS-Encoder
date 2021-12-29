import concurrent.futures
import ale_p
import subprocess
import os
import sys
import argparse
import re

font = "/System/Library/Fonts/Apple Symbols.ttf".replace(" ", "\ ")

parser = argparse.ArgumentParser()

parser.add_argument("-tl", "--topleft", type=str)
parser.add_argument("-tm", "--topmid", type=str)
parser.add_argument("-tr", "--topright", type=str)
parser.add_argument("-bl", "--bottomleft", type=str)
parser.add_argument("-bm", "--bottommid", type=str)
parser.add_argument("-br", "--bottomright", type=str)

parser.add_argument("-s", "--speed", type=str, choices=["ultrafast", "superfast", "veryfast", "faster", "fast",
                                                        "medium", "slow", "slower", "veryslow"], default="veryfast")

parser.add_argument("-t", "--threads", type=int, default=4)
parser.add_argument("-b", "--blanking", type=float, default=None)
parser.add_argument("-x", "--textsize", type=int, default=18)

args = parser.parse_args()


def get_input():
    input_text = input("Drop ALE here...")

    input_text = input_text.replace("\\", "").strip()

    return input_text


def load_ale_as_df(path_to_ale: str):
    ale_object = ale_p.Ale()
    ale_object.load_from_file(path_to_ale)

    return ale_object.df


def compile_process(data: dict):

    burnins = []

    aspect_ratio = data["blanking"]

    if aspect_ratio:

        blanking_height = (1080-(1920/aspect_ratio))/2

        blanking_top_string = "drawbox=x=0:y=0:h=" + str(blanking_height) + ":thickness=fill:color=black"
        blanking_bottom_string = "drawbox=x=0:y=" + str(1080 - blanking_height) + ":h=" + str(
            blanking_height) + ":thickness=fill:color=black"

        burnins.append(blanking_top_string)
        burnins.append(blanking_bottom_string)

    # Create a burnin string for each position
    for this_index, this_position in enumerate(burnin_pos):

        this_position_data = data.get(this_position)

        if re.match(r"([0-9]{2}:){3}[0-9]{2}", this_position_data):

            this_position_data = '\''+this_position_data.replace(":", "\\:")+'\''

            this_burnin = "drawtext=fontfile=" + font + ":" + "Timecode\\ " \
                          + ":timecode=" + this_position_data + ":rate=24:fontsize=" + str(args.textsize) + ":" \
                          + burnin_locs[this_index] + ":fontcolor=DarkGray"

        else:
            this_burnin = "drawtext=fontfile=" + font + ":" + this_position_data + ":fontsize=" \
                          + str(args.textsize) + ":" + burnin_locs[this_index] + ":fontcolor=DarkGray"

        if not this_position_data:
            continue

        burnins.append(this_burnin)

    export_process = ["ffmpeg",
                      "-y",
                      "-i", data["file_in"],
                      "-loglevel", "warning",
                      "-filter_complex", ",".join(burnins),
                      "-codec:v", "libx264",
                      "-preset", args.speed,
                      "-b:v", "10000k",
                      "-minrate", "8000k",
                      "-maxrate", "10000k",
                      "-bufsize", "4800k",
                      "-threads", "0",
                      "-movflags", "+faststart",
                      "-s", "1920x1080",
                      "-pix_fmt", "yuv420p",
                      "-codec:a", "aac",
                      data["file_out"]]

    return export_process


def process_video(process_data: list):
    process_result = subprocess.run(process_data, capture_output=False)

    return process_result


def print_progress_bar(iteration, total, prefix='', suffix='', length=25, fill='#'):
    percent = iteration / total * 100
    bar_count = (int(length * (iteration / total)))
    empty_count = length - bar_count
    bar = (fill * bar_count) + "-" * empty_count

    print(f'\r{prefix}|{bar}| {round(percent)}% complete {suffix}', end="", flush=True)


if __name__ == "__main__":

    # my_input_ale = get_input()
    my_input_ale = "/Users/christykail/Desktop/SAS/_WORKING.ALE"
    my_input_dir = os.path.dirname(my_input_ale)
    my_output_dir = os.path.join(os.path.dirname(my_input_dir), "H264")

    if not os.path.isdir(my_output_dir):

        try:
            os.mkdir(my_output_dir)
        except:
            print("Output folder could not be initialised")
            sys.exit("Output folder could not be initialised")

    print(my_input_dir)
    print(my_output_dir)

    try:
        df = load_ale_as_df(my_input_ale)
    except:
        print("ALE loading failed for some reason *shrug*")
        sys.exit("ALE loading failed")

    pad = str(5)
    burnin_locs = ["x=" + pad + ":y=" + pad, "x=(w/2)-(tw/2):y=" + pad, "x=w-tw-" + pad + ":y=" + pad,
                   "x=" + pad + ":y=h-th-" + pad, "x=(w/2)-(tw/2):y=h-th-" + pad, "x=w-tw-" + pad + ":y=h-th-" + pad]
    burnin_pos = ["topleft", "topmid", "topright", "bottomleft", "bottommid", "bottomright"]
    burnin_cols = [args.topleft, args.topmid, args.topright, args.bottomleft, args.bottommid, args.bottomright]

    # modify the dataframe so burn-in data is labelled correctly
    for index, position in enumerate(burnin_pos):
        try:
            df[position] = df[burnin_cols[index]]

        except KeyError:
            print("No value set for", position)
            df[position] = ""

    processes_list = []
    files_in_dir = []
    files_to_process = []

    # get a list of MOV files in the source directory
    for file in os.listdir(my_input_dir):

        if file.endswith(".mov"):
            files_in_dir.append(file)

    # compare clips in directory against dataframe

    df["file_in"], df["file_out"]  = "", ""

    for index, value in enumerate(df["Name"]):

        if value + ".mov" in files_in_dir:

            print(f"Found {value}")
            df["file_in"][index] = os.path.join(my_input_dir, value + ".mov")
            df["file_out"][index] = os.path.join(my_output_dir, value + ".mov")

        else:

            print(f"No data found for {file.strip('.mov')}")
            df.drop(index)

    df["blanking"] = args.blanking

    for index, values in df.iterrows():

        this_process = compile_process(values)
        processes_list.append(this_process)

    complete_files = 0
    total_files = len(processes_list)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.threads) as executor:

        futures = {executor.submit(process_video, process): process for process in processes_list}

        print_progress_bar(complete_files, total_files, suffix="")

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            complete_files = complete_files + 1

            print_progress_bar(complete_files, total_files)

    print("\07")
