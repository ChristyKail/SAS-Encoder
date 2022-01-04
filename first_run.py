import os


def first_run():
    if not os.path.isfile("run.command"):
        print("Performing first run")

        file_name = "run.command"
        import __main__
        this_file = os.path.realpath(__main__.__file__)

        with open(file_name, "w") as file_handler:
            file_handler.write("#!/bin/bash")
            file_handler.write("\n")
            file_handler.write(f"cd \'{os.path.dirname(this_file)}\'")
            file_handler.write("\n")
            file_handler.write("clear")
            file_handler.write("\n")
            file_handler.write(f"python3 \'{os.path.basename(this_file)}\'")

        os.chmod(file_name, os.stat(file_name).st_mode ^ 111)
