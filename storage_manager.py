import json
from datetime import datetime

class StorageManager:
    def __init__(self, storage_file='storage.json', disk_size=1024*1024):  # 1MB default
        self.storage_file = storage_file
        self.disk_size = disk_size
        self.block_size = 512  # Bytes per block
        self.total_blocks = disk_size // self.block_size
        self.bitmap = [0] * self.total_blocks  # 0=free, 1=used
        self.file_allocation_table = {}  # {file_path: (start_block, num_blocks)}
        self.load_storage()
        
    def load_storage(self):
        """Load storage data from file"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.bitmap = data['bitmap']
                self.file_allocation_table = data['file_allocation_table']
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_storage()
            
    def _initialize_storage(self):
        """Initialize a new storage"""
        self.bitmap = [0] * self.total_blocks
        self.file_allocation_table = {}
        self.save_storage()
        
    def save_storage(self):
        """Save storage data to file"""
        data = {
            'bitmap': self.bitmap,
            'file_allocation_table': self.file_allocation_table
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def allocate_blocks(self, num_blocks):
        """
        Allocate contiguous blocks using first-fit strategy
        Returns (start_block, num_blocks) if successful, None otherwise
        """
        start_block = None
        consecutive_free = 0
        
        for i, block in enumerate(self.bitmap):
            if block == 0:
                if start_block is None:
                    start_block = i
                consecutive_free += 1
                if consecutive_free >= num_blocks:
                    # Mark blocks as used
                    for j in range(start_block, start_block + num_blocks):
                        self.bitmap[j] = 1
                    self.save_storage()
                    return (start_block, num_blocks)
            else:
                start_block = None
                consecutive_free = 0
                
        return None  # Not enough contiguous space
        
    def free_blocks(self, start_block, num_blocks):
        """Mark blocks as free"""
        for i in range(start_block, start_block + num_blocks):
            if i < len(self.bitmap):
                self.bitmap[i] = 0
        self.save_storage()
        
    def allocate_file(self, file_path, size):
        """Allocate space for a file"""
        num_blocks = (size + self.block_size - 1) // self.block_size  # Ceiling division
        allocation = self.allocate_blocks(num_blocks)
        
        if allocation:
            self.file_allocation_table[file_path] = allocation
            self.save_storage()
            return allocation
        return None
        
    def deallocate_file(self, file_path):
        """Deallocate space for a file"""
        if file_path in self.file_allocation_table:
            start_block, num_blocks = self.file_allocation_table[file_path]
            self.free_blocks(start_block, num_blocks)
            del self.file_allocation_table[file_path]
            self.save_storage()
            return True
        return False
        
    def get_file_allocation(self, file_path):
        """Get allocation info for a file"""
        return self.file_allocation_table.get(file_path)
        
    def get_disk_usage(self):
        """Calculate disk usage statistics"""
        used_blocks = sum(self.bitmap)
        free_blocks = len(self.bitmap) - used_blocks
        return {
            'total_blocks': len(self.bitmap),
            'used_blocks': used_blocks,
            'free_blocks': free_blocks,
            'block_size': self.block_size,
            'total_bytes': self.disk_size,
            'used_bytes': used_blocks * self.block_size,
            'free_bytes': free_blocks * self.block_size
        }
        
    def calculate_size(self, node):
        """Calculate size of a directory recursively"""
        if node['type'] == 'file':
            return node.get('size', 0)
            
        total = 0
        for name, item in node['content'].items():
            total += self.calculate_size(item)
        return total