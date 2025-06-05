from gui import FileSystemGUI
import tkinter as tk
import os 

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemGUI(root)
    root.mainloop()