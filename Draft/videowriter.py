
import cv2
import json
import os
import numpy as np

class VideoWriter:
    def __init__(self, output_path):
        self.output_path = output_path
        self.video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (640, 480))
        self.metadata_path = f"{os.path.splitext(output_path)[0]}_metadata.json"
        self.metadata = {"frames": []}
    
    def write_frame(self, frame, compression_info=None):
        self.video_writer.write(frame)

        if compression_info:
            # Recursively sanitize compression_info
            def sanitize(obj):
                if isinstance(obj, dict):
                    # Convert keys to strings and recursively sanitize values
                    return {str(key): sanitize(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [sanitize(element) for element in obj]
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.generic):
                    return obj.item()
                return obj


            valid_compression_info = sanitize(compression_info)
            self.metadata["frames"].append(valid_compression_info)

    '''
    def release(self):
        
        self.video_writer.release()
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    '''
    def release(self):
        self.video_writer.release()

        # Ensure metadata is JSON-serializable
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                # Recursively process dictionary values
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                # Recursively process list elements
                return [convert_to_serializable(element) for element in obj]
            elif isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy arrays to lists
            elif isinstance(obj, np.generic):  # Handle NumPy scalars
                return obj.item()  # Convert to Python scalar
            return obj

        try:
            # Recursively process metadata
            serializable_metadata = convert_to_serializable(self.metadata)

            # Debugging: Print sanitized metadata before saving
            #print("Sanitized metadata:", serializable_metadata)

            with open(self.metadata_path, 'w') as f:
                json.dump(serializable_metadata, f)
        except Exception as e:
            print("Error while dumping metadata:", e)
            raise


    def load_compression_metadata(self):
        print('videowriter')
        with open(self.metadata_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def play_video(decoded_frames, framerate=10):
        for frame in decoded_frames:
            print(f"Frame type: {type(frame)}, Frame shape: {frame.shape if isinstance(frame, np.ndarray) else 'Invalid'}")

            if not isinstance(frame, np.ndarray):
                print("Invalid frame detected:", frame)
                continue

            cv2.imshow("Video", frame)
            if cv2.waitKey(int(1000 / framerate)) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()