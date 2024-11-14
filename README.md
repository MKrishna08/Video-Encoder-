# Video-Encoder-
Video Encoder project for EC504 Fall 24

Requirements: OpenCV and Argparser modules in python.

Note: Before running the main.py file, ensure the images are named in a way that sorts them in the desired order (e.g., frame001.jpg, frame002.jpg, etc.).

Basic Usage: 
python main.py <Location_of_the_folder_containing_images>
eg: if the folder is named images and you're in the current directory then use the command: 
python main.py ./images "on command line"

Custom output filename and framerate: 

python main . py ./images -o my_video.mp4 -r 30 (creates the video file named my_video.mp4 with frame rate of 30fps)


| Feature          | Short Flag | Long Flag      | Description                                   | Type    | Default      | Choices            |
|------------------|------------|----------------|-----------------------------------------------|---------|--------------|--------------------|
| Input Folder     | N/A        | N/A            | Path to the folder containing input images    | String  | N/A          | N/A                |
| Output Filename  | `-o`       | `--output`     | Name of the output video file                 | String  | `output.mp4` | `mp4`, `avi`, `mov`|
| Frame Rate       | `-fr`      | `--framerate`  | Frame rate of the output video (fps)          | Integer | `10`         | N/A                |
| Video Format     | `-f`       | `--format`     | Format of the output video                    | String  | `mp4`        | `mp4`, `avi`, `mov`|
| Resolution       | `-r`       | `--resolution` | Resolution of the output video (WIDTHxHEIGHT) | String  | `640x480`    | N/A                |
| Verbose Mode     | `-v`       | `--verbose`    | Enables verbose output                        | Flag    | `False`      | N/A                |





