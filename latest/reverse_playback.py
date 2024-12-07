# reverse_playback.py

import cv2
import json
from videowriter import VideoWriter

def reverse_playback(encoded_video_path, frame_types_path, window_name='Reverse Video'):
    """
    Plays the video in reverse.

    :param encoded_video_path: Path to the encoded video file.
    :param frame_types_path: Path to the frame types metadata.
    :param window_name: Name of the display window.
    """
    # Load frame types
    with open(frame_types_path, 'r') as f:
        frame_types = json.load(f)

    # Open the video using PyAV
    container = av.open(encoded_video_path)
    stream = container.streams.video[0]

    # Read all frames into a list
    frames = []
    for frame in container.decode(stream):
        img = frame.to_ndarray(format='bgr24')
        frames.append(img)

    # Initialize OpenCV window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Play frames in reverse
    for img, frame_type in zip(reversed(frames), reversed(frame_types)):
        cv2.imshow(window_name, img)
        if cv2.waitKey(int(1000 / stream.rate)) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    container.close()

# Usage Example
if __name__ == "__main__":
    reverse_playback('output.mp4', 'frame_types.json')
