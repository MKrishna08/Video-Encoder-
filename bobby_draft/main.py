from video_encoder import VideoEncoder
from videowriter import VideoWriter
from arg_parser import CLIArguments

def main():
    cli_args = CLIArguments()  
    args = cli_args.get_args()  

    encoder = VideoEncoder(
        input_folder=args.input_folder,
        output_path=args.output,
        resolution=(args.width, args.height),
        compression_quality=90
    )

    if args.command == "encode":
        encoder.encode_video()
        

    elif args.command == "view":
        decoded_frames = encoder.decode_video()
        if decoded_frames:
            VideoWriter.play_video(decoded_frames, framerate=args.framerate)
        else:
            print("no decoded frames to view")

if __name__ == "__main__":
    main()
