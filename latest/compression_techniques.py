# compression_techniques.py

import numpy as np
import cv2

class CompressionTechniques:
    @staticmethod
    def apply_dct(frame, quality=500):
        if frame.shape[2] == 3:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            frame_bgr = frame
        frame_float = np.float32(frame_bgr) / 255.0
        dct_channels = []
        for channel in cv2.split(frame_float):
            dct_channel = cv2.dct(channel)
            dct_channels.append(CompressionTechniques.quantize(dct_channel, quality))
        return cv2.merge(dct_channels)

    @staticmethod
    def apply_idct(dct_frame):
        dct_frame = dct_frame / np.max(dct_frame) if np.max(dct_frame) != 0 else dct_frame
        idct_channels = []
        for channel in cv2.split(dct_frame):
            idct_channel = cv2.idct(channel)
            idct_channels.append(idct_channel)
        reconstructed_frame = cv2.merge(idct_channels)
        reconstructed_frame = (reconstructed_frame * 255.0).clip(0, 255)
        return cv2.cvtColor(reconstructed_frame.astype(np.uint8), cv2.COLOR_BGR2RGB)

    @staticmethod
    def quantize(dct_matrix, quality):
        quantization_factor = (100 - quality) / 50.0
        quantization_matrix = np.ones_like(dct_matrix) * quantization_factor
        quantized = np.round(dct_matrix / quantization_matrix)
        return quantized

    @staticmethod
    def dequantize(quantized_matrix, quality):
        quantization_factor = (100 - quality) / 50.0
        quantization_matrix = np.ones_like(quantized_matrix) * quantization_factor
        return quantized_matrix * quantization_matrix
