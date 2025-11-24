import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import heapq
from collections import Counter, defaultdict
import pickle

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompressor:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}
    
    def build_frequency_dict(self, data):
        return Counter(data)
    
    def build_heap(self, frequency):
        heap = []
        for char, freq in frequency.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(heap, node)
        return heap
    
    def build_tree(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(heap, merged)
        return heap[0] if heap else None
    
    def build_codes(self, node, current_code=""):
        if node is None:
            return
        
        if node.char is not None:
            self.codes[node.char] = current_code
            self.reverse_mapping[current_code] = node.char
            return
        print()
        self.build_codes(node.left, current_code + "0")
        self.build_codes(node.right, current_code + "1")
    
    def get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text
    
    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text
    
    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)
        
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b
    
    def compress(self, input_path, output_path):
        try:
            with open(input_path, 'rb') as file:
                text = file.read()
            
            if len(text) == 0:
                return False, "File is empty"
            # Count how often each piece of data occurs
            frequency = self.build_frequency_dict(text)
            #Build a binary tree, starting with the nodes with the lowest count.
            # The new parent node has the combined count of its child nodes.
            heap = self.build_heap(frequency)
            root = self.build_tree(heap)
            # Create the Huffman code by converting the data, piece-by-piece,
            #  into a binary code using the binary tree.
            self.build_codes(root)
            
            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            b = self.get_byte_array(padded_encoded_text)
            
            # Save compressed data along with the reverse mapping
            compressed_data = {
                'reverse_mapping': self.reverse_mapping,
                'compressed_data': b
            }
            
            with open(output_path, 'wb') as output:
                pickle.dump(compressed_data, output)
            
            return True, "Compression successful"
            
        except Exception as e:
            return False, f"Compression failed: {str(e)}"
    
    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-extra_padding]
        
        return encoded_text
    
    def decode_text(self, encoded_text):
        current_code = ""
        decoded_bytes = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                char = self.reverse_mapping[current_code]
                decoded_bytes.append(char)
                current_code = ""
        
        return decoded_bytes
    
    def decompress(self, input_path, output_path):
        try:
            with open(input_path, 'rb') as file:
                compressed_data = pickle.load(file)
            
            self.reverse_mapping = compressed_data['reverse_mapping']
            bit_string = ""
            
            for byte in compressed_data['compressed_data']:
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
            
            encoded_text = self.remove_padding(bit_string)
            decompressed_bytes = self.decode_text(encoded_text)
            
            with open(output_path, 'wb') as output:
                output.write(decompressed_bytes)
            
            return True, "Decompression successful"
            
        except Exception as e:
            return False, f"Decompression failed: {str(e)}"






class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman File Compression Tool")
        self.root.geometry("600x450")
        
        self.compressor = HuffmanCompressor()
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Huffman File Compression Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Select File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        #tkinter variable to hold string for linking to entry field
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path, width=50)
        file_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Compression options frame
        options_frame = ttk.LabelFrame(main_frame, text="Compression Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.compression_var = tk.StringVar(value="compress")
        ttk.Radiobutton(options_frame, text="Compress File", 
                       variable=self.compression_var, value="compress").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Decompress File", 
                       variable=self.compression_var, value="decompress").grid(row=0, column=1, sticky=tk.W)
        
        # Output location
        ttk.Label(main_frame, text="Output Location:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        output_browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_output)
        output_browse_btn.grid(row=5, column=1, padx=(10, 0), pady=5)
        
        # Process button
        process_btn = ttk.Button(main_frame, text="Process File", command=self.process_file)
        process_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="blue")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_file(self):
        file_types = [
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("Huffman compressed", "*.huff")
        ]
        
        filename = filedialog.askopenfilename(filetypes=file_types) #opens a standard “Open File” dialog box.
        if filename:
            #take this filename and set it to the entry field
            self.file_path.set(filename)
            # Auto-generate output filename
            self.auto_generate_output()
    
    def browse_output(self):
        if self.compression_var.get() == "compress":
            default_ext = ".huff"
            file_types = [("Huffman compressed files", "*.huff")]
        else:
            default_ext = ".txt"
            file_types = [("All files", "*.*")]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=file_types
        )
        if filename:
            self.output_path.set(filename)
    
    def auto_generate_output(self):
        input_file = self.file_path.get()
        if not input_file:
            return
        
        if self.compression_var.get() == "compress":
            output_file = input_file + ".huff"
        else:
            if input_file.endswith('.huff'):
                output_file = input_file[:-5]  # Remove .huff extension
            else:
                output_file = input_file + ".decompressed"
        
        self.output_path.set(output_file)
    
    def process_file(self):
        input_file = self.file_path.get()
        output_file = self.output_path.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        # Start progress bar
        self.progress.start()
        self.status_label.config(text="Processing...", foreground="orange")
        self.root.update()
        
        try:
            if self.compression_var.get() == "compress":
                success, message = self.compressor.compress(input_file, output_file)
            else:
                success, message = self.compressor.decompress(input_file, output_file)
            
            # Stop progress bar
            self.progress.stop()
            
            if success:
                self.status_label.config(text=message, foreground="green")
            else:
                self.status_label.config(text=message, foreground="red")
                messagebox.showerror("Error", message)
                
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()


main()