import tkinter as tk

def test_two_columns():
    root = tk.Tk()
    root.title("Two Column Test")
    root.geometry("1000x500")
    root.configure(bg="#1e1e2e")
    
    # Main container
    main_frame = tk.Frame(root, bg="#1e1e2e")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Container for two columns
    container = tk.Frame(main_frame, bg="#2d3748", relief="raised", bd=2)
    container.pack(fill="both", expand=True)
    
    # Configure grid for two equal columns
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)
    
    # LEFT COLUMN
    left_column = tk.LabelFrame(container, text="💰 LEFT COLUMN", 
                               font=("Arial", 14, "bold"), 
                               bg="#4ade80", fg="white", 
                               relief="raised", bd=3)
    left_column.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    # Add content to left column
    for i in range(5):
        tk.Label(left_column, text=f"Left Content {i+1}", 
                font=("Arial", 12), bg="#4ade80", fg="white").pack(pady=5)
    
    # RIGHT COLUMN  
    right_column = tk.LabelFrame(container, text="📈 RIGHT COLUMN", 
                                font=("Arial", 14, "bold"), 
                                bg="#ef4444", fg="white", 
                                relief="raised", bd=3)
    right_column.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    
    # Add content to right column
    for i in range(5):
        tk.Label(right_column, text=f"Right Content {i+1}", 
                font=("Arial", 12), bg="#ef4444", fg="white").pack(pady=5)
    
    # Configure row weight
    container.grid_rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing basic two-column layout...")
    test_two_columns()
