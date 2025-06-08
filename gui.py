import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from tkinter.font import Font
import os
from filesystem import FileSystem

class FileSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File System Simulator with Contiguous Allocation")
        self.root.geometry("1200x600")
        
        self.fs = FileSystem()
        
        self.setup_ui()
        self.refresh_view()
        
    def setup_ui(self):
        # Main PanedWindow for split view
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - File Explorer
        self.left_frame = tk.Frame(self.main_pane)
        self.main_pane.add(self.left_frame)
        
        # Right pane - Terminal and Allocation Info
        self.right_frame = tk.Frame(self.main_pane)
        self.main_pane.add(self.right_frame)
        
        # Setup File Explorer (left pane)
        self.setup_file_explorer()
        
        # Setup Right pane with Terminal and Allocation Info
        self.setup_right_panel()
        
    def setup_right_panel(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Terminal tab
        self.terminal_tab = tk.Frame(self.notebook)
        self.notebook.add(self.terminal_tab, text="Terminal")
        self.setup_terminal()
        
        # Allocation Info tab
        self.allocation_tab = tk.Frame(self.notebook)
        self.notebook.add(self.allocation_tab, text="Allocation Info")
        self.setup_allocation_info()
        
    def setup_allocation_info(self):
        # Allocation visualization
        self.canvas = tk.Canvas(self.allocation_tab, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Disk usage info
        self.disk_info_label = tk.Label(self.allocation_tab, anchor=tk.W)
        self.disk_info_label.pack(fill=tk.X, padx=5)
        
        # File allocation details
        self.allocation_text = scrolledtext.ScrolledText(
            self.allocation_tab,
            wrap=tk.WORD,
            height=10,
            state='disabled'
        )
        self.allocation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        tk.Button(
            self.allocation_tab,
            text="Refresh Allocation View",
            command=self.update_allocation_view
        ).pack(pady=5)
        
    def update_allocation_view(self):
        """Update the allocation visualization"""
        self.canvas.delete("all")
        usage = self.fs.storage.get_disk_usage()
        
        # Display disk usage info
        disk_info = (
            f"Total: {usage['total_blocks']} blocks ({usage['total_bytes']/1024:.1f} KB) | "
            f"Used: {usage['used_blocks']} blocks ({usage['used_bytes']/1024:.1f} KB) | "
            f"Free: {usage['free_blocks']} blocks ({usage['free_bytes']/1024:.1f} KB)"
        )
        self.disk_info_label.config(text=disk_info)
        
        # Draw block visualization
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 10:  # Handle initial small size
            canvas_width = 500
            
        block_width = max(5, canvas_width // usage['total_blocks'])
        
        for i in range(usage['total_blocks']):
            color = "red" if self.fs.storage.bitmap[i] else "green"
            self.canvas.create_rectangle(
                i * block_width, 20,
                (i+1) * block_width, 50,
                fill=color,
                outline="black",
                tags="block"
            )
            
        # Show selected file allocation
        selected = self.tree.selection()
        if selected:
            item_name = self.tree.item(selected[0], "text")
            allocation_info = self.fs.show_allocation_info(item_name)
            
            if allocation_info:
                info_text = (
                    f"File: {allocation_info['file_name']}\n"
                    f"Size: {allocation_info['size_bytes']} bytes\n"
                    f"Blocks: {allocation_info['num_blocks']} "
                    f"(#{allocation_info['start_block']}-#{allocation_info['start_block']+allocation_info['num_blocks']-1})\n"
                    f"Location: bytes {allocation_info['start_byte']}-{allocation_info['end_byte']}"
                )
                
                # Highlight allocated blocks
                for i in range(allocation_info['start_block'], 
                              allocation_info['start_block'] + allocation_info['num_blocks']):
                    self.canvas.create_rectangle(
                        i * block_width, 20,
                        (i+1) * block_width, 50,
                        outline="yellow",
                        width=2,
                        tags="highlight"
                    )
            else:
                info_text = f"No allocation info for {item_name}"
                
            self.allocation_text.config(state='normal')
            self.allocation_text.delete(1.0, tk.END)
            self.allocation_text.insert(tk.END, info_text)
            self.allocation_text.config(state='disabled')
        
        # Bind canvas resize
        self.canvas.bind("<Configure>", lambda e: self.update_allocation_view())
    
    def setup_file_explorer(self):
        # Top frame with path and buttons
        top_frame = tk.Frame(self.left_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(top_frame, text="Path:").pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar(value=self.fs.current_dir)
        self.path_entry = tk.Entry(top_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_entry.bind("<Return>", self.on_path_enter)
        
        tk.Button(top_frame, text="Go", command=self.on_path_enter).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Up", command=self.go_up).pack(side=tk.LEFT)
        
        # Tree view for files and directories
        self.tree_frame = tk.Frame(self.left_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Size", "Modified"))
        self.tree.heading("#0", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Modified", text="Modified")
        
        self.tree.column("#0", width=250)
        self.tree.column("Type", width=100)
        self.tree.column("Size", width=100)
        self.tree.column("Modified", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons = [
            ("New Folder", self.create_directory),
            ("New File", self.create_file),
            ("Delete", self.delete_item),
            ("Rename", self.rename_item),
            ("View", self.view_content),
            ("Properties", self.show_properties),
            ("Disk Info", self.show_disk_info)
        ]
        
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self.left_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)
    
    def on_tree_select(self, event):
        """Update allocation view when tree selection changes"""
        self.update_allocation_view()
    
    def on_path_enter(self, event=None):
        """Handle path entry or Go button"""
        path = self.path_var.get()
        success, message = self.fs.change_directory(path)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
            self.path_var.set(self.fs.current_dir)
    
    def go_up(self):
        """Go to parent directory"""
        if self.fs.current_dir == "/":
            return
            
        parent_dir = os.path.dirname(self.fs.current_dir)
        success, message = self.fs.change_directory(parent_dir)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
    
    def setup_terminal(self):
        # Terminal frame
        terminal_frame = tk.Frame(self.terminal_tab, bd=2, relief=tk.SUNKEN)
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Terminal output
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame, 
            wrap=tk.WORD,
            state='disabled',
            bg='black',
            fg='white',
            insertbackground='white',
            font=Font(family="Consolas", size=10)
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        # Terminal input
        input_frame = tk.Frame(terminal_frame)
        input_frame.pack(fill=tk.X, pady=(5,0))
        
        tk.Label(input_frame, text="$", fg="white", bg="black").pack(side=tk.LEFT)
        
        self.terminal_input = tk.Entry(
            input_frame,
            bg='black',
            fg='white',
            insertbackground='white',
            font=Font(family="Consolas", size=10)
        )
        self.terminal_input.pack(fill=tk.X, expand=True, padx=5)
        self.terminal_input.bind("<Return>", self.execute_command)
        
        # Terminal help label
        help_label = tk.Label(
            terminal_frame, 
            text="Commands: ls, cd, mkdir, touch, rm, cp, mv, cat, df, clear, help",
            anchor=tk.W
        )
        help_label.pack(fill=tk.X)
        
        # Write welcome message
        self.write_to_terminal("File System Terminal\nType 'help' for available commands\n")
        self.write_to_terminal(f"Current directory: {self.fs.current_dir}\n")
    
    def write_to_terminal(self, text, color="white"):
        """Write text to terminal output"""
        self.terminal_output.configure(state='normal')
        self.terminal_output.tag_config(color, foreground=color)
        self.terminal_output.insert(tk.END, text, color)
        self.terminal_output.configure(state='disabled')
        self.terminal_output.see(tk.END)
    
    def execute_command(self, event):
        """Execute terminal command"""
        command = self.terminal_input.get().strip()
        self.terminal_input.delete(0, tk.END)
        
        # Display command in terminal
        self.write_to_terminal(f"$ {command}\n")
        
        if not command:
            return
            
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]
        
        if cmd == "help":
            self.write_to_terminal(
                "Available commands:\n"
                "  ls [path]      - List directory contents\n"
                "  cd [path]      - Change directory\n"
                "  mkdir <dir>    - Create directory\n"
                "  touch <file>   - Create file\n"
                "  rm <path>      - Remove file/directory\n"
                "  cp <src> <dest> - Copy file\n"
                "  mv <src> <dest> - Move file\n"
                "  cat <file>     - Show file content\n"
                "  df             - Show disk usage\n"
                "  clear          - Clear terminal\n"
                "  help           - Show this help\n"
            )
        elif cmd == "clear":
            self.terminal_output.configure(state='normal')
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.configure(state='disabled')        
        elif cmd == "ls":
            # Get path from arguments or use current directory
            path = args[0] if args else self.fs.current_dir
            
            # Normalize the path for consistency
            path = path.replace("\\", "/")
            
            # Handle relative paths properly
            if not path.startswith("/"):
                # If path is relative, join it with current directory
                if self.fs.current_dir.endswith("/"):
                    path = self.fs.current_dir + path
                else:
                    path = self.fs.current_dir + "/" + path
                    
            # Clean path from double slashes
            while "//" in path:
                path = path.replace("//", "/")
                
            contents = self.fs.get_directory_contents(path)
            if contents is None:
                self.write_to_terminal(f"ls: cannot access '{path}': No such file or directory\n", "red")
            else:
                self.write_to_terminal(f"Contents of {path}:\n")
                for name, item in contents.items():
                    self.write_to_terminal(f"{name}/\n" if item['type'] == 'directory' else f"{name}\n")        
        elif cmd == "cd":
            path = args[0] if args else "/"
            
            # Special case for ".." to go up one directory
            if path == "..":
                if self.fs.current_dir == "/":
                    # Already at root, do nothing
                    self.write_to_terminal("Already at root directory\n")
                    return
                # Get parent directory by removing the last segment
                path_parts = self.fs.current_dir.rstrip('/').split('/')
                if len(path_parts) > 1:
                    parent_dir = '/'.join(path_parts[:-1])
                    if not parent_dir:
                        parent_dir = "/"
                else:
                    parent_dir = "/"
                success, message = self.fs.change_directory(parent_dir)
            else:
                success, message = self.fs.change_directory(path)
                
            if success:
                self.write_to_terminal(f"Changed directory to {self.fs.current_dir}\n")
                self.refresh_view()
            else:
                self.write_to_terminal(f"cd: {message}\n", "red")
        elif cmd == "mkdir":
            if not args:
                self.write_to_terminal("mkdir: missing operand\n", "red")
            else:
                success, message = self.fs.create_directory(args[0])
                if success:
                    self.write_to_terminal(f"Directory '{args[0]}' created\n")
                    self.refresh_view()
                else:
                    self.write_to_terminal(f"mkdir: {message}\n", "red")
        elif cmd == "touch":
            if not args:
                self.write_to_terminal("touch: missing operand\n", "red")
            else:
                size = 1024  # Default size
                if len(args) > 1 and args[1].isdigit():
                    size = int(args[1])
                success, message = self.fs.create_file(args[0], size)
                if success:
                    self.write_to_terminal(f"File '{args[0]}' created ({size} bytes)\n")
                    self.refresh_view()
                else:
                    self.write_to_terminal(f"touch: {message}\n", "red")
        elif cmd == "rm":
            if not args:
                self.write_to_terminal("rm: missing operand\n", "red")
            else:
                success, message = self.fs.delete_file(args[0])
                if success:
                    self.write_to_terminal(f"Removed '{args[0]}'\n")
                    self.refresh_view()
                else:
                    self.write_to_terminal(f"rm: {message}\n", "red")
        elif cmd == "cp":
            if len(args) < 2:
                self.write_to_terminal("cp: missing file operand\n", "red")
            else:
                # Implement copy logic here
                self.write_to_terminal(f"Copying '{args[0]}' to '{args[1]}'\n")
                # Placeholder - actual implementation would use fs.copy_file()
        elif cmd == "mv":
            if len(args) < 2:
                self.write_to_terminal("mv: missing file operand\n", "red")
            else:
                # Implement move logic here
                self.write_to_terminal(f"Moving '{args[0]}' to '{args[1]}'\n")
                # Placeholder - actual implementation would use fs.move_file()
        elif cmd == "cat":
            if not args:
                self.write_to_terminal("cat: missing file operand\n", "red")
            else:
                content = self.fs.get_file_content(args[0])
                if content is None:
                    self.write_to_terminal(f"cat: {args[0]}: No such file or directory\n", "red")
                else:
                    self.write_to_terminal(f"{content}\n")
        elif cmd == "df":
            disk_info = self.fs.get_disk_info()
            usage = (disk_info['used_bytes'] / disk_info['total_bytes']) * 100 if disk_info['total_bytes'] > 0 else 0
            self.write_to_terminal(
                f"Filesystem      Size  Used  Avail Use%\n"
                f"VirtualDisk   {self.fs.format_size(disk_info['total_bytes'])} "
                f"{self.fs.format_size(disk_info['used_bytes'])} "
                f"{self.fs.format_size(disk_info['free_bytes'])} "
                f"{int(usage)}%\n"
            )
        else:
            self.write_to_terminal(f"{cmd}: command not found\n", "red")
    
    def refresh_view(self):
        """Refresh the tree view with current directory contents"""
        self.tree.delete(*self.tree.get_children())
        self.path_var.set(self.fs.current_dir)
        
        contents = self.fs.get_directory_contents()
        if contents is None:
            messagebox.showerror("Error", "Invalid directory")
            return
            
        for name, item in contents.items():
            size = self.fs.format_size(item.get('size', 0)) if item['type'] == 'file' else ''
            self.tree.insert("", "end", text=name, 
                            values=(item['type'], size, item['modified']))
        
        disk_info = self.fs.get_disk_info()
        self.status_var.set(
            f"Current directory: {self.fs.current_dir} | "
            f"Used space: {self.fs.format_size(disk_info['used_bytes'])}/"
            f"{self.fs.format_size(disk_info['total_bytes'])}"
        )
        self.update_allocation_view()
    
    def on_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        item_name = self.tree.item(item, "text")
        item_type = self.tree.item(item, "values")[0]
        
        if item_type == 'directory':
            new_path = os.path.join(self.fs.current_dir, item_name)
            success, message = self.fs.change_directory(new_path)
            if success:
                self.refresh_view()
            else:
                messagebox.showerror("Error", message)
    
    def create_directory(self):
        """Create a new directory"""
        dir_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if not dir_name:
            return
            
        success, message = self.fs.create_directory(dir_name)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
            
    def create_file(self):
        """Create a new file"""
        file_name = simpledialog.askstring("New File", "Enter file name:")
        if not file_name:
            return
            
        file_size = simpledialog.askinteger("New File", "Enter file size (bytes):", minvalue=1)
        if not file_size:
            return
            
        success, message = self.fs.create_file(file_name, file_size)
        if success:            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
            
    def delete_item(self):
        """Delete selected item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
            
        item_name = self.tree.item(selected[0], "text")
        item_type = self.tree.item(selected[0], "values")[0]
        
        # Check if trying to delete a directory that's currently open
        if item_type == 'directory':
            # Build full path to selected directory
            full_path = self.fs.current_dir
            if not full_path.endswith("/"):
                full_path += "/"
            full_path += item_name
            
            # Normalize paths for comparison
            norm_full_path = full_path.replace("\\", "/")
            norm_current_dir = self.fs.current_dir.replace("\\", "/")
            
            # Check if user is in the directory they're trying to delete
            if norm_current_dir.startswith(norm_full_path):
                messagebox.showerror("Error", "Cannot delete the directory you are currently in. Please navigate to a different directory first.")
                return
                
            confirm = messagebox.askyesno("Confirm", f"Delete directory '{item_name}' and all its contents?")
        else:
            confirm = messagebox.askyesno("Confirm", f"Delete file '{item_name}'?")
            
        if confirm:
            if item_type == 'directory':
                success, message = self.fs.delete_directory(item_name)
            else:
                success, message = self.fs.delete_file(item_name)
                
            if success:
                self.refresh_view()
            else:
                messagebox.showerror("Error", message)
                
    def rename_item(self):
        """Rename selected item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
            
        old_name = self.tree.item(selected[0], "text")
        new_name = simpledialog.askstring("Rename", f"Rename '{old_name}' to:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
            
        success, message = self.fs.rename_item(old_name, new_name)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
            
    def view_content(self):
        """View content of selected file"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file")
            return
            
        item_name = self.tree.item(selected[0], "text")
        item_type = self.tree.item(selected[0], "values")[0]
        
        if item_type != 'file':
            messagebox.showwarning("Warning", "Can only view content of files")
            return
            
        content = self.fs.get_file_content(item_name)
        if content is None:
            messagebox.showerror("Error", "Could not read file content")
            return
            
        # Create content viewer window
        viewer = tk.Toplevel(self.root)
        viewer.title(f"Content of {item_name}")
        
        text_frame = tk.Frame(viewer)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text = tk.Text(text_frame, wrap=tk.WORD)
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(text_frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        
    def show_properties(self):
        """Show properties of selected item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
            
        item_name = self.tree.item(selected[0], "text")
        item_type = self.tree.item(selected[0], "values")[0]
        
        node = self.fs.get_node_at_path(os.path.join(self.fs.current_dir, item_name))
        if not node:
            messagebox.showerror("Error", "Item not found")
            return
            
        size = node.get('size', 0)
        if item_type == 'directory':
            size = self.fs.storage.calculate_size(node)
            
        message = (
            f"Name: {item_name}\n"
            f"Type: {'Directory' if item_type == 'directory' else 'File'}\n"
            f"Size: {self.fs.format_size(size)}\n"
            f"Created: {node['created']}\n"
            f"Modified: {node['modified']}"
        )
        messagebox.showinfo("Properties", message)
        
    def show_disk_info(self):
        """Show disk usage information"""
        disk_info = self.fs.storage.get_disk_usage()
        usage = (disk_info['used_bytes'] / disk_info['total_bytes']) * 100 if disk_info['total_bytes'] > 0 else 0
        
        message = (
            f"Total space: {self.fs.format_size(disk_info['total_bytes'])}\n"
            f"Used space: {self.fs.format_size(disk_info['used_bytes'])} ({usage:.1f}%)\n"
            f"Free space: {self.fs.format_size(disk_info['free_bytes'])}"
        )
        messagebox.showinfo("Disk Information", message)
        
    def on_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        item_name = self.tree.item(item, "text")
        item_type = self.tree.item(item, "values")[0]
        
        if item_type == 'directory':
            new_path = os.path.join(self.fs.current_dir, item_name)
            success, message = self.fs.change_directory(new_path)
            if success:
                self.refresh_view()
            else:
                messagebox.showerror("Error", message)
                
    def on_path_enter(self, event=None):
        """Handle path entry or Go button"""
        path = self.path_var.get()
        success, message = self.fs.change_directory(path)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)
            self.path_var.set(self.fs.current_dir)
            
    def go_up(self):
        """Go to parent directory"""
        if self.fs.current_dir == "/":
            return
            
        parent_dir = os.path.dirname(self.fs.current_dir)
        success, message = self.fs.change_directory(parent_dir)
        if success:
            self.refresh_view()
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemGUI(root)
    root.mainloop()