import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pyperclip

class FolderBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Browser")

        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.heading('#0', text='Folder Structure', anchor='w')

        browse_button = tk.Button(root, text="Browse Folder", command=self.browse_folder)
        browse_button.pack()

        copy_selected_button = tk.Button(root, text="Copy Only This Folder Structure to Clipboard", command=self.copy_selected_folder_structure)
        copy_selected_button.pack()

        copy_full_button = tk.Button(root, text="Copy Full Folder Structure to Clipboard", command=self.copy_full_folder_structure)
        copy_full_button.pack()

        self.path_label = tk.Label(root, text="Selected Path: ")
        self.path_label.pack(fill=tk.X)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.tree.delete(*self.tree.get_children())
            self.insert_node('', folder_selected)
            self.path_label.config(text=f"Selected Path: {folder_selected}")
            self.selected_path = folder_selected

    def insert_node(self, parent, path):
        node = self.tree.insert(parent, 'end', text=os.path.basename(path), open=True, values=[path])
        self.populate_tree(node, path)

    def populate_tree(self, parent, path):
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                if os.path.isdir(abs_path):
                    self.tree.insert(parent, 'end', text=item, values=[abs_path])
                else:
                    self.tree.insert(parent, 'end', text=item, values=[abs_path])
        except PermissionError:
            pass  # Skip folders that cannot be accessed

        self.tree.bind('<<TreeviewOpen>>', self.open_node)

    def open_node(self, event):
        node = self.tree.focus()
        abs_path = self.tree.item(node, 'values')[0]
        if self.tree.get_children(node):
            return
        self.tree.delete(*self.tree.get_children(node))
        self.populate_tree(node, abs_path)

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        selected_path = self.tree.item(selected_item, 'values')[0]
        self.path_label.config(text=f"Selected Path: {selected_path}")
        self.selected_path = selected_path

    def copy_selected_folder_structure(self):
        if hasattr(self, 'selected_path'):
            folder_structure = self.get_selected_folder_structure(self.selected_path)
            pyperclip.copy(folder_structure)
            messagebox.showinfo("Success", "Folder structure copied to clipboard.\n\n" + folder_structure)

    def copy_full_folder_structure(self):
        if hasattr(self, 'selected_path'):
            folder_structure = self.get_full_folder_structure(self.selected_path)
            pyperclip.copy(folder_structure)
            messagebox.showinfo("Success", "Full folder structure copied to clipboard.\n\n" + folder_structure)

    def get_selected_folder_structure(self, path):
        folder_structure = path + "\n"
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                folder_structure += abs_path + "\n"
        except PermissionError:
            pass  # Skip folders that cannot be accessed
        return folder_structure

    def get_full_folder_structure(self, path, prefix=""):
        folder_structure = path + "\n"
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                if os.path.isdir(abs_path):
                    folder_structure += prefix + abs_path + "\n"
                    folder_structure += self.get_full_folder_structure(abs_path, prefix + "    ")
                else:
                    folder_structure += prefix + abs_path + "\n"
        except PermissionError:
            pass  # Skip folders that cannot be accessed
        return folder_structure

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderBrowserApp(root)
    root.mainloop()
