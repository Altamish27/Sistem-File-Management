from datetime import datetime

class VirtualFileSystem:
    def __init__(self, disk_size=1024*1024):
        self.current_dir = "/"
        self.root_node = {
            "name": "/",
            "type": "directory",
            "content": {},
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.disk_size = disk_size
        self.used_space = 0

    def get_node_at_path(self, path):
        if path == "/":
            return self.root_node
        parts = path.split('/')[1:]
        current = self.root_node
        for part in parts:
            if part not in current["content"]:
                return None
            current = current["content"][part]
        return current

    def is_valid_name(self, name):
        if not name:
            return False
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return all(char not in name for char in invalid_chars)

    def calculate_size(self, node):
        if node["type"] == "file":
            return node["size"]
        total = 0
        for name, item in node["content"].items():
            total += self.calculate_size(item)
        return total

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
