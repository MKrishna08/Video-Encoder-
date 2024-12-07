# motion_estimator.py

import numpy as np
import cv2

class MotionEstimator:
    def __init__(self, search_range=8, block_size=16):
        """
        Initializes the MotionEstimator.
        
        :param search_range: Range of pixels to search for motion (default is 8).
        :param block_size: Size of the macroblocks (default is 16x16).
        """
        self.search_range = search_range
        self.block_size = block_size

    def estimate_motion(self, reference_frame, target_frame):
        """
        Estimates motion vectors between a reference frame and a target frame.
        
        :param reference_frame: Previous frame (NumPy array).
        :param target_frame: Current frame (NumPy array).
        :return: List of motion vectors for each macroblock.
        """
        motion_vectors = []
        height, width, channels = reference_frame.shape

        for y in range(0, height, self.block_size):
            for x in range(0, width, self.block_size):
                ref_block = reference_frame[y:y+self.block_size, x:x+self.block_size]
                min_ssd = float('inf')
                mv = (0, 0)

                # Define search window
                for dy in range(-self.search_range, self.search_range + 1):
                    for dx in range(-self.search_range, self.search_range + 1):
                        ref_y = min(max(y + dy, 0), height - self.block_size)
                        ref_x = min(max(x + dx, 0), width - self.block_size)
                        search_block = target_frame[ref_y:ref_y+self.block_size, ref_x:ref_x+self.block_size]

                        # Ensure both blocks are of the correct size
                        if ref_block.shape != (self.block_size, self.block_size, channels):
                            print(f"Incomplete reference block at ({y}, {x}) with shape {ref_block.shape}")
                            continue
                        if search_block.shape != (self.block_size, self.block_size, channels):
                            print(f"Incomplete search block at ({ref_y}, {ref_x}) with shape {search_block.shape}")
                            continue

                        ssd = np.sum((ref_block - search_block) ** 2)
                        if ssd < min_ssd:
                            min_ssd = ssd
                            mv = (dx, dy)
                
                motion_vectors.append(mv)
        
        return motion_vectors
