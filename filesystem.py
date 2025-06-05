import os
import json
from datetime import datetime

class FileSystem:
    def __init__(self, storage_file='filesystem.json'):
        self.storage_file = storage_file
        self.disk_size = 1024 * 1024  # 1MB
        self.load_filesystem()
        
    def load_filesystem(self):
        """Load filesystem from JSON file"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.root = data['root']
                self.used_space = data['used_space']
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
        self.used_space = 0
        self.current_dir = "/"
        self.save_filesystem()
        
    def save_filesystem(self):
        """Save filesystem to JSON file"""
        data = {
            'root': self.root,
            'used_space': self.used_space,
            'current_dir': self.current_dir
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def get_node_at_path(self, path=None):
        """Get node at specified path (default to current directory)"""
        if path is None:
            path = self.current_dir
            
        if path == "/":
            return self.root
            
        parts = path.split('/')[1:]  # Remove empty first element
        current = self.root
        
        for part in parts:
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
        """Create a new file"""
        if self.used_space + size > self.disk_size:
            return False, "Not enough disk space"
            
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent:
            return False, "Parent directory not found"
            
        if file_name in parent["content"]:
            return False, "File already exists"
            
        parent["content"][file_name] = {
            "name": file_name,
            "type": "file",
            "size": size,
            "content": f"Content of {file_name}",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.used_space += size
        self.save_filesystem()
        return True, "File created"
        
    def delete_item(self, item_name, parent_path=None):
        """Delete a file or directory"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or item_name not in parent["content"]:
            return False, "Item not found"
            
        item = parent["content"][item_name]
        
        if item["type"] == "directory":
            # Calculate directory size recursively
            size = self._calculate_size(item)
        else:
            size = item["size"]
            
        del parent["content"][item_name]
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.used_space -= size
        self.save_filesystem()
        return True, "Item deleted"
        
    def rename_item(self, old_name, new_name, parent_path=None):
        """Rename a file or directory"""
        if not self.is_valid_name(new_name):
            return False, "Invalid name"
            
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or old_name not in parent["content"]:
            return False, "Item not found"
            
        if new_name in parent["content"]:
            return False, "Name already exists"
            
        # Move the item to new name
        parent["content"][new_name] = parent["content"][old_name]
        parent["content"][new_name]["name"] = new_name
        parent["content"][new_name]["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        del parent["content"][old_name]
        parent["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_filesystem()
        return True, "Item renamed"
        
    def change_directory(self, path):
        """Change current directory"""
        if path.startswith("/"):
            new_path = path
        else:
            new_path = os.path.join(self.current_dir, path)
            
        if self.get_node_at_path(new_path):
            self.current_dir = new_path
            self.save_filesystem()
            return True, f"Changed directory to {new_path}"
        return False, "Directory not found"
        
    def get_directory_contents(self, path=None):
        """Get contents of a directory"""
        node = self.get_node_at_path(path) if path else self.get_node_at_path()
        if not node or node["type"] != "directory":
            return None
            
        return node["content"]
        
    def get_file_content(self, file_name, parent_path=None):
        """Get content of a file"""
        parent = self.get_node_at_path(parent_path) if parent_path else self.get_node_at_path()
        if not parent or file_name not in parent["content"]:
            return None
            
        item = parent["content"][file_name]
        if item["type"] != "file":
            return None
            
        return item["content"]
        
    def _calculate_size(self, node):
        """Calculate size of a directory recursively"""
        if node["type"] == "file":
            return node["size"]
            
        total = 0
        for name, item in node["content"].items():
            total += self._calculate_size(item)
        return total
        
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
        return {
            'total': self.disk_size,
            'used': self.used_space,
            'free': self.disk_size - self.used_space
        }