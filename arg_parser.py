"""
The arg_parser file contains the commands you can use on the CLI to provide additional
options to the program. The description is provided in the docstring of the CLIArguments class.
"""

import argparse
import os


def parse_resolution(value):
    """
    Parses the resolution string in the format WIDTHxHEIGHT and returns a tuple of integers.

    Args:
        value (str): Resolution string, e.g., "1920x1080"

    Returns:
        tuple: (width, height)

    Raises:
        argparse.ArgumentTypeError: If the format is incorrect or values are not integers.
    """
    try:
        width, height = map(int, value.lower().split('x'))
        return (width, height)
    except ValueError:
        raise argparse.ArgumentTypeError("Resolution must be in the format WIDTHxHEIGHT, e.g., 640x480.")


class CLIArguments:
    """
    Parses and stores command-line arguments for the program.
    """

    def __init__(self):
        # Create an instance of ArgumentParser
        self.parser = argparse.ArgumentParser(
            description="Convert a sequence of images into a video with specified settings."
        )
        self._add_arguments()  # Add command-line arguments to the parser (private)
        self.args = self.parser.parse_args()  # Contains all the arguments after being parsed as attributes
        self._validate_arguments()  # Validate the arguments to ensure they adhere to criteria (private)

    def _add_arguments(self):
        """
        Adds the command-line arguments to the parser.
        """
        # Positional argument: input folder (must be provided in the CLI)
        self.parser.add_argument(
            'input_folder',
            type=str,
            help='Path to the folder containing input images.'
        )

        # Optional arguments
        self.parser.add_argument(
            '-o', '--output',
            type=str,
            default='output.mp4',
            help='Name of the output video file (default: output.mp4).'
        )
        self.parser.add_argument(
            '-fr', '--framerate',
            type=int,
            default=10,
            help='Frame rate for the output video (default: 10).'
        )
        self.parser.add_argument(
            '-fmt', '--video-format',
            type=str,
            choices=['mp4', 'avi', 'mov'],
            default='mp4',
            help='Output video format (default: mp4).'
        )
        self.parser.add_argument(
            '-r', '--resolution',
            type=parse_resolution,
            default=(640, 480),
            metavar='WIDTHxHEIGHT',
            help='Resolution of the output video in WIDTHxHEIGHT format (e.g., 1920x1080). Default is 640x480.'
        )
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose output for debugging.'
        )

    def _validate_arguments(self):
        """
        Validates the parsed command-line arguments.
        """
        # Validate input folder
        if not os.path.isdir(self.args.input_folder):
            self.parser.error(f"The folder '{self.args.input_folder}' does not exist.")

        # Resolution is already parsed and validated by the custom type
        self.args.width, self.args.height = self.args.resolution

    def get_args(self):
        """
        Returns the parsed arguments.

        Returns:
            Namespace: Parsed command-line arguments.
        """
        return self.args
