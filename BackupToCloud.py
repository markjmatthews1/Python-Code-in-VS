import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except Exception as e:
        return str(e)

def git_add():
    output = run_git_command("git add .")
    messagebox.showinfo("Git Add", output or "Staged all changes.")

def git_commit():
    msg = simpledialog.askstring("Commit Message", "Enter commit message:")
    if msg:
        output = run_git_command(f'git commit -m "{msg}"')
        messagebox.showinfo("Git Commit", output or "Committed changes.")

def git_push():
    output = run_git_command("git push")
    messagebox.showinfo("Git Push", output or "Pushed to remote.")

root = tk.Tk()
root.title("Simple Git GUI")

tk.Button(root, text="Stage (git add .)", command=git_add, width=30).pack(pady=5)
tk.Button(root, text="Commit (git commit)", command=git_commit, width=30).pack(pady=5)
tk.Button(root, text="Push (git push)", command=git_push, width=30).pack(pady=5)

root.mainloop()