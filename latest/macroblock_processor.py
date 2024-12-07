# macroblock_processor.py

import numpy as np

class MacroblockProcessor:
    def __init__(self, block_size=16):
        self.block_size = block_size

    def split_into_macroblocks(self, frame):
        """
        Splits the frame into macroblocks.

        :param frame: Padded frame as a NumPy array.
        :return: List of macroblocks.
        """
        blocks = []
        height, width, channels = frame.shape
        for y in range(0, height, self.block_size):
            for x in range(0, width, self.block_size):
                mb = frame[y:y+self.block_size, x:x+self.block_size]
                blocks.append(mb)
        return blocks

    def reconstruct_frame(self, macroblocks, width, height):
        """
        Reconstructs the frame from macroblocks.

        :param macroblocks: List of decoded macroblocks.
        :param width: Original frame width.
        :param height: Original frame height.
        :return: Reconstructed frame as a NumPy array.
        """
        blocks_per_row = width // self.block_size
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        for idx, mb in enumerate(macroblocks):
            row = idx // blocks_per_row
            col = idx % blocks_per_row
            y = row * self.block_size
            x = col * self.block_size
            frame[y:y+self.block_size, x:x+self.block_size] = mb

        return frame
