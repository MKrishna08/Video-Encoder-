
from collections import defaultdict
import heapq

class HuffmanCoder:
    #Defining the tree tree structure and the frequency of each char
    class Node:
        def __init__(self, char, freq):
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.freq < other.freq

    @staticmethod
    #This function goes through each byte and calculates the frequency of each byte
    def build_frequency_dict(data):
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        return freq

    @classmethod
    #This function creates a priority queue and adds each byte to the queue
    def build_huffman_tree(cls, freq):

        #We create an initial heap structure with the bytes according to their frequency
        heap = [cls.Node(char, count) for char, count in freq.items()]
        heapq.heapify(heap)

        #We keep combining the left and right nodes to form a new node and create another heap
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = cls.Node(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)
        return heap[0]

    @classmethod
    #This function generates the frequency code for each byte
    def generate_huffman_codes(cls, root):
        codes = {}
        def traverse(node, current_code):
            if not node:
                return
            if node.char is not None:
                codes[node.char] = current_code
                return
            traverse(node.left, current_code + "0")
            traverse(node.right, current_code + "1")
        traverse(root, "")
        return codes

    @classmethod
    #This function compresses the data using the huffman codes
    def compress(cls, data):
        freq = cls.build_frequency_dict(data)
        root = cls.build_huffman_tree(freq)
        codes = cls.generate_huffman_codes(root)
        encoded_data = ''.join(codes[byte] for byte in data)
        return {'encoded_data': encoded_data, 'codes': codes}

    @classmethod
    #This function can be used to decompress data for viewing the video later
    def decompress(cls, encoded_data, codes):
        reverse_codes = {v: k for k, v in codes.items()}
        current_code = ""
        decoded_data = []
        for bit in encoded_data:
            current_code += bit
            if current_code in reverse_codes:
                decoded_data.append(reverse_codes[current_code])
                current_code = ""
        return decoded_data