import os
import sqlite3
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Configuration for saving conversations locally and in database
class Config:
    LOG_DIR = 'conversations'
    DB_NAME = 'conversations.db'

# Manage conversations locally
class ConversationLogger:
    def __init__(self, log_dir=Config.LOG_DIR):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def save_conversation(self, conversation_id, conversation):
        file_path = os.path.join(self.log_dir, f'{conversation_id}.txt')
        with open(file_path, 'w') as file:
            file.write(conversation)
        logger.info(f"Conversation {conversation_id} saved locally.")
    
    def load_conversation(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                logger.info(f"Conversation loaded from {file_path}.")
                return file.read()
        else:
            logger.warning(f"Conversation file {file_path} not found.")
            return None

# Manage conversations in SQLite database
class ConversationDatabase:
    def __init__(self, db_name=Config.DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
    
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_question TEXT,
            assistant_answer TEXT,
            timestamp TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()
    
    def save_conversation(self, conversation_id, user_question, assistant_answer, timestamp):
        query = "INSERT OR REPLACE INTO conversations (id, user_question, assistant_answer, timestamp) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (conversation_id, user_question, assistant_answer, timestamp))
        self.conn.commit()
        logger.info(f"Conversation {conversation_id} saved to database.")
    
    def load_conversation(self, conversation_id):
        query = "SELECT user_question, assistant_answer FROM conversations WHERE id = ?"
        cursor = self.conn.execute(query, (conversation_id,))
        row = cursor.fetchone()
        if row:
            logger.info(f"Conversation {conversation_id} loaded from database.")
            return row
        else:
            logger.warning(f"Conversation {conversation_id} not found in database.")
            return None

# Summarize conversation function
def summarize_conversation(conversation):
    # Removing unnecessary characters and formatting
    cleaned_conversation = re.sub(r'\n+', '\n', conversation.strip())
    
    # Splitting conversation into individual messages
    messages = cleaned_conversation.split('\n')
    
    summary = []
    for msg in messages:
        # Keeping only essential part of each message
        if 'user:' in msg.lower():
            summary.append("User: " + msg.split(':')[1].strip())
        elif 'assistant:' in msg.lower():
            summary.append("Assistant: " + msg.split(':')[1].strip())
    
    return '\n'.join(summary)

# Main class to integrate both local and database storage
class ConversationManager:
    def __init__(self):
        self.local_logger = ConversationLogger()
        self.db_logger = ConversationDatabase()
    
    def save_conversation(self, conversation_id, user_question, assistant_answer):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conversation = f"User: {user_question}\nChatGPT: {assistant_answer}"
        self.local_logger.save_conversation(conversation_id, conversation)
        self.db_logger.save_conversation(conversation_id, user_question, assistant_answer, timestamp)
    
    def load_conversation(self, conversation_id):
        conversation = self.local_logger.load_conversation(conversation_id)
        if conversation is None:
            conversation = self.db_logger.load_conversation(conversation_id)
            if conversation:
                conversation = f"User: {conversation[0]}\nChatGPT: {conversation[1]}"
        return conversation

    def load_conversation_summary(self, conversation_id):
        conversation = self.load_conversation(conversation_id)
        if conversation:
            return summarize_conversation(conversation)
        else:
            return "Conversation not found."

    def set_log_dir(self, new_log_dir):
        self.local_logger.log_dir = new_log_dir
        if not os.path.exists(new_log_dir):
            os.makedirs(new_log_dir)

# GUI Application
class ConversationApp:
    def __init__(self, root):
        self.manager = ConversationManager()
        
        self.root = root
        self.root.title("Conversation Manager")
        
        self.create_widgets()
    
    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Conversation ID
        ttk.Label(frame, text="Conversation ID:").grid(row=0, column=0, sticky=tk.W)
        self.conversation_id_entry = ttk.Entry(frame, width=30)
        self.conversation_id_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        # User Question
        ttk.Label(frame, text="User Question:").grid(row=1, column=0, sticky=tk.W)
        self.user_question_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=5)
        self.user_question_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Assistant Answer
        ttk.Label(frame, text="Assistant Answer:").grid(row=3, column=0, sticky=tk.W)
        self.assistant_answer_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=5)
        self.assistant_answer_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Save Button
        self.save_button = ttk.Button(frame, text="Save", command=self.save_conversation)
        self.save_button.grid(row=5, column=0, sticky=tk.W)
        
        # Load Button
        self.load_button = ttk.Button(frame, text="Load", command=self.load_conversation)
        self.load_button.grid(row=5, column=1, sticky=tk.W)
        
        # Load Summary Button
        self.load_summary_button = ttk.Button(frame, text="Load Summary", command=self.load_conversation_summary)
        self.load_summary_button.grid(row=5, column=2, sticky=tk.W)
        
        # Set Save Path Button
        self.set_save_path_button = ttk.Button(frame, text="Set Save Path", command=self.set_save_path)
        self.set_save_path_button.grid(row=6, column=0, sticky=tk.W)

        # Browse for Load File Button
        self.browse_load_file_button = ttk.Button(frame, text="Browse Load File", command=self.browse_load_file)
        self.browse_load_file_button.grid(row=6, column=1, sticky=tk.W)
    
    def save_conversation(self):
        conversation_id = self.conversation_id_entry.get()
        user_question = self.user_question_text.get("1.0", tk.END).strip()
        assistant_answer = self.assistant_answer_text.get("1.0", tk.END).strip()
        if conversation_id and user_question and assistant_answer:
            self.manager.save_conversation(conversation_id, user_question, assistant_answer)
            messagebox.showinfo("Success", f"Conversation {conversation_id} saved successfully.")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid conversation ID, question, and answer.")
    
    def load_conversation(self):
        conversation_id = self.conversation_id_entry.get()
        if conversation_id:
            conversation = self.manager.load_conversation(conversation_id)
            if conversation:
                self.user_question_text.delete("1.0", tk.END)
                self.assistant_answer_text.delete("1.0", tk.END)
                self.user_question_text.insert(tk.END, conversation.split('\n')[0].replace("User: ", ""))
                self.assistant_answer_text.insert(tk.END, conversation.split('\n')[1].replace("ChatGPT: ", ""))
            else:
                messagebox.showwarning("Not Found", f"Conversation {conversation_id} not found.")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid conversation ID.")
    
    def load_conversation_summary(self):
        conversation_id = self.conversation_id_entry.get()
        if conversation_id:
            summary = self.manager.load_conversation_summary(conversation_id)
            if summary:
                self.save_summary(conversation_id, summary)
                messagebox.showinfo("Conversation Summary", summary)
            else:
                messagebox.showwarning("Not Found", f"Summary for conversation {conversation_id} not found.")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid conversation ID.")
    
    def save_summary(self, conversation_id, summary):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], initialfile=f"{conversation_id}_summary.txt")
        if file_path:
            with open(file_path, 'w') as file:
                file.write(summary)
            messagebox.showinfo("Success", f"Summary saved to {file_path}.")
    
    def set_save_path(self):
        new_log_dir = filedialog.askdirectory()
        if new_log_dir:
            self.manager.set_log_dir(new_log_dir)
            messagebox.showinfo("Success", f"Save path set to {new_log_dir}.")
    
    def browse_load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            conversation = self.manager.local_logger.load_conversation(file_path)
            if conversation:
                try:
                    self.user_question_text.delete("1.0", tk.END)
                    self.assistant_answer_text.delete("1.0", tk.END)
                    user_question, assistant_answer = conversation.split('\n', 1)
                    self.user_question_text.insert(tk.END, user_question.replace("User: ", ""))
                    self.assistant_answer_text.insert(tk.END, assistant_answer.replace("ChatGPT: ", ""))
                except ValueError:
                    messagebox.showerror("Error", "File content is not in the expected format.")
            else:
                messagebox.showwarning("Not Found", f"Conversation file {file_path} not found.")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = ConversationApp(root)
    root.mainloop()
