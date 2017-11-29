This is a final year project for BSc in Computer Science.
The project aims to assist atheletes involved in strength sports by determining the speed of a barbell in a video.

# Usage
`python src/main.py -vp <video_path>`
This will run the program and the bar distance per frame will be logged to a file called `track_barbell.log`. 
If the `-d`flag is specified, the video will play with tracking information video.
Example:
`python src/main.py -vp src/test_squat.mp4 -d`

Graphs can be displayed by using the plot program.
Pass the log file generate by the tracker program to the plot program in order to view graphs of the barbell speed.
Example:
`python src/plot.py --graph all --path src/track_barbell.log`
NOTE: It is important that the log only contains a single run of the tracker program. Running the tracker program multiple times will output to the same log. Please ensure that only one run is present in the log file before you run the graph program. Otherwise the results will be inaccurate.
