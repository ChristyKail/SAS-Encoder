from typing import List
from collections import Counter
import pandas
import csv
import os


class Ale:

    def __init__(self):

        self.heading = list()
        self.df = pandas.DataFrame()
        self.name = "Empty ALE"
        self.source = list()

    def load_from_file(self, file_in):

        # This function will set the ALE to the ALE file specified

        file_as_lines = list()
        heading_as_lines = list()
        data_frame = pandas.DataFrame()

        # CONFORM FILENAME
        file_in = file_in.replace("\ ", " ")
        file_in = file_in.strip()

        # OPEN THE FILE AND SAVE THE HEADER

        if not os.path.isfile(file_in):

            print(str(file_in)+" is not a file!")

        with open(file_in, "r") as file_in_handler:

            # Copy the file into a list

            try:

                for line in file_in_handler:

                    file_as_lines.append(line.strip())

            except:

                print("ale_p.load_from_file: file doesn't contain text data")

                return False

            # Save the header for later, and select which rows to skip loading into DF
            ii = 0
            for line in file_as_lines:

                if line.strip() == "Column":
                    skip_rows = list(range(0, ii + 1))
                    skip_rows.append(ii + 2)
                    skip_rows.append(ii + 3)

                    break

                if line.strip() == "Heading":

                    pass

                else:

                    heading_as_lines.append(line.strip())

                ii = ii + 1

        # LOAD THE ALE INTO A DATA FRAME

        try:

            data_frame = pandas.read_csv(file_in, sep="\t", skiprows=skip_rows, dtype=str, engine="python", keep_default_na=False)

        except:

            return "False"

        data_frame.drop(data_frame.filter(regex="Unname"), axis=1, inplace=True)

        self.heading = heading_as_lines

        self.df = data_frame

        return "True"

    def save_ale(self, file_out: str):

        output_builder: List[str] = list()

        # Save the DF to a the file

        self.df.to_csv(file_out, sep='\t', index=False, header=True, quoting=csv.QUOTE_NONE, columns=list(self.df))

        # Reopen the file to add the heading data
        with open(file_out, 'r+') as file_in_handler:
            # Iterate through the file, adding each line of data to a list
            ii = 0
            for line in file_in_handler:
                output_builder.append(line.strip("\n"))

                ii = ii + 1

            # Combine the heading, text, and data to make a completed list of lines for saving
            output_builder = ["Heading"] + self.heading + ["Column"] + [output_builder[0]] + ["\nData"] + output_builder[1:ii] + ["\n"]

            # Save the complete list of lines to the file
            file_in_handler.seek(0, 0)
            file_in_handler.write("\n".join(output_builder))

    def save_to_csv(self, file_out: str):

        self.df.to_csv(file_out, sep='\t', index=False, header=True, quoting=csv.QUOTE_NONE)

    def add_cols(self, other, match):

        #  if we're adding to an empty dataframe, just add it and skip the complicated stuff
        if self.df.empty:

            self.df = other.df
            self.source = other.source
            return True

        match = match

        # Check if the match criteria is given as a single string or a tuple, and act accordingly

        self.df["Match"] = self.df["Tape"]+self.df["Start"]
        other.df["Match"] = other.df["Tape"]+other.df["Start"]

        # Make copies of the columns we want to match by, so we can check the DFs can be matched
        match_col_l = self.df["Match"].copy()
        match_col_r = other.df["Match"].copy()

        match_col_l.sort_values(0, ascending=False, inplace=True)
        match_col_l.reset_index(drop=True, inplace=True)

        match_col_r.sort_values(0, ascending=False, inplace=True)
        match_col_r.reset_index(drop=True, inplace=True)

        # If the sorted match columns don't match, cancel

        if not match_col_l.equals(match_col_r):

            print(str(self) + ": added ALE doesn't have the same reels loaded")

            return False

        self.df = pandas.merge(self.df, other.df, how="outer", on="Match", suffixes=["", "_2"])

        self.heading = other.heading
        self.source = self.source + other.source

        return True

    # Add rows to the current DF

    def add_rows(self, other):

        # if we're adding to an empty dataframe, just add it and skip the complicated stuff

        if self.df.empty:

            self.df = other.df
            self.source = other.source
            return True

        # Is there a difference in the columns between the DFs? If so, do something about it

        counter1 = Counter(self.df.columns)
        counter2 = Counter(other.df.columns)

        missing1 = list(counter1 - counter2)
        missing2 = list(counter2 - counter1)

        for line in missing1:

            print("Missing in new ALE "+ str(line))
            other.df[line] = ""

        for line in missing2:

            print("Missing in existing ALE " + str(line))
            self.df[line] = ""

        # Concatenate the new new ALE to the existing one

        self.df = pandas.concat([self.df, other.df], axis=0, ignore_index=True)
        self.heading = other.heading
        self.source = self.source+other.source

        return True

    def edit_heading(self, tag: str, value: str):

        ii = 0

        for line in self.heading:

            line = line.split("\t")

            if line[0] == tag:

                line[1] = value

                self.heading[ii] = line[0]+"\t"+line[1]

                return True

            ii = ii+1

        self.heading.append(tag+"\t"+value)
