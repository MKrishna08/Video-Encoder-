import cv2
import json
import os
import numpy as np


class VideoWriter:
    def __init__(self, output_path, resolution):
        self.output_path = output_path
        self.width, self.height = resolution
        self.video_writer = cv2.VideoWriter(
            output_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (self.width, self.height)
        )
        self.metadata_path = f"{os.path.splitext(output_path)[0]}_metadata.json"
        self.metadata = {"frames": []}

    def write_frame(self, frame, compression_info=None):
        #convert frame to BGR before writing
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        #validate frame properties
        if frame_bgr.shape[:2] != (self.height, self.width):
            raise ValueError(f"Frame resolution {frame_bgr.shape[:2]} does not match VideoWriter resolution {(self.height, self.width)}")
        if frame_bgr.dtype != np.uint8:
            raise ValueError("Frame must be in uint8 format")

        #write the frame
        self.video_writer.write(frame_bgr)

        #optionally write compression metadata
        if compression_info:
            self.write_metadata(compression_info)

    def release(self):
        #release the video writer
        self.video_writer.release()

        #save metadata on release
        self.release_metadata()

    def release_metadata(self):
        print(f"Saving metadata to {self.metadata_path}")  # Debugging
        try:
            #convert metadata to JSON-compatible types
            def convert_to_json_compatible(obj):
                if isinstance(obj, dict):
                    return {str(key): convert_to_json_compatible(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_json_compatible(item) for item in obj]
                elif isinstance(obj, (np.integer, np.uint8, np.int32, np.int64)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float32, np.float64)):
                    return float(obj)
                else:
                    return obj

            sanitized_metadata = convert_to_json_compatible(self.metadata)

            with open(self.metadata_path, 'w') as f:
                json.dump(sanitized_metadata, f)
            print("Metadata saved successfully.")  # Debugging
        except Exception as e:
            print(f"Error while saving metadata: {e}")

    def load_compression_metadata(self):
        #print(f"Loading metadata from {self.metadata_path}")  #debugging
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata file {self.metadata_path} does not exist.")

        with open(self.metadata_path, 'r') as f:
            metadata = json.load(f)
            #print(f"Loaded metadata: {metadata}")  #debugging
            return metadata

    @staticmethod
    def play_video(decoded_frames, framerate=10):
        for frame in decoded_frames:
            cv2.imshow("Video", frame)
            if cv2.waitKey(int(1000 / framerate)) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def write_metadata(self, compression_info):
        #print(f"Adding frame metadata: {compression_info}")  #debugging
        self.metadata["frames"].append({"compression": compression_info})
