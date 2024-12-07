# video_encoder.py

import json
import numpy as np
import cv2
from math import ceil
from image_processor import ImageProcessor
from videowriter import VideoWriter
from huffman_coder import HuffmanCoder
from macroblock_processor import MacroblockProcessor
from frame_encoder import FrameEncoder  
from motion_estimator import MotionEstimator


class VideoEncoder:
    def __init__(self, input_folder, output_path, metadata_output_path, resolution, compression_quality=90, codec='h264', gop_size=10, b_frame_interval=2):
        """
        Initializes the VideoEncoder instance.

        :param input_folder: Path to input images.
        :param output_path: Path to save the encoded video.
        :param metadata_output_path: Path to save metadata.
        :param resolution: Tuple of (width, height).
        :param compression_quality: Quality factor for quantization.
        :param codec: Codec to use for video encoding.
        :param gop_size: Number of frames in a Group of Pictures (GOP).
        :param b_frame_interval: Interval between B-frames.
        """
        self.image_processor = ImageProcessor(input_folder, verbose=True)
        self.video_writer = VideoWriter(output_path, resolution, codec=codec)
        self.width, self.height = resolution
        self.compression_quality = compression_quality
        self.metadata_output_path = metadata_output_path
        self.gop_size = gop_size
        self.b_frame_interval = b_frame_interval

        # Initialize FrameEncoder
        self.frame_encoder = FrameEncoder(block_size=16, search_range=8, compression_quality=compression_quality)
        # Initialize MotionEstimator here
        self.motion_estimator = MotionEstimator(search_range=8, block_size=16)

    def pad_frame(self, frame):
        """
        Pads the frame so that its dimensions are multiples of block_size.

        :param frame: Original frame as a NumPy array.
        :return: Padded frame.
        """
        block_size = self.frame_encoder.block_size
        height, width, channels = frame.shape

        # Calculate the required padding for height and width
        new_height = ceil(height / block_size) * block_size
        new_width = ceil(width / block_size) * block_size

        pad_bottom = new_height - height
        pad_right = new_width - width

        # Apply padding using BORDER_REPLICATE to replicate the edge pixels
        padded_frame = cv2.copyMakeBorder(frame, 0, pad_bottom, 0, pad_right, cv2.BORDER_REPLICATE)
        print(f"Padded frame shape: {padded_frame.shape}")  # Debug statement
        return padded_frame

    def unpad_frame(self, padded_frame):
        """
        Removes padding from the frame to restore original dimensions.

        :param padded_frame: Padded frame as a NumPy array.
        :return: Unpadded frame.
        """
        original_height = self.height
        original_width = self.width
        unpadded_frame = padded_frame[0:original_height, 0:original_width]
        print(f"Unpadded frame shape: {unpadded_frame.shape}")  # Debug statement
        return unpadded_frame

    def encode_video(self):
        compressed_data_list = []
        codes_list = []
        frame_lengths = []
        frame_types = []

        frames = list(self.image_processor.process_images())
        total_frames = len(frames)
        print(f"Total frames to encode: {total_frames}")

        # Initialize MacroblockProcessor
        mbp = MacroblockProcessor(block_size=16)

        for i in range(0, total_frames, self.gop_size):
            gop = frames[i:i + self.gop_size]
            gop_length = len(gop)
            print(f"Encoding GOP starting at frame {i+1} with {gop_length} frames.")

            # Previous I-frame reference
            i_frame_reference = None

            for j, frame in enumerate(gop):
                frame_number = i + j + 1
                if j == 0:
                    # I-frame
                    frame_type = 'I'
                    # Resize the reference frame to (640, 480)
                    resized_ref_frame = cv2.resize(frame, (self.width, self.height))
                    # Pad the reference frame
                    i_frame_reference = self.pad_frame(resized_ref_frame).copy()
                elif (j % (self.b_frame_interval + 1)) == 0:
                    # P-frame
                    frame_type = 'P'
                else:
                    # B-frame
                    frame_type = 'B'

                frame_types.append(frame_type)

                # Resize frame to (640, 480)
                resized_frame = cv2.resize(frame, (self.width, self.height))
                print(f"Processing frame {frame_number}: Resized shape {resized_frame.shape}")  # Debug

                # Pad frame to ensure macroblocks are full-sized
                padded_frame = self.pad_frame(resized_frame)
                print(f"Processing frame {frame_number}: Padded shape {padded_frame.shape}")  # Debug

                # Split into macroblocks
                macroblocks = mbp.split_into_macroblocks(padded_frame)
                print(f"Number of macroblocks: {len(macroblocks)}")  # Debug

                # If P or B frame, estimate motion relative to I-frame reference or another reference frame
                if frame_type in ['P', 'B'] and i_frame_reference is not None:
                    motion_vectors = self.motion_estimator.estimate_motion(i_frame_reference, padded_frame)
                else:
                    motion_vectors = [(0, 0)] * len(macroblocks)

                # Lists to store encoded macroblocks
                encoded_macroblocks = []

                # Process each macroblock
                for idx, mb in enumerate(macroblocks):
                    print(f"Macroblock {idx+1} shape: {mb.shape}")  # Debug
                    if frame_type == 'I':
                        # I-frame: Encode macroblock directly using FrameEncoder
                        encoded_mb = self.frame_encoder.encode_i_frame(mb)
                    else:
                        mv = motion_vectors[idx]

                        # Determine the macroblock's position
                        blocks_per_row = self.width // self.frame_encoder.block_size
                        row = idx // blocks_per_row
                        col = idx % blocks_per_row
                        y = row * self.frame_encoder.block_size
                        x = col * self.frame_encoder.block_size

                        # Apply motion vector to get reference macroblock's top-left corner
                        ref_y = y + mv[1]
                        ref_x = x + mv[0]

                        # Ensure reference positions are within frame boundaries
                        ref_y = min(max(ref_y, 0), self.height - self.frame_encoder.block_size)
                        ref_x = min(max(ref_x, 0), self.width - self.frame_encoder.block_size)

                        # Extract reference macroblock from i_frame_reference
                        reference_mb = i_frame_reference[ref_y:ref_y+self.frame_encoder.block_size, ref_x:ref_x+self.frame_encoder.block_size, :]

                        # Encode B-frame macroblock
                        encoded_mb = self.frame_encoder.encode_b_frame(reference_mb, mb, mv)

                    encoded_macroblocks.append(encoded_mb)

                # Combine encoded macroblocks into one bitstring
                encoded_data = ''.join(encoded_macroblocks)
                compressed_data_list.append(encoded_data)
                codes_list.append({})  # Placeholder: Store Huffman codes if needed
                frame_lengths.append(len(encoded_data))

                print(f"Encoded frame {frame_number} as {frame_type}-frame.")

        # Save compressed data
        with open('compressed_data.bin', 'wb') as f:
            for data in compressed_data_list:
                if len(data) % 8 != 0:
                    data = data.ljust(len(data) + (8 - len(data) % 8), '0')  # Pad with zeros to make it byte-aligned
                byte_data = int(data, 2).to_bytes(len(data) // 8, byteorder='big')
                f.write(byte_data)
                print(f"Written {len(byte_data)} bytes of compressed data.")  # Debug statement

        # Save metadata
        metadata = {
            'version': '1.0',
            'resolution': (self.width, self.height),
            'frame_rate': self.video_writer.frame_rate,
            'compression_quality': self.compression_quality,
            'gop_size': self.gop_size,
            'b_frame_interval': self.b_frame_interval,
            'frames': []
        }

        for frame_idx, (frame_type, codes, length) in enumerate(zip(frame_types, codes_list, frame_lengths), start=1):
            frame_metadata = {
                'frame_number': frame_idx,
                'frame_type': frame_type,
                'codes': codes,
                'length': length
            }
            metadata['frames'].append(frame_metadata)

        with open(self.metadata_output_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            print(f"Metadata saved to {self.metadata_output_path}")  # Debug statement

        # Close the video writer
        self.video_writer.close()
        print("Encoding complete.")

    def decode_video(self):
        # Load metadata
        with open(self.metadata_output_path, 'r') as f:
            metadata = json.load(f)

        frames_metadata = metadata['frames']
        width, height = metadata['resolution']
        compression_quality = metadata['compression_quality']

        # Load compressed data
        with open('compressed_data.bin', 'rb') as f:
            compressed_data_bytes = f.read()

        # Convert bytes back to bitstring
        compressed_bitstring = ''.join(f'{byte:08b}' for byte in compressed_data_bytes)
        print(f"Total bits loaded: {len(compressed_bitstring)}")  # Debug

        # Initialize MacroblockProcessor
        mbp = MacroblockProcessor(block_size=16)

        decoded_frames = []
        idx = 0
        i_frame_reference = None  # To keep track of the latest I-frame

        for frame_info in frames_metadata:
            frame_number = frame_info['frame_number']
            frame_type = frame_info['frame_type']
            codes = frame_info['codes']
            frame_bits_length = frame_info['length']

            frame_bits = compressed_bitstring[idx:idx + frame_bits_length]
            idx += frame_bits_length
            print(f"Decoding frame {frame_number}: {len(frame_bits)} bits")  # Debug

            if frame_type == 'I':
                # Decode I-frame
                reconstructed_mbs = self.frame_encoder.decode_i_frame(frame_bits)
                if reconstructed_mbs is None:
                    print(f"Frame {frame_number} I-frame decoding failed.")
                    continue
                # Reconstruct frame from macroblocks
                frame = mbp.reconstruct_frame(reconstructed_mbs, width, height)
                # Remove padding if any
                unpadded_frame = self.unpad_frame(frame)
                i_frame_reference = unpadded_frame.copy()
                decoded_frames.append(unpadded_frame)
                print(f"Decoded and unpadded frame {frame_number} as I-frame.")
            elif frame_type == 'B':
                # Decode B-frame using the latest I-frame reference
                reconstructed_mbs = self.frame_encoder.decode_b_frame(i_frame_reference, frame_bits)
                if reconstructed_mbs is None:
                    print(f"Frame {frame_number} B-frame decoding failed.")
                    continue
                frame = mbp.reconstruct_frame(reconstructed_mbs, width, height)
                # Remove padding if any
                unpadded_frame = self.unpad_frame(frame)
                decoded_frames.append(unpadded_frame)
                print(f"Decoded and unpadded frame {frame_number} as B-frame.")
            elif frame_type == 'P':
                # Decode P-frame (similar to I-frame but using prediction)
                # Implement decode_p_frame if needed
                print(f"Frame {frame_number} is a P-frame. Decoding not implemented.")
                continue
            else:
                print(f"Frame {frame_number} has an unknown frame type: {frame_type}")
                continue

        return decoded_frames
