# SAS Encoder

Tool for batch encoding DNxHD files based on an Avid Log Exchange (ALE) file

To report bugs or for feature requests, email christy.kail@cinelab.co.uk

Recommended python version 3.9.9 (check by running `python3 --version`)

#### Installation instructions

- From the Github page, click the green `Code` button, then `Download zip`
- Extract files to a folder where you want to install the tool. This should not be moved after installation.
- Right click the `first_time_run.command` file and click `open` to begin setup. You may be prompted to allow "A program
  downloaded from the internet"
- The script will run through initial setup, downloading `pandas` `tkinter` and `ffmpeg` from Pip and Brew.
- When the installation is complete, the main window will open and a `run.command` file will be created in the folder.
- You can rename and move this file to wherever you want. Double-clicking it will run the script from anywhere.
- If the main window *doesn't* open and the terminal shows `[process completed]`, try re-running the setup.
- If you ever need to move the actual install, delete the `run.command` from the install folder and
  rerun `first_time_run.command`. This will create a new `run.command` linked to the new location.

#### Using the tool

- Open the tool by running your shortcut file.
- A user interface and a terminal window will open.
- Set the required options in the window
- Click `convert files` and choose an ALE file to begin processing. All you clips must be in the same directory as the ALE.
- Any issues found will be brought to your attention in a dialog window. Fix any issues and try again.
- The window will go transparent, indicating the processing is taking place.
- You can view a list of files that were found and a progress bar in the terminal window.
- Note the progress bar only updates when a file has completed. If you are only processing one file it will show 0% and then jump to 100% upon completion.
- When the job is complete, the UI window will return to the front.

#### Some of the options
- __Burnin layout__ - typing text in each input box will burn it into the relevant corner
  - Using curly brackets will load that data column from ALE, e.g. `Shot` will burn in "Shot", but `{Shot}` will burn in "25B-1A" or whatever the `shot` field is for that clip. These are called 'dynamic elements'
  - Multiple static and dynamic can be combined, e.g. `Shot {Scene} {Take}` will burn in "Shot 25B 1A"
  - If timecode like data is found in a dynamic element (e.g `00:00:00:00`), this will be assumed to be a starting timecode value, and the burnin will run on from that point.
  - A timecode element will always move to the end of a burnin, no matter where it is placed in the string, e.g. `{Start} TC` will output "TC19:26:23:04".  They will also ignore any spaces around them.
  - Only one timecode element can be added per burnin position.
- __Watermark__ - the watermark can be entered in a similar way to other burn ins
  - Only one dynamic element is supported in the watermark
  - Watermark position - the vertical position of the watermark on the picture, use `0` for the top, `1` for the bottom, or any value inbetween.
  - Watermark opacity - the opacity of the watermark, use `0` for completely transparent, `1` for fully opaque, or any value inbetween.
  - Watermark size - the height of the watermark in pixels, around `100` is a good starting size
- __Font__ - the font to use for burn ins and the watermark
- __Text size__ - the height in pixels of the burn in text, basically the font size
- __Padding__ - the distance in pixels to place the burn ins from the edge of the frame
- __Bitrate__ - the bitrate to encode the output video at. `5000` is a good starting point.
- __MOS TC__ - The text to replace audio timecode with when the clip has no audio timecode or is MOS, usually `MOS`. This currently works with `{Sound TC}` and `{Auxiliary TC1}`.
- __Blanking__ - the aspect ratio to use for applying blanking. Common examples are `2.39`, `2`, `1.85`, etc. Note that pillarboxing is not currently supported.
- __Processes__ - the number of video files to process simultaneously. Higher numbers will be faster up to a point, but may lock up you machine during processing. Optimal value will depend on your setup. `4` is a good starting point.
- __Encoding speed__ - the FFMPEG preset used for encoding. This will not have an effect of bitrate/filesize, just the quality of the encoding. `veryfast` is default, but may not be high enough quality for some use cases.
- __Limit to A1__ - Only include the first audio track in the output. Useful when you are syncing in Avid to all tracks, but only wanting the mix track in the H264s.

#### Using presets

- You can create and save presets by clicking `save preset` and `load preset`
- Presets are saved as `.sasen` files, but they're just CSVs and can be tweaked in any text editor. Note, tweaking them in externals programs may cause things to break!
- By default, presets are stored in a `<install location>/presets` folder. SAS Encoder will automatically load `default.sassen` on startup.

#### Errors and Debugging
- If you are having issues, you should check the terminal window to see if it tells you anything helpful.
- If something goes wrong with the FFMPEG process you may get line in the terminal saying `There may have been some issues...` followed by details on the error.
- The tool will also save details of each job and any errors to the `sasen_logs.txt` file. Sending this to the development team may help them to diagnose you issue. You can periodically delete this file as it grows.

#### Known issues
- The tool will fail to find any clips where the name in the file or the ALE contains special characters, including the star or asterisk sign. This is caused by inconsistent character encoding in Avid.
