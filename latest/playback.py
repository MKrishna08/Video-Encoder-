# # playback.py

# import cv2
# import json
# import av
# from videowriter import VideoWriter

# def fast_forward_playback(video_path, metadata_path, play_speed=4):
#     # Load metadata
#     with open(metadata_path, 'r') as file:
#         metadata = json.load(file)
    
#     frames_metadata = metadata['frames']
    
#     # Open video using OpenCV
#     cap = cv2.VideoCapture(video_path)
    
#     if not cap.isOpened():
#         print(f"Error: Cannot open video {video_path}")
#         return
    
#     frame_count = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         frame_info = frames_metadata[frame_count]
#         frame_type = frame_info['frame_type']
        
#         # Implement fast forward logic
#         if frame_type == 'B':
#             # For example, skip B-frames during fast forward
#             frame_count += 1
#             continue
        
#         # Display the frame
#         cv2.imshow('Fast Forward Playback', frame)
        
#         # Control playback speed
#         key = cv2.waitKey(int(1000 / (metadata['frame_rate'] * play_speed))) & 0xFF
#         if key == ord('q'):
#             break
        
#         frame_count += 1
    
#     cap.release()
#     cv2.destroyAllWindows()
# def reverse_playback(encoded_video_path, frame_types_path, window_name='Reverse Video'):
#     """
#     Plays the video in reverse order.

#     :param encoded_video_path: Path to the encoded video file.
#     :param frame_types_path: Path to the frame types metadata.
#     :param window_name: Name of the display window.
#     """
#     # Load frame types
#     with open(frame_types_path, 'r') as f:
#         frame_types = json.load(f)

#     # Open the video using PyAV
#     container = av.open(encoded_video_path)
#     stream = container.streams.video[0]
#     stream.thread_type = 'AUTO'

#     # Read all frames into a list
#     frames = []
#     for frame in container.decode(stream):
#         img = frame.to_ndarray(format='bgr24')
#         frames.append(img)

#     # Initialize OpenCV window
#     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

#     # Play frames in reverse
#     for img, frame_type in zip(reversed(frames), reversed(frame_types)):
#         cv2.imshow(window_name, img)
#         # Adjust waitKey based on frame rate
#         wait_time = max(int(1000 / stream.rate), 1)
#         if cv2.waitKey(wait_time) & 0xFF == ord('q'):
#             break

#     cv2.destroyAllWindows()
#     container.close()

# # Usage Example
# if __name__ == "__main__":
#     fast_forward_playback('output.mp4', 'frame_types.json', play_speed=4)

# playback.py

import cv2
import json

def fast_forward_playback(video_path, metadata_path, play_speed=4):
    """
    Plays the video in fast-forward mode, potentially skipping certain frame types.
    
    :param video_path: Path to the video file.
    :param metadata_path: Path to the metadata JSON file.
    :param play_speed: Speed multiplier for playback.
    """
    # Load metadata
    try:
        with open(metadata_path, 'r') as file:
            metadata = json.load(file)
    except FileNotFoundError:
        print(f"Error: '{metadata_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{metadata_path}' contains invalid JSON.")
        return

    # Extract frame types
    frames_metadata = metadata.get('frames', [])
    frame_types = [frame['frame_type'] for frame in frames_metadata]

    # Open video using OpenCV
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video '{video_path}'.")
        return

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    display_delay = int(1000 / (frame_rate * play_speed))  # in milliseconds

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count >= len(frame_types):
            print("Warning: More frames in video than metadata.")
            break

        frame_type = frame_types[frame_count]

        # Implement fast forward logic
        # Example: Skip B-frames during fast forward
        if frame_type == 'B':
            frame_count += 1
            continue

        # Display the frame
        cv2.imshow('Fast Forward Playback', frame)

        # Control playback speed
        key = cv2.waitKey(display_delay) & 0xFF
        if key == ord('q'):
            print("Fast forward playback interrupted by user.")
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()


def reverse_playback(video_path, metadata_path, play_speed=4, window_name='Reverse Playback'):
    """
    Plays the video in reverse order, potentially applying logic based on frame types.
    
    :param video_path: Path to the video file.
    :param metadata_path: Path to the metadata JSON file.
    :param play_speed: Speed multiplier for playback.
    :param window_name: Name of the display window.
    """
    # Load metadata
    try:
        with open(metadata_path, 'r') as file:
            metadata = json.load(file)
    except FileNotFoundError:
        print(f"Error: '{metadata_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{metadata_path}' contains invalid JSON.")
        return

    # Extract frame types and frame order
    frames_metadata = metadata.get('frames', [])
    frame_types = [frame['frame_type'] for frame in frames_metadata]
    total_frames = len(frame_types)

    # Open video using OpenCV
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video '{video_path}'.")
        return

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    display_delay = int(1000 / (frame_rate * play_speed))  # in milliseconds

    # Read all frames into a list
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    if len(frames) != total_frames:
        print("Warning: Number of frames in video and metadata do not match.")
        # Adjust total_frames if necessary
        total_frames = min(len(frames), total_frames)
        frames_metadata = frames_metadata[:total_frames]
        frame_types = frame_types[:total_frames]

    # Reverse the frames and corresponding metadata
    reversed_frames = frames[:total_frames][::-1]
    reversed_frame_types = frame_types[:total_frames][::-1]

    # Initialize OpenCV window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    for idx, (frame, frame_type) in enumerate(zip(reversed_frames, reversed_frame_types)):
        # Implement reverse playback logic
        # Example: Skip I-frames during reverse playback
        if frame_type == 'I':
            continue  # Skip I-frames

        # Display the frame
        cv2.imshow(window_name, frame)

        # Control playback speed
        key = cv2.waitKey(display_delay) & 0xFF
        if key == ord('q'):
            print("Reverse playback interrupted by user.")
            break

    cv2.destroyAllWindows()


# Usage Example
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Video Playback Tool")
    parser.add_argument('--video', type=str, required=True, help='Path to the video file (e.g., output.mp4)')
    parser.add_argument('--metadata', type=str, required=True, help='Path to the metadata JSON file (e.g., metadata.json)')
    parser.add_argument('--play_speed', type=int, default=4, help='Playback speed multiplier')
    parser.add_argument('--mode', type=str, choices=['fast_forward', 'reverse', 'both'], default='fast_forward',
                        help='Playback mode: fast_forward, reverse, or both')

    args = parser.parse_args()

    if args.mode in ['fast_forward', 'both']:
        print("Starting Fast Forward Playback...")
        fast_forward_playback(args.video, args.metadata, play_speed=args.play_speed)
    
    if args.mode in ['reverse', 'both']:
        print("Starting Reverse Playback...")
        reverse_playback(args.video, args.metadata, play_speed=args.play_speed)
