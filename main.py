import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class FileSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File System Simulator")
        self.root.geometry("800x600")
        
        # Inisialisasi filesystem
        self.current_dir = "/"
        self.root_node = {
            "name": "/",
            "type": "directory",
            "content": {},
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.disk_size = 1024 * 1024  # 1MB virtual disk
        self.used_space = 0
        
        # Frame untuk path dan tombol
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.path_label = tk.Label(self.top_frame, text="Current Path:")
        self.path_label.pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar(value="/")
        self.path_entry = tk.Entry(self.top_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.refresh_btn = tk.Button(self.top_frame, text="Refresh", command=self.refresh_view)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame utama untuk layout kiri-kanan
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame untuk tree view (kiri)
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Size", "Created", "Modified"))
        self.tree.heading("#0", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Created", text="Created")
        self.tree.heading("Modified", text="Modified")
        self.tree.column("#0", width=200)
        self.tree.column("Type", width=80)
        self.tree.column("Size", width=80)
        self.tree.column("Created", width=120)
        self.tree.column("Modified", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame untuk terminal (kanan)
        self.terminal_frame = tk.Frame(self.main_frame, width=250)
        self.terminal_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.terminal_label = tk.Label(self.terminal_frame, text="Terminal")
        self.terminal_label.pack(anchor=tk.W)
        self.terminal_text = tk.Text(self.terminal_frame, height=30, width=38, bg="#181818", fg="#00FF00")
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        self.terminal_text.insert(tk.END, "Welcome to Virtual Terminal!\nType 'help' for commands.\n\n")
        self.terminal_text.config(state=tk.DISABLED)
        # Entry dan tombol untuk input perintah
        self.terminal_entry = tk.Entry(self.terminal_frame)
        self.terminal_entry.pack(fill=tk.X, pady=2)
        self.terminal_entry.bind("<Return>", self.run_terminal_command)
        self.terminal_run_btn = tk.Button(self.terminal_frame, text="Run", command=self.run_terminal_command)
        self.terminal_run_btn.pack(fill=tk.X)
        
        # Frame untuk tombol aksi
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_dir_btn = tk.Button(self.button_frame, text="Create Directory", command=self.create_directory)
        self.create_dir_btn.pack(side=tk.LEFT, padx=2)
        
        self.create_file_btn = tk.Button(self.button_frame, text="Create File", command=self.create_file)
        self.create_file_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_btn = tk.Button(self.button_frame, text="Delete", command=self.delete_item)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        self.rename_btn = tk.Button(self.button_frame, text="Rename", command=self.rename_item)
        self.rename_btn.pack(side=tk.LEFT, padx=2)
        
        self.view_btn = tk.Button(self.button_frame, text="View Content", command=self.view_content)
        self.view_btn.pack(side=tk.LEFT, padx=2)
        
        self.disk_info_btn = tk.Button(self.button_frame, text="Disk Info", command=self.show_disk_info)
        self.disk_info_btn.pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)
        
        # Populate initial view
        self.refresh_view()
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.path_entry.bind("<Return>", self.on_path_enter)
        
    def refresh_view(self):
        """Refresh the tree view with current directory contents"""
        self.tree.delete(*self.tree.get_children())
        
        current_node = self.get_node_at_path(self.current_dir)
        if not current_node:
            messagebox.showerror("Error", "Invalid path")
            self.current_dir = "/"
            self.path_var.set("/")
            current_node = self.root_node
        
        for name, item in current_node["content"].items():
            self.tree.insert("", "end", text=name, 
                            values=(item["type"], 
                                   self.format_size(item.get("size", 0)), 
                                   item["created"], 
                                   item["modified"]))
        
        self.status_var.set(f"Current directory: {self.current_dir} | Used space: {self.format_size(self.used_space)}/{self.format_size(self.disk_size)}")
    
    def get_node_at_path(self, path):
        """Get the node at the specified path"""
        if path == "/":
            return self.root_node
            
        parts = path.split('/')[1:]  # Remove empty first element
        current = self.root_node
        
        for part in parts:
            if part not in current["content"]:
                return None
            current = current["content"][part]
            
        return current
    
    def create_directory(self):
        """Create a new directory"""
        dir_name = tk.simpledialog.askstring("Create Directory", "Enter directory name:")
        if not dir_name:
            return
            
        if not self.is_valid_name(dir_name):
            messagebox.showerror("Error", "Invalid directory name")
            return
            
        parent_node = self.get_node_at_path(self.current_dir)
        if not parent_node:
            messagebox.showerror("Error", "Invalid current directory")
            return
            
        if dir_name in parent_node["content"]:
            messagebox.showerror("Error", "Directory already exists")
            return
            
        parent_node["content"][dir_name] = {
            "name": dir_name,
            "type": "directory",
            "content": {},
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.refresh_view()
    
    def create_file(self):
        """Create a new file"""
        file_name = tk.simpledialog.askstring("Create File", "Enter file name:")
        if not file_name:
            return
            
        if not self.is_valid_name(file_name):
            messagebox.showerror("Error", "Invalid file name")
            return
            
        file_size = tk.simpledialog.askinteger("Create File", "Enter file size (bytes):", minvalue=1)
        if not file_size:
            return
            
        if self.used_space + file_size > self.disk_size:
            messagebox.showerror("Error", "Not enough disk space")
            return
            
        parent_node = self.get_node_at_path(self.current_dir)
        if not parent_node:
            messagebox.showerror("Error", "Invalid current directory")
            return
            
        if file_name in parent_node["content"]:
            messagebox.showerror("Error", "File already exists")
            return
            
        parent_node["content"][file_name] = {
            "name": file_name,
            "type": "file",
            "size": file_size,
            "content": f"This is content of file {file_name}",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.used_space += file_size
        self.refresh_view()
    
    def delete_item(self):
        """Delete selected file or directory"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
            
        item_name = self.tree.item(selected[0], "text")
        item_path = os.path.join(self.current_dir, item_name)
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_name}'?")
        if not confirm:
            return
            
        parent_node = self.get_node_at_path(self.current_dir)
        if not parent_node or item_name not in parent_node["content"]:
            messagebox.showerror("Error", "Item not found")
            return
            
        item_node = parent_node["content"][item_name]
        
        if item_node["type"] == "directory":
            # Calculate directory size recursively
            dir_size = self.calculate_size(item_node)
            self.used_space -= dir_size
        else:
            self.used_space -= item_node["size"]
            
        del parent_node["content"][item_name]
        parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.refresh_view()
    
    def rename_item(self):
        """Rename selected file or directory"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to rename")
            return
            
        old_name = self.tree.item(selected[0], "text")
        new_name = tk.simpledialog.askstring("Rename", f"Rename '{old_name}' to:", initialvalue=old_name)
        
        if not new_name or new_name == old_name:
            return
            
        if not self.is_valid_name(new_name):
            messagebox.showerror("Error", "Invalid name")
            return
            
        parent_node = self.get_node_at_path(self.current_dir)
        if not parent_node or old_name not in parent_node["content"]:
            messagebox.showerror("Error", "Item not found")
            return
            
        if new_name in parent_node["content"]:
            messagebox.showerror("Error", "Name already exists")
            return
            
        # Move the item to new name
        parent_node["content"][new_name] = parent_node["content"][old_name]
        parent_node["content"][new_name]["name"] = new_name
        parent_node["content"][new_name]["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        del parent_node["content"][old_name]
        parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.refresh_view()
    
    def view_content(self):
        """View content of selected file"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to view")
            return
            
        item_name = self.tree.item(selected[0], "text")
        item_type = self.tree.item(selected[0], "values")[0]
        
        if item_type != "file":
            messagebox.showwarning("Warning", "Can only view content of files")
            return
            
        parent_node = self.get_node_at_path(self.current_dir)
        if not parent_node or item_name not in parent_node["content"]:
            messagebox.showerror("Error", "File not found")
            return
            
        content = parent_node["content"][item_name]["content"]
        
        # Create a new window to display content
        content_window = tk.Toplevel(self.root)
        content_window.title(f"Content of {item_name}")
        
        text_frame = tk.Frame(content_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def show_disk_info(self):
        """Show disk usage information"""
        total = self.disk_size
        used = self.used_space
        free = total - used
        usage_percent = (used / total) * 100 if total > 0 else 0
        
        message = (
            f"Disk Information:\n\n"
            f"Total space: {self.format_size(total)}\n"
            f"Used space: {self.format_size(used)} ({usage_percent:.1f}%)\n"
            f"Free space: {self.format_size(free)}"
        )
        messagebox.showinfo("Disk Information", message)
    
    def on_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        item_name = self.tree.item(item, "text")
        item_type = self.tree.item(item, "values")[0]
        
        if item_type == "directory":
            new_path = os.path.join(self.current_dir, item_name)
            self.current_dir = new_path
            self.path_var.set(new_path)
            self.refresh_view()
    
    def on_path_enter(self, event):
        """Handle Enter key in path entry"""
        new_path = self.path_var.get()
        if not new_path.startswith("/"):
            new_path = "/" + new_path
            
        if self.get_node_at_path(new_path):
            self.current_dir = new_path
            self.refresh_view()
        else:
            messagebox.showerror("Error", "Invalid path")
            self.path_var.set(self.current_dir)
    
    def calculate_size(self, node):
        """Calculate size of a directory recursively"""
        if node["type"] == "file":
            return node["size"]
            
        total = 0
        for name, item in node["content"].items():
            total += self.calculate_size(item)
        return total
    
    def format_size(self, size):
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def is_valid_name(self, name):
        """Check if name is valid for files/directories"""
        if not name:
            return False
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return all(char not in name for char in invalid_chars)
    
    def run_terminal_command(self, event=None):
        cmd = self.terminal_entry.get().strip()
        if not cmd:
            return
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.insert(tk.END, f"$ {cmd}\n")
        output = self.handle_terminal_command(cmd)
        if output:
            self.terminal_text.insert(tk.END, output + "\n")
        self.terminal_text.see(tk.END)
        self.terminal_text.config(state=tk.DISABLED)
        self.terminal_entry.delete(0, tk.END)

    def handle_terminal_command(self, cmd):
        # Simple command parser for virtual FS
        parts = cmd.split()
        if not parts:
            return ""
        c = parts[0]
        if c == "ls":
            node = self.get_node_at_path(self.current_dir)
            if not node:
                return "Invalid path"
            names = list(node["content"].keys())
            return "  ".join(names) if names else "(empty)"
        elif c == "pwd":
            return self.current_dir
        elif c == "cd":
            if len(parts) < 2:
                return "Usage: cd <dir>"
            target = parts[1]
            if target == "/":
                new_path = "/"
            elif target == "..":
                if self.current_dir == "/":
                    new_path = "/"
                else:
                    new_path = "/".join(self.current_dir.rstrip("/").split("/")[:-1])
                    if not new_path:
                        new_path = "/"
            else:
                if self.current_dir == "/":
                    new_path = f"/{target}"
                else:
                    new_path = f"{self.current_dir}/{target}"
            if self.get_node_at_path(new_path):
                self.current_dir = new_path
                self.path_var.set(new_path)
                self.refresh_view()
                return ""
            else:
                return f"Directory not found: {target}"
        elif c == "help":
            return "Commands: ls, cd <dir>, pwd, mkdir <dir>, rm <name>, cat <file>, touch <file>, help"
        elif c == "mkdir":
            if len(parts) < 2:
                return "Usage: mkdir <dir>"
            dir_name = parts[1]
            if not self.is_valid_name(dir_name):
                return "Invalid directory name"
            parent_node = self.get_node_at_path(self.current_dir)
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
            self.refresh_view()
            return ""
        elif c == "rm":
            if len(parts) < 2:
                return "Usage: rm <name>"
            name = parts[1]
            parent_node = self.get_node_at_path(self.current_dir)
            if not parent_node or name not in parent_node["content"]:
                return "Item not found"
            item_node = parent_node["content"][name]
            if item_node["type"] == "directory":
                dir_size = self.calculate_size(item_node)
                self.used_space -= dir_size
            else:
                self.used_space -= item_node["size"]
            del parent_node["content"][name]
            parent_node["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.refresh_view()
            return ""
        elif c == "cat":
            if len(parts) < 2:
                return "Usage: cat <file>"
            name = parts[1]
            parent_node = self.get_node_at_path(self.current_dir)
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
            if not self.is_valid_name(file_name):
                return "Invalid file name"
            parent_node = self.get_node_at_path(self.current_dir)
            if not parent_node:
                return "Invalid current directory"
            if file_name in parent_node["content"]:
                return "File already exists"
            # Default file size 1 byte
            if self.used_space + 1 > self.disk_size:
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
            self.used_space += 1
            self.refresh_view()
            return ""
        else:
            return f"Unknown command: {c}"

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemGUI(root)
    root.mainloop()