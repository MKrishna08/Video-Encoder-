# # videowriter.py

# import av
# import numpy as np
# import cv2

# class VideoWriter:
#     def __init__(self, output_path, resolution, codec='h264', frame_rate=24):
#         """
#         Initializes the VideoWriter instance.

#         :param output_path: Path to save the video.
#         :param resolution: Tuple of (width, height).
#         :param codec: Codec to use for video encoding (default: 'h264').
#         :param frame_rate: Frame rate for the video (default: 24).
#         """
#         self.output_path = output_path
#         self.width, self.height = resolution
#         self.codec = codec
#         self.frame_rate = frame_rate

#         # Open container for writing
#         self.container = av.open(output_path, mode='w')

#         # Add video stream
#         self.stream = self.container.add_stream(codec, rate=frame_rate)
#         self.stream.width = self.width
#         self.stream.height = self.height
#         self.stream.pix_fmt = 'yuv420p'  # Common pixel format for many codecs

#         # Metadata for frame types
#         self.frame_types = []  # List to store frame types ('I', 'B')

#     def write_frame(self, frame, frame_type='I'):
#         """
#         Writes a single frame to the video with specified frame type.

#         :param frame: A NumPy array representing the frame (RGB format).
#         :param frame_type: Type of the frame ('I' or 'B').
#         """
#         if frame.shape[:2] != (self.height, self.width):
#             raise ValueError(f"Frame size {frame.shape[:2]} does not match VideoWriter resolution {(self.height, self.width)}")

#         # Store frame type
#         self.frame_types.append(frame_type)

#         # Convert frame to YUV format and encode
#         video_frame = av.VideoFrame.from_ndarray(frame, format='rgb24').reformat(self.width, self.height, 'yuv420p')
#         for packet in self.stream.encode(video_frame):
#             self.container.mux(packet)

#     def close(self):
#         """
#         Closes the video writer, flushing any remaining packets and finalizing the file.
#         """
#         # Flush remaining packets
#         for packet in self.stream.encode():
#             self.container.mux(packet)
#         # Close the container
#         self.container.close()

#         # Save frame types metadata
#         with open('frame_types.json', 'w') as f:
#             json.dump(self.frame_types, f, indent=4)

#     @staticmethod
#     def play_video(frames, framerate=24, window_name='Video'):
#         """
#         Plays a list of frames using OpenCV.

#         :param frames: List of NumPy arrays representing frames.
#         :param framerate: Playback framerate.
#         :param window_name: Name of the display window.
#         """
#         cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
#         for frame in frames:
#             cv2.imshow(window_name, frame)
#             if cv2.waitKey(int(1000 / framerate)) & 0xFF == ord('q'):
#                 break
#         cv2.destroyAllWindows()

   
   # videowriter.py

import av
import numpy as np
import cv2

class VideoWriter:
    def __init__(self, output_path, resolution, codec='h264', frame_rate=24):
        """
        Initializes the VideoWriter instance.

        :param output_path: Path to save the video.
        :param resolution: Tuple of (width, height).
        :param codec: Codec to use for video encoding (default: 'h264').
        :param frame_rate: Frame rate for the video (default: 24).
        """
        self.output_path = output_path
        self.width, self.height = resolution
        self.codec = codec
        self.frame_rate = frame_rate

        # Open container for writing
        self.container = av.open(output_path, mode='w')

        # Add video stream
        self.stream = self.container.add_stream(codec, rate=frame_rate)
        self.stream.width = self.width
        self.stream.height = self.height
        self.stream.pix_fmt = 'yuv420p'  # Common pixel format for many codecs

    def write_frame(self, frame):
        """
        Writes a single frame to the video.

        :param frame: A NumPy array representing the frame (RGB format).
        """
        if frame.shape[:2] != (self.height, self.width):
            raise ValueError(f"Frame size {frame.shape[:2]} does not match VideoWriter resolution {(self.height, self.width)}")

        # Convert frame to YUV format and encode
        video_frame = av.VideoFrame.from_ndarray(frame, format='rgb24').reformat(self.width, self.height, 'yuv420p')
        for packet in self.stream.encode(video_frame):
            self.container.mux(packet)

    def close(self):
        """
        Closes the video writer, flushing any remaining packets and finalizing the file.
        """
        # Flush remaining packets
        for packet in self.stream.encode():
            self.container.mux(packet)
        # Close the container
        self.container.close()

    @staticmethod
    def play_video(frames, framerate=24, window_name='Video'):
        """
        Plays a list of frames using OpenCV.

        :param frames: List of NumPy arrays representing frames.
        :param framerate: Playback framerate.
        :param window_name: Name of the display window.
        """
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        for frame in frames:
            cv2.imshow(window_name, frame)
            if cv2.waitKey(int(1000 / framerate)) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
