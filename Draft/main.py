from video_encoder import VideoEncoder
from videowriter import VideoWriter
from arg_parser import CLIArguments
from image_processor import ImageProcessor

def main():
    # Create an instance of CLIArguments and get the parsed arguments
    cli_args = CLIArguments()  # Instantiate CLIArguments
    args = cli_args.get_args()  # Get parsed arguments as a Namespace object
    encoder = VideoEncoder(args.input_folder, args.output, 50)

    #print(args)  # Debug: Display all parsed arguments
    #print(type(args))  # Debug: Show the type of the parsed arguments (should be Namespace)

    if args.command == "encode":
        # Add your encoding logic here, e.g.,
        encoder.encode_video()
        

    elif args.command == "view":
        print("Viewing")
        # Add your viewing logic here, e.g.,
        decoded_frames = encoder.decode_video()
        print('why not?')

        # VideoWriter.play_video(decoded_frames)

if __name__ == "__main__":
    main()
