import os
import json
from datetime import datetime
from storage_manager import StorageManager

class FileSystem:
    def __init__(self, storage_file='filesystem.json'):
        self.storage_file = storage_file
        self.storage = StorageManager()
        self.load_filesystem()
        
    def load_filesystem(self):
        """Load filesystem metadata"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.root = data['root']
                self.current_dir = data.get('current_dir', '/')
        else:
            self._initialize_filesystem()
            
    def _initialize_filesystem(self):
        """Initialize a new filesystem"""
        self.root = {
            "name": "/",
            "type": "directory",
            "content": {},
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.current_dir = "/"
        self.save_filesystem()
        
    def save_filesystem(self):
        """Save filesystem metadata"""
        data = {
            'root': self.root,
            'current_dir': self.current_dir
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def get_node_at_path(self, path=None):
        """Get node at specified path (default to current directory)"""
        if path is None:
            path = self.current_dir
            
        # Normalize path with forward slashes
        path = path.replace("\\", "/")
            
        if path == "/":
            return self.root
            
        parts = path.split('/')[1:]  # Remove empty first element
        current = self.root
        
        for part in parts:
            if not part:  # Skip empty parts (happens with '//' in path)
                continue
                
            if part not in current["content"]:
                return None
            current = current["content"][part]
            
        return current
        
    def create_directory(self, dir_name, parent_path=None):
        """Create a new directory"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent:
            return False, "Parent directory not found"
            
        if dir_name in parent["content"]:
            return False, "Directory already exists"
            
        parent["content"][dir_name] = {
            "name": dir_name,
            "type": "directory",
            "content": {},
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "Directory created"
        
    def create_file(self, file_name, size=1024, parent_path=None):
        """Create a new file with contiguous allocation"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent:
            return False, "Parent directory not found"
            
        if file_name in parent["content"]:
            return False, "File already exists"
        
        # Construct the file path with forward slashes
        if parent_path:
            parent_path = parent_path.replace("\\", "/")
            file_path = parent_path
            if not file_path.endswith("/"):
                file_path += "/"
            file_path += file_name
        else:
            file_path = self.current_dir
            if not file_path.endswith("/"):
                file_path += "/"
            file_path += file_name
            
        # Allocate storage space
        allocation = self.storage.allocate_file(file_path, size)
        if not allocation:
            return False, "Not enough contiguous space"
            
        parent["content"][file_name] = {
            "name": file_name,
            "type": "file",
            "size": size,
            "content": f"Content of {file_name}",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "allocation": allocation
        }
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "File created"
        
    def delete_file(self, file_name, parent_path=None):
        """Delete a file and deallocate its space"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or file_name not in parent["content"]:
            return False, "File not found"
            
        if parent["content"][file_name]["type"] != "file":
            return False, "Not a file"
        
        # Construct the file path with forward slashes
        if parent_path:
            parent_path = parent_path.replace("\\", "/")
            file_path = parent_path
            if not file_path.endswith("/"):
                file_path += "/"
            file_path += file_name
        else:
            file_path = self.current_dir
            if not file_path.endswith("/"):
                file_path += "/"
            file_path += file_name
            
        self.storage.deallocate_file(file_path)
        del parent["content"][file_name]
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "File deleted"
        
    def show_allocation_info(self, file_name, parent_path=None):
        """Show allocation information for a file"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or file_name not in parent["content"]:
            return None
            
        file_node = parent["content"][file_name]
        if file_node["type"] != "file":
            return None
            
        allocation = file_node.get("allocation")
        if not allocation:
            return None
            
        start_block, num_blocks = allocation
        block_size = self.storage.block_size
        return {
            'file_name': file_name,
            'start_block': start_block,
            'num_blocks': num_blocks,
            'start_byte': start_block * block_size,
            'end_byte': (start_block + num_blocks) * block_size - 1,
            'size_bytes': file_node["size"],
            'block_size': block_size
        }
        
    def change_directory(self, path):
        """Change current directory"""
        # Normalize path with forward slashes
        path = path.replace("\\", "/")
        
        if path.startswith("/"):
            new_path = path
        else:
            # Join path with forward slashes
            if self.current_dir.endswith("/"):
                new_path = self.current_dir + path
            else:
                new_path = self.current_dir + "/" + path
                
        # Clean path from double slashes
        while "//" in new_path:
            new_path = new_path.replace("//", "/")
            
        if self.get_node_at_path(new_path):
            self.current_dir = new_path
            self.save_filesystem()
            return True, f"Changed directory to {new_path}"
        return False, "Directory not found"
        
    def get_directory_contents(self, path=None):
        """Get contents of a directory"""
        if path:
            # Normalize path with forward slashes
            path = path.replace("\\", "/")
            
        node = self.get_node_at_path(path) if path else self.get_node_at_path()
        if not node or node["type"] != "directory":
            return None
            
        return node["content"]
        
    def get_file_content(self, file_name, parent_path=None):
        """Get content of a file"""
        if parent_path:
            # Normalize path with forward slashes
            parent_path = parent_path.replace("\\", "/")
            
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or file_name not in parent["content"]:
            return None
            
        item = parent["content"][file_name]
        if item["type"] != "file":
            return None
            
        return item["content"]
        
    def rename_item(self, old_name, new_name, parent_path=None):
        """Rename a file or directory"""
        if not self.is_valid_name(new_name):
            return False, "Invalid name"
        
        if parent_path:
            # Normalize path with forward slashes
            parent_path = parent_path.replace("\\", "/")
            
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or old_name not in parent["content"]:
            return False, "Item not found"
            
        if new_name in parent["content"]:
            return False, "Name already exists"
            
        # Move the item to new name
        parent["content"][new_name] = parent["content"][old_name]
        parent["content"][new_name]["name"] = new_name
        parent["content"][new_name]["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update storage allocation if it's a file
        if parent["content"][new_name]["type"] == "file":
            # Construct paths with forward slashes
            if parent_path:
                parent_path_norm = parent_path.replace("\\", "/")
                old_path = parent_path_norm + ("/" if not parent_path_norm.endswith("/") else "") + old_name
                new_path = parent_path_norm + ("/" if not parent_path_norm.endswith("/") else "") + new_name
            else:
                current_dir_norm = self.current_dir.replace("\\", "/")
                old_path = current_dir_norm + ("/" if not current_dir_norm.endswith("/") else "") + old_name
                new_path = current_dir_norm + ("/" if not current_dir_norm.endswith("/") else "") + new_name
                
            if old_path in self.storage.file_allocation_table:
                allocation = self.storage.file_allocation_table.pop(old_path)
                self.storage.file_allocation_table[new_path] = allocation
        
        del parent["content"][old_name]
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "Item renamed"
        
    def is_valid_name(self, name):
        """Check if name is valid for files/directories"""
        if not name:
            return False
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return all(char not in name for char in invalid_chars)
        
    def format_size(self, size):
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
        
    def get_disk_info(self):
        """Get disk usage information"""
        return self.storage.get_disk_usage()
        
    def delete_directory(self, dir_name, parent_path=None):
        """Delete a directory and all its contents recursively"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or dir_name not in parent["content"]:
            return False, "Directory not found"
            
        if parent["content"][dir_name]["type"] != "directory":
            return False, "Not a directory"
            
        # Get the full path to the directory
        if parent_path:
            parent_path = parent_path.replace("\\", "/")
            dir_path = parent_path
            if not dir_path.endswith("/"):
                dir_path += "/"
            dir_path += dir_name
        else:
            dir_path = self.current_dir
            if not dir_path.endswith("/"):
                dir_path += "/"
            dir_path += dir_name
        
        # Recursively delete all files in the directory
        self._delete_directory_contents(parent["content"][dir_name], dir_path)
        
        # Delete the directory itself
        del parent["content"][dir_name]
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "Directory deleted"
        
    def _delete_directory_contents(self, dir_node, dir_path):
        """Recursively delete all contents of a directory"""
        for name, item in list(dir_node["content"].items()):
            item_path = dir_path + "/" + name
            # Clean path from double slashes
            while "//" in item_path:
                item_path = item_path.replace("//", "/")
                
            if item["type"] == "file":
                # Deallocate file storage
                self.storage.deallocate_file(item_path)
            elif item["type"] == "directory":
                # Recursively delete subdirectory contents
                self._delete_directory_contents(item, item_path)