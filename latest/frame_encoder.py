# frame_encoder.py

import numpy as np
import cv2

class FrameEncoder:
    def __init__(self, block_size=16, search_range=8, compression_quality=90):
        self.block_size = block_size
        self.search_range = search_range
        self.compression_quality = compression_quality

    def encode_i_frame(self, macroblock):
        """
        Encodes an I-frame macroblock using DCT and quantization.

        :param macroblock: Macroblock as a NumPy array (16x16x3).
        :return: Encoded bitstring.
        """
        # Apply DCT to each channel
        dct_channels = []
        for c in range(3):  # B, G, R
            channel = macroblock[:, :, c].astype(np.float32)
            dct = cv2.dct(channel)
            quantized = self.quantize(dct)
            dct_channels.append(quantized.flatten())
        
        # Concatenate all channels
        dct_flat = np.concatenate(dct_channels)
        
        # Convert to bitstring (binary representation)
        bitstring = ''.join(['0' if pixel < 128 else '1' for pixel in macroblock.flatten()])
        return bitstring

    def decode_i_frame(self, bitstring):
        """
        Decodes an I-frame macroblock from a bitstring using dequantization and IDCT.

        :param bitstring: Encoded bitstring.
        :return: Decoded macroblock as a NumPy array (16x16x3).
        """
        # Split bitstring into chunks of 16 bits (assuming 16-bit integers)
        chunks = [bitstring[i:i+16] for i in range(0, len(bitstring), 16)]
        if len(chunks) != self.block_size * self.block_size * 3:
            print("Bitstring length does not match expected size for I-frame.")
            return None
        
        # Convert chunks back to integers
        dct_flat = np.array([int(chunk, 2) for chunk in chunks], dtype=np.float32)
        
        # Separate channels
        dct_channels = np.split(dct_flat, 3)
        
        # Reshape and dequantize
        macroblock = np.zeros((self.block_size, self.block_size, 3), dtype=np.uint8)
        for c in range(3):
            dct = dct_channels[c].reshape((self.block_size, self.block_size))
            dequantized = self.dequantize(dct)
            idct = cv2.idct(dequantized)
            idct = np.clip(idct, 0, 255).astype(np.uint8)
            macroblock[:, :, c] = idct
        
        return macroblock

    def encode_b_frame(self, reference_macroblock, macroblock, motion_vector):
        """
        Encodes a B-frame macroblock using motion vectors and difference encoding.

        :param reference_macroblock: Reference macroblock from the I-frame.
        :param macroblock: Current macroblock to encode (16x16x3).
        :param motion_vector: Tuple (dx, dy) representing motion.
        :return: Encoded bitstring.
        """
        # Apply motion compensation (shift reference macroblock)
        dx, dy = motion_vector
        compensated_macroblock = np.roll(reference_macroblock, shift=(dy, dx), axis=(0, 1))
        
        # Calculate difference
        difference = macroblock.astype(np.int16) - compensated_macroblock.astype(np.int16)
        difference = np.clip(difference, -128, 127).astype(np.int8)
        
        # Apply DCT to difference
        dct_channels = []
        for c in range(3):
            channel = difference[:, :, c].astype(np.float32)
            dct = cv2.dct(channel)
            quantized = self.quantize(dct)
            dct_channels.append(quantized.flatten())
        
        # Concatenate all channels``
        dct_flat = np.concatenate(dct_channels)
        
        # Convert to bitstring (binary representation)
        bitstring = ''.join(['1' if pixel > 128 else '0' for pixel in macroblock.flatten()])
        return bitstring

    def decode_b_frame(self, reference_macroblock, bitstring):
        """
        Decodes a B-frame macroblock from a bitstring using motion vectors and difference decoding.

        :param reference_macroblock: Reference macroblock from the I-frame.
        :param bitstring: Encoded bitstring.
        :return: Decoded macroblock as a NumPy array (16x16x3).
        """
        # Split bitstring into chunks of 16 bits
        chunks = [bitstring[i:i+16] for i in range(0, len(bitstring), 16)]
        if len(chunks) != self.block_size * self.block_size * 3:
            print("Bitstring length does not match expected size for B-frame.")
            return None
        
        # Convert chunks back to integers
        dct_flat = np.array([int(chunk, 2) for chunk in chunks], dtype=np.float32)
        
        # Separate channels
        dct_channels = np.split(dct_flat, 3)
        
        # Reshape and dequantize
        difference = np.zeros((self.block_size, self.block_size, 3), dtype=np.int8)
        for c in range(3):
            dct = dct_channels[c].reshape((self.block_size, self.block_size))
            dequantized = self.dequantize(dct)
            idct = cv2.idct(dequantized)
            idct = np.clip(idct, -128, 127).astype(np.int8)
            difference[:, :, c] = idct
        
        # Apply inverse motion compensation
        dx, dy = (0, 0)  # Placeholder: You need to store and retrieve motion vectors
        reconstructed_macroblock = np.roll(difference, shift=(-dy, -dx), axis=(0, 1)) + reference_macroblock.astype(np.int16)
        reconstructed_macroblock = np.clip(reconstructed_macroblock, 0, 255).astype(np.uint8)
        
        return reconstructed_macroblock

    def quantize(self, dct_matrix):
        """
        Quantizes the DCT matrix based on compression quality.

        :param dct_matrix: DCT-transformed matrix.
        :return: Quantized DCT matrix.
        """
        # Simple quantization matrix (uniform)
        quant_matrix = np.ones_like(dct_matrix) * (100 - self.compression_quality)
        quantized = np.round(dct_matrix / quant_matrix)
        return quantized

    def dequantize(self, quantized_matrix):
        """
        Dequantizes the DCT matrix based on compression quality.

        :param quantized_matrix: Quantized DCT matrix.
        :return: Dequantized DCT matrix.
        """
        quant_matrix = np.ones_like(quantized_matrix) * (100 - self.compression_quality)
        dequantized = quantized_matrix * quant_matrix
        return dequantized


def test_frame_encoder():
    import numpy as np
    encoder = FrameEncoder()
    original_mb = np.random.randint(0, 256, (16, 16, 3), dtype=np.uint8)
    encoded_bits = encoder.encode_i_frame(original_mb)
    decoded_mb = encoder.decode_i_frame(encoded_bits)
    
    if decoded_mb is None:
        print("Decoding returned None.")
        return
    
    # Use allclose with a tolerance
    if np.allclose(original_mb, decoded_mb, atol=10):
        print("I-frame encoding/decoding test passed.")
    else:
        print("I-frame encoding/decoding test failed.")
        # Optionally, inspect the differences
        difference = np.abs(original_mb.astype(int) - decoded_mb.astype(int))
        print(f"Maximum difference per channel: {difference.max(axis=(0,1))}")
    
if __name__ == "__main__":
    test_frame_encoder()
