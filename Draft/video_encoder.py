
import numpy as np
import cv2
from image_processor import ImageProcessor
from videowriter import VideoWriter
from huffman_coder import HuffmanCoder

class CompressionTechniques:
    @staticmethod
    #One of the compression techniques is Discrete Cosine Transformation to reduce spatial redundancy 
    def apply_dct(frame, quality=50):
        frame_float = np.float32(frame)
        
        dct_channels = []
        for channel in cv2.split(frame_float):
            dct_channel = cv2.dct(channel)
            dct_channels.append(CompressionTechniques.quantize(dct_channel, quality))
        
        return cv2.merge(dct_channels)
    
    #IDCT for playback
    @staticmethod
    def apply_idct(dct_frame):
        idct_channels = []
        for channel in cv2.split(dct_frame):
            idct_channel = cv2.idct(channel)
            idct_channels.append(idct_channel)
        return cv2.merge(idct_channels)

    @staticmethod
    #Another technique is quantization to reduce less significant details, effectively compressing the data.
    def quantize(dct_matrix, quality):
        quantization_factor = 255 * (100 - quality) / 100
        quantization_matrix = np.ones_like(dct_matrix) * quantization_factor
        quantized = np.round(dct_matrix / quantization_matrix) * quantization_matrix
        return quantized
    
    #Dequantizing for playback
    @staticmethod
    def dequantize(quantized_matrix, quality):
        quantization_factor = 255 * (100 - quality) / 100
        quantization_matrix = np.ones_like(quantized_matrix) * quantization_factor
        return quantized_matrix / quantization_matrix



class VideoEncoder:
    def __init__(self, input_folder, output_path, compression_quality=50):
        self.image_processor = ImageProcessor(input_folder, verbose= True)
        self.video_writer = VideoWriter(output_path)
        self.compression_quality = compression_quality

    def encode_video(self):
        for frame in self.image_processor.process_images():
            compressed_frame = CompressionTechniques.apply_dct(frame, self.compression_quality)
            flattened_frame = compressed_frame.flatten()
            huffman_result = HuffmanCoder.compress(flattened_frame.astype(np.uint8))

            huffman_result['codes'] = {str(key): value for key, value in huffman_result['codes'].items()}

            self.video_writer.write_frame(compressed_frame.astype(np.uint8), huffman_result)
        self.video_writer.release()
        print('done')

    def decode_video(self):
        print('Calling the function')
        metadata = self.video_writer.load_compression_metadata()
        print(metadata['frames'].keys())
        for frame_metadata in metadata["frames"]:
            compressed_data = frame_metadata["compression"]["encoded_data"]
            decompressed_data = HuffmanCoder.decompress(compressed_data)
            dequantized_matrix = CompressionTechniques.dequantize(
                np.array(decompressed_data).reshape(self.video_writer.frame_size), 
                self.compression_quality
            )
            reconstructed_frame = CompressionTechniques.apply_idct(dequantized_matrix)

            # Debugging: Check reconstructed frame
            print(f"Reconstructed frame type: {type(reconstructed_frame)}, shape: {reconstructed_frame.shape if isinstance(reconstructed_frame, np.ndarray) else 'Invalid'}")

            #yield reconstructed_frame.astype(np.uint8)
