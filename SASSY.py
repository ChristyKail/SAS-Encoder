import concurrent.futures
import multiprocessing
import pandas
import ale_p
import subprocess
import os
import sys
import argparse

font = ""

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

    # Create a burnin string for each position
    for this_position in burnin_pos:
        this_burnin = "drawtext=fontfile=" + font + ":" + data.get(this_position) + ":fontsize=24:" + "x=(w/2)-(tw/2):y=h-th-5" + ":fontcolor=DarkGray"
        burnins.append(this_burnin)

    export_process = ["ffmpeg",
                      "-y",
                      "-i", data["file_in"],
                      "-loglevel", "warning",
                      # "-filter_complex", ",".join(burnins),
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

    process_result = subprocess.run(process_data, capture_output=True)

    return process_result


def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):

    percent = iteration / total * 100
    bar_count = (int(length*(iteration/total)))
    empty_count = length-bar_count
    bar = (fill*bar_count)+" "*empty_count

    print(f'\r{prefix}|{bar}| {round(percent)}% complete {suffix}', end="", flush=True)


if __name__ == "__main__":

    # my_input_ale = get_input()
    my_input_ale = "/Volumes/GoogleDrive/Shared drives/OST - Software Dev/01_Current/2PIX/SAS/20210819_MU_PREP_Sync.ALE"
    my_input_dir = os.path.dirname(my_input_ale)
    my_output_dir = os.path.join(os.path.dirname(my_input_dir), "H264")
    print(my_input_dir)

    try:
        df = load_ale_as_df(my_input_ale)
    except Exception:
        print("ALE loading failed for some reason *shrug*")
        sys.exit("ALE loading failed")

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

    df["file_in"], df["file_out"] = "", ""

    for index, value in enumerate(df["Name"]):

        if value+".mov" in files_in_dir:

            print(f"Found {value}")
            df["file_in"][index] = os.path.join(my_input_dir, value+".mov")
            df["file_out"][index] = os.path.join(my_output_dir, value + ".mov")

        else:

            print(f"No data found for {file.strip('.mov')}")
            df.drop(index)

    print(df[["file_in", "file_out", "Name"]])
    
    df[["file_in", "file_out", "Name"]].to_csv("Dataframe.csv")

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
            
            print_progress_bar(complete_files, total_files, suffix=result)

