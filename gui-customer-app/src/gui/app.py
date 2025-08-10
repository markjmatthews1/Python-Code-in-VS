from tkinter import Tk, Label, Entry, Button, Listbox, END

class CustomerApp:
    def __init__(self, master):
        self.master = master
        master.title("Customer Information")

        self.label_name = Label(master, text="Name:")
        self.label_name.pack()

        self.entry_name = Entry(master)
        self.entry_name.pack()

        self.label_age = Label(master, text="Age:")
        self.label_age.pack()

        self.entry_age = Entry(master)
        self.entry_age.pack()

        self.add_button = Button(master, text="Add Customer", command=self.add_customer)
        self.add_button.pack()

        self.display_button = Button(master, text="Display Customers", command=self.display_customers)
        self.display_button.pack()

        self.customer_listbox = Listbox(master)
        self.customer_listbox.pack()

        self.customers = []

    def add_customer(self):
        name = self.entry_name.get()
        age = self.entry_age.get()
        if name and age:
            self.customers.append(f"{name}, Age: {age}")
            self.entry_name.delete(0, END)
            self.entry_age.delete(0, END)

    def display_customers(self):
        self.customer_listbox.delete(0, END)
        for customer in self.customers:
            self.customer_listbox.insert(END, customer)