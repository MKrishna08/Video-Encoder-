
from arg_parser import CLIArguments
from image_processor import ImageProcessor
from video_writer import VideoWriter

class VideoEncoder:
    """
    Set up the video encoding process.
    """
    def __init__(self):
        """
        Initializes the VideoEncoder by parsing arguments.
        """
        self.args = CLIArguments().get_args()
        self.image_processor = ImageProcessor(
            input_folder=self.args.input_folder,
            width=self.args.width,
            height=self.args.height,
            verbose=self.args.verbose
        )
        self.video_writer = VideoWriter(
            output_path=self.args.output,
            frame_size=(self.args.width, self.args.height),
            framerate=self.args.framerate,
            video_format=self.args.format
        )

    def encode_video(self):
        """
        Processes images and encodes them into a video.
        """
        try:
            for frame in self.image_processor.process_images():
                self.video_writer.write_frame(frame)
            if self.args.verbose:
                print(f"Video successfully saved to '{self.args.output}'.")
        finally:
            self.video_writer.release()
