
import numpy as np
import cv2
from image_processor import ImageProcessor
from videowriter import VideoWriter
from huffman_coder import HuffmanCoder

class CompressionTechniques:
    @staticmethod
    def apply_dct(frame, quality=500):
        #convert to BGR if needed
        if frame.shape[2] == 3:  #ensure 3 channels for color
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            frame_bgr = frame

        #normalize to range [0, 1]
        frame_float = np.float32(frame_bgr) / 255.0

        dct_channels = []
        for channel in cv2.split(frame_float):  #split into color channels
            dct_channel = cv2.dct(channel)  #apply DCT
            dct_channels.append(CompressionTechniques.quantize(dct_channel, quality))  #quantize
        return cv2.merge(dct_channels)

    @staticmethod
    def apply_idct(dct_frame):
        #normalize DCT coefficients for IDCT
        dct_frame = dct_frame / dct_frame.max()  # Normalize to [0, 1]

        idct_channels = []
        for channel in cv2.split(dct_frame):  #split into color channels
            idct_channel = cv2.idct(channel)  #apply IDCT
            idct_channels.append(idct_channel)

        reconstructed_frame = cv2.merge(idct_channels)
        reconstructed_frame = (reconstructed_frame * 255.0).clip(0, 255)  #scale back to [0, 255]
        return cv2.cvtColor(reconstructed_frame.astype(np.uint8), cv2.COLOR_BGR2RGB)  #convert back to RGB




    @staticmethod
    def quantize(dct_matrix, quality):
        #quantization factor adjusted for normalized DCT coefficients
        quantization_factor = (100 - quality) / 50.0  # Reduced scaling
        quantization_matrix = np.ones_like(dct_matrix) * quantization_factor
        quantized = np.round(dct_matrix / quantization_matrix)  # Quantize
        return quantized

    @staticmethod
    def dequantize(quantized_matrix, quality):
        #match quantization scale for dequantization
        quantization_factor = (100 - quality) / 50.0
        quantization_matrix = np.ones_like(quantized_matrix) * quantization_factor
        return quantized_matrix * quantization_matrix


    
class VideoEncoder:
    def __init__(self, input_folder, output_path, resolution, compression_quality=90):
        self.image_processor = ImageProcessor(input_folder, verbose= True)
        self.video_writer = VideoWriter(output_path, resolution)
        self.width, self.height = resolution
        self.compression_quality = compression_quality

    def encode_video(self):
        for frame_idx, frame in enumerate(self.image_processor.process_images(), start=1):
            print(f"Processing frame {frame_idx} with shape {frame.shape}.")  # Debugging

            #apply compression (DCT and quantization)
            compressed_frame = CompressionTechniques.apply_dct(frame, self.compression_quality)
            flattened_frame = compressed_frame.flatten()

            #huffman compression
            huffman_result = HuffmanCoder.compress(flattened_frame.astype(np.uint8))
            compression_info = {
                "encoded_data": huffman_result['encoded_data'],
                "codes": huffman_result['codes']
            }

            #debug to make sure compression info not empty
            #print(f"Frame {frame_idx} compression info: {compression_info}")  # Debugging

            #write metadata
            self.video_writer.write_metadata(compression_info)
            #print(f"Frame {frame_idx} metadata written.")  # Debugging

            #reconstruct frame for writing to video
            dequantized_matrix = CompressionTechniques.dequantize(
                flattened_frame.reshape(self.height, self.width, 3),
                self.compression_quality
            )
            reconstructed_frame = CompressionTechniques.apply_idct(dequantized_matrix)
            self.video_writer.write_frame(reconstructed_frame.astype(np.uint8))

        #save metadata
        self.video_writer.release_metadata()
        self.video_writer.release()
        print("Encoding complete.")




    def decode_video(self):
        metadata = self.video_writer.load_compression_metadata()
        decoded_frames = []

        if "frames" not in metadata or not metadata["frames"]:
            print("Error: No frames found in metadata.")
            return []

        for frame_metadata in metadata["frames"]:
            if "compression" not in frame_metadata:
                print("Error: Missing compression metadata in frame.")
                continue

            encoded_data = frame_metadata["compression"]["encoded_data"]
            codes = frame_metadata["compression"]["codes"]

            #decompress
            decompressed_data = HuffmanCoder.decompress(encoded_data, codes)
            if not decompressed_data:
                print("Error: Decompressed data is empty.")
                continue

            decompressed_array = np.array(decompressed_data, dtype=np.float32)

            #dequantize
            try:
                dequantized_matrix = CompressionTechniques.dequantize(
                    decompressed_array.reshape(self.height, self.width, 3),
                    self.compression_quality
                )
            except ValueError as e:
                print(f"Error in reshaping or dequantization: {e}")
                continue

            #reconstruct frame
            reconstructed_frame = CompressionTechniques.apply_idct(dequantized_matrix)
            reconstructed_frame_rgb = cv2.cvtColor(reconstructed_frame.astype(np.uint8), cv2.COLOR_BGR2RGB)
            decoded_frames.append(reconstructed_frame_rgb)

        print(f"Decoded {len(decoded_frames)} frames.")
        return decoded_frames






