import tkinter as tk
from tkinter import ttk
from ConversationManagerGU import ConversationApp
from gui_folder_browser_final import FolderBrowserApp

def run_conversation_manager():
    root = tk.Tk()
    app = ConversationApp(root)
    root.mainloop()

def run_folder_browser():
    root = tk.Tk()
    app = FolderBrowserApp(root)
    root.mainloop()

def create_main_window():
    root = tk.Tk()
    root.title("Select Application")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Select the application to run:").grid(row=0, column=0, columnspan=2, pady=(0, 10))

    run_conversation_manager_button = ttk.Button(frame, text="Run Conversation Manager", command=run_conversation_manager)
    run_conversation_manager_button.grid(row=1, column=0, padx=(0, 5))

    run_folder_browser_button = ttk.Button(frame, text="Run Folder Browser", command=run_folder_browser)
    run_folder_browser_button.grid(row=1, column=1, padx=(5, 0))

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
