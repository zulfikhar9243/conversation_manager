import tkinter as tk
from tkinter import ttk
from ConversationManagerGU import ConversationApp
from gui_folder_browser_final import FolderBrowserApp

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Combined Application")
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        
        # Create frames for each app
        self.conversation_frame = ttk.Frame(self.notebook)
        self.folder_browser_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.conversation_frame, text='Conversation Manager')
        self.notebook.add(self.folder_browser_frame, text='Folder Browser')
        
        # Initialize each app in their respective frames
        self.init_conversation_manager(self.conversation_frame)
        self.init_folder_browser(self.folder_browser_frame)
    
    def init_conversation_manager(self, parent):
        # Initialize ConversationApp in the given frame
        self.conversation_app = ConversationApp(parent)
    
    def init_folder_browser(self, parent):
        # Initialize FolderBrowserApp in the given frame
        self.folder_browser_app = FolderBrowserApp(parent)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
