# main.py
import numpy as np
import argparse
from video_encoder import VideoEncoder
from videowriter import VideoWriter
from image_processor import ImageProcessor


def parse_arguments():
    parser = argparse.ArgumentParser(description="Custom Video Encoder/Decoder")
    parser.add_argument('--command', type=str, choices=['encode', 'view'], required=True, help='Command to execute: encode or view')
    parser.add_argument('--input_folder', type=str, help='Path to input images for encoding')
    parser.add_argument('--output', type=str, default='output.mp4', help='Output video file path')
    parser.add_argument('--metadata', type=str, default='metadata.json', help='Path to metadata file')
    parser.add_argument('--width', type=int, default=480, help='Width of the video frames')
    parser.add_argument('--height', type=int, default=640, help='Height of the video frames')
    parser.add_argument('--framerate', type=int, default=24, help='Frame rate for playback')
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    if args.command == "encode":
        if not args.input_folder:
            print("Error: --input_folder is required for encoding.")
            return

        encoder = VideoEncoder(
            input_folder=args.input_folder,
            output_path=args.output,
            metadata_output_path=args.metadata,
            resolution=(args.width, args.height),
            compression_quality=90,
            codec='h264',
            gop_size=10,
            b_frame_interval=2
        )
        encoder.encode_video()

    elif args.command == "view":
        from playback import fast_forward_playback, reverse_playback

        # Example: Fast Forward Playback
        print("Playing video in fast forward...")
        
        fast_forward_playback(args.output, 'metadata.json', play_speed=1)


        # Example: Reverse Playback
        print("Playing video in reverse...")
        reverse_playback(args.output, 'metadata.json')

if __name__ == "__main__":
        main()
