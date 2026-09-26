# Compression Tool (Huffman Algorithm)

A file compression and decompression tool built using the **Huffman Coding algorithm** — a greedy, lossless data compression technique based on character frequency.

## How It Works
- Builds a frequency table of characters in the input file.
- Constructs a Huffman Tree based on those frequencies.
- Assigns shorter binary codes to more frequent characters and longer codes to rarer ones.
- Encodes the file using these variable-length codes to reduce overall size.
- Supports decompression by rebuilding the tree and decoding the binary back to the original data.

## Concepts Covered
- Binary trees
- Priority queues / min-heaps
- Bit manipulation
- Lossless data compression

## Getting Started

```bash
git clone https://github.com/INAYAT-ULLAH67/Compression-Toll.git
cd Compression-Toll
python huffman.py <input_file>
```

## Purpose
Built as a practical exercise in understanding compression algorithms and how real-world tools like ZIP achieve size reduction.
