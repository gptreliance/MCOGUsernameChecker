import requests
import time
from tqdm import tqdm
from collections import deque
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Constants
API_URL = "https://api.mojang.com/users/profiles/minecraft/"

# Helper functions
def read_words_from_file(file_path):
    """Reads a list of words from a file and filters out invalid ones."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if is_valid_word(line.strip())]

def is_valid_word(word):
    """Checks if the word only contains alphabets, numbers, or underscores."""
    return bool(re.match(r'^[a-zA-Z0-9_]+$', word))

def check_username(username):
    """Checks if a username is available using the Mojang API."""
    start_time = time.time()
    retry_time = 1  # Initial backoff time in seconds
    
    while retry_time <= 8:
        try:
            response = requests.get(API_URL + username)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                return None, elapsed_time  # Username is taken
            elif response.status_code == 404:
                return username, elapsed_time  # Username is available
            elif response.status_code == 429:
                # Print retry message in the same line
                print(f"Rate limited. Retrying in {retry_time}s...", end="\r", flush=True)
                time.sleep(retry_time)
                retry_time = min(retry_time * 2, 8)
            else:
                print(f"\nUnexpected response for {username}: {response.text}")
                break
        except requests.exceptions.RequestException as e:
            # Print error message in the same line
            print(f"Error checking {username}: {e}. Retrying in {retry_time}s...", end="\r", flush=True)
            time.sleep(retry_time)
            retry_time = min(retry_time * 2, 8)
    
    # Clear the retry message after the loop ends
    print(" " * 50, end="\r", flush=True)  # Clear the line
    return None, elapsed_time

# GUI Application
class UsernameCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Username Checker")
        self.root.geometry("600x400")
        
        # Variables
        self.usernames = []
        self.available_usernames = []
        
        # GUI Elements
        self.label = tk.Label(root, text="Minecraft Username Checker", font=("Arial", 16))
        self.label.pack(pady=10)
        
        self.load_usernames_button = tk.Button(root, text="Load Usernames", command=self.load_usernames)
        self.load_usernames_button.pack(pady=5)
        
        self.start_button = tk.Button(root, text="Start Checking", command=self.start_checking)
        self.start_button.pack(pady=5)
        
        self.progress_label = tk.Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=5)
        
        self.results_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        self.results_text.pack(pady=10)
        
    def load_usernames(self):
        """Loads usernames from a file."""
        file_path = filedialog.askopenfilename(title="Select Usernames File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.usernames = read_words_from_file(file_path)
            messagebox.showinfo("Usernames Loaded", f"Loaded {len(self.usernames)} usernames.")
    
    def start_checking(self):
        """Starts the username checking process."""
        if not self.usernames:
            messagebox.showwarning("No Usernames", "Please load usernames first.")
            return
        
        self.available_usernames = []
        self.results_text.delete(1.0, tk.END)  # Clear previous results
        
        def update_progress(checked_count, available_count):
            """Updates the progress label and results text."""
            progress = (checked_count / len(self.usernames)) * 100
            self.progress_label.config(text=f"Progress: {progress:.2f}%")
            self.results_text.insert(tk.END, f"Checked {checked_count}: Available {available_count}\n")
            self.results_text.see(tk.END)  # Scroll to the bottom
            self.root.update_idletasks()
        
        # Start the username checking process
        for i, username in enumerate(tqdm(self.usernames, desc="Checking usernames")):
            username_result, elapsed_time = check_username(username)
            if username_result:
                self.available_usernames.append(username_result)
                with open("available_usernames.txt", "a") as f:
                    f.write(f"{username_result}\n")
            update_progress(i + 1, len(self.available_usernames))
        
        messagebox.showinfo("Complete", f"Username checking complete. Found {len(self.available_usernames)} available usernames.")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = UsernameCheckerApp(root)
    root.mainloop()