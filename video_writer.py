
import cv2

class VideoWriter:
    """
    Encapsulates OpenCV's VideoWriter functionality.
    """
    FOURCC_CODES = {
        'mp4': 'mp4v',
        'avi': 'XVID',
        'mov': 'mp4v'
    }

    def __init__(self, output_path, frame_size, framerate, video_format):
        """
        Initializes the VideoWriter.

        Args:
            output_path (str): Path to the output video file.
            frame_size (tuple): (width, height) of the video frames.
            framerate (int): Frame rate of the video.
            video_format (str): Output video format.
        """
        self.output_path = output_path
        self.frame_size = frame_size
        self.framerate = framerate
        self.video_format = video_format
        self.video_writer = self._initialize_writer()

    def _initialize_writer(self):
        """
        Initializes the OpenCV VideoWriter object.

        Returns:
            cv2.VideoWriter: Initialized VideoWriter object.

        Raises:
            IOError: If the VideoWriter cannot be opened.
        """
        fourcc = cv2.VideoWriter_fourcc(*self.FOURCC_CODES.get(self.video_format, 'mp4v'))
        writer = cv2.VideoWriter(self.output_path, fourcc, self.framerate, self.frame_size)
        if not writer.isOpened():
            raise IOError(f"Cannot open video writer with path '{self.output_path}'.")
        return writer

    def write_frame(self, frame):
        """
        Writes a single frame to the video.

        Args:
            frame (numpy.ndarray): Image frame to write.
        """
        self.video_writer.write(frame)

    def release(self):
        """
        Releases the VideoWriter resource.
        """
        self.video_writer.release()
