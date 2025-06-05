from datetime import datetime

class TerminalHandler:
    def __init__(self, vfs, gui_callback=None):
        self.vfs = vfs
        self.gui_callback = gui_callback  # Optional: callback to refresh GUI

    def handle_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return ""
        c = parts[0]
        if c == "ls":
            node = self.vfs.get_node_at_path(self.vfs.current_dir)
            if not node:
                return "Invalid path"
            names = list(node["content"].keys())
            return "  ".join(names) if names else "(empty)"
        elif c == "pwd":
            return self.vfs.current_dir
        elif c == "cd":
            if len(parts) < 2:
                return "Usage: cd <dir>"
            target = parts[1]
            if target == "/":
                new_path = "/"
            elif target == "..":
                if self.vfs.current_dir == "/":
                    new_path = "/"
                else:
                    new_path = "/".join(self.vfs.current_dir.rstrip("/").split("/")[:-1])
                    if not new_path:
                        new_path = "/"
            else:
                if self.vfs.current_dir == "/":
                    new_path = f"/{target}"
                else:
                    new_path = f"{self.vfs.current_dir}/{target}"
            if self.vfs.get_node_at_path(new_path):
                self.vfs.current_dir = new_path
                if self.gui_callback:
                    self.gui_callback(new_path)
                return ""
            else:
                return f"Directory not found: {target}"
        elif c == "help":
            return "Commands: ls, cd <dir>, pwd, mkdir <dir>, rm <name>, cat <file>, touch <file>, help"
        elif c == "mkdir":
            if len(parts) < 2:
                return "Usage: mkdir <dir>"
            dir_name = parts[1]
            if not self.vfs.is_valid_name(dir_name):
                return "Invalid directory name"
            parent_node = self.vfs.get_node_at_path(self.vfs.current_dir)
            if not parent_node:
                return "Invalid current directory"
            if dir_name in parent_node["content"]:
                return "Directory already exists"
            parent_node["content"][dir_name] = {
                "name": dir_name,
                "type": "directory",
                "content": {},
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.gui_callback:
                self.gui_callback()
            return ""
        elif c == "rm":
            if len(parts) < 2:
                return "Usage: rm <name>"
            name = parts[1]
            parent_node = self.vfs.get_node_at_path(self.vfs.current_dir)
            if not parent_node or name not in parent_node["content"]:
                return "Item not found"
            item_node = parent_node["content"][name]
            if item_node["type"] == "directory":
                dir_size = self.vfs.calculate_size(item_node)
                self.vfs.used_space -= dir_size
            else:
                self.vfs.used_space -= item_node["size"]
            del parent_node["content"][name]
            parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.gui_callback:
                self.gui_callback()
            return ""
        elif c == "cat":
            if len(parts) < 2:
                return "Usage: cat <file>"
            name = parts[1]
            parent_node = self.vfs.get_node_at_path(self.vfs.current_dir)
            if not parent_node or name not in parent_node["content"]:
                return "File not found"
            item_node = parent_node["content"][name]
            if item_node["type"] != "file":
                return f"{name} is not a file"
            return item_node["content"]
        elif c == "touch":
            if len(parts) < 2:
                return "Usage: touch <file>"
            file_name = parts[1]
            if not self.vfs.is_valid_name(file_name):
                return "Invalid file name"
            parent_node = self.vfs.get_node_at_path(self.vfs.current_dir)
            if not parent_node:
                return "Invalid current directory"
            if file_name in parent_node["content"]:
                return "File already exists"
            if self.vfs.used_space + 1 > self.vfs.disk_size:
                return "Not enough disk space"
            parent_node["content"][file_name] = {
                "name": file_name,
                "type": "file",
                "size": 1,
                "content": f"This is content of file {file_name}",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.vfs.used_space += 1
            if self.gui_callback:
                self.gui_callback()
            return ""
        else:
            return f"Unknown command: {c}"
