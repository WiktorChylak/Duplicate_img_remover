import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
from os import path
import sys
from duplicate_image_remover import DuplicateImageRemover

class DuplicateImageRemoverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Duplicate Image Remover")
        self.geometry("400x250")
        
        self.set_icon()
        
        self.label = tk.Label(self, text="Select a directory to remove duplicate images")
        self.label.pack(pady=10)
        
        self.select_button = tk.Button(self, text="Select Directory", command=self.select_directory)
        self.select_button.pack(pady=5)
        
        similarity_frame = tk.Frame(self)
        similarity_frame.pack(pady=5)

        self.similarity_label = tk.Label(similarity_frame, text="Set Similarity Percentage:")
        self.similarity_label.pack(side=tk.LEFT, padx=(0, 5))

        self.similarity_entry = tk.Entry(similarity_frame, width=5)
        self.similarity_entry.pack(side=tk.LEFT)

        self.percent_label = tk.Label(similarity_frame, text="%")
        self.percent_label.pack(side=tk.LEFT, padx=(5, 0))

        self.similarity_entry.insert(0, "95")

        self.set_similarity_button = tk.Button(self, text="Set Similarity", command=self.set_similarity)
        self.set_similarity_button.pack(pady=5)
        
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        
        self.start_button = tk.Button(self, text="Start", command=self.start_removal_thread)
        self.start_button.pack(pady=10)
        
        self.directory = None
        self.remover = None
        self.thread = None
        self.similarity_percentage = 95
        
    def set_icon(self):
        # Locate the icon file and set it
        icon_path = self.resource_path("icon.ico")
        if path.exists(icon_path):
            self.iconbitmap(icon_path)
    
    @staticmethod
    def resource_path(relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)
    
    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.label.config(text=f"Selected Directory: {self.directory}")
            self.remover = DuplicateImageRemover(self.directory)
            
    def set_similarity_percentage(self, similarity=None) -> None:
        if similarity is not None:
            self.similarity_percentage = similarity
        if self.remover:
            self.remover.set_percentage(self.similarity_percentage)
    
    def set_similarity(self):
        try:
            similarity = int(self.similarity_entry.get())
            if 0 <= similarity <= 100:
                self.set_similarity_percentage(similarity)
                messagebox.showinfo("Success", f"Similarity set to {self.similarity_percentage}%")
            else:
                messagebox.showwarning("Invalid Input", "Please enter a value between 0 and 100.")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
    
    def start_removal_thread(self):
        if not self.directory:
            messagebox.showwarning("No Directory Selected", "Please select a directory first.")
            return
        
        self.start_button.config(state=tk.DISABLED, text="Running...")
        self.set_similarity_percentage()
        
        self.thread = threading.Thread(target=self.remove_duplicate_images)
        self.thread.start()
    
    def remove_duplicate_images(self):
        self.remover.remove_duplicate_images(progress_callback=self.update_progress)
        self.start_button.config(state=tk.NORMAL, text="Start")
        messagebox.showinfo("Completed", "Duplicate images removal completed.")
        self.progress["value"] = 0
    
    def update_progress(self, current, total):
        self.progress["maximum"] = total
        self.progress["value"] = current
        self.update_idletasks()

if __name__ == "__main__":
    app = DuplicateImageRemoverApp()
    app.mainloop()
