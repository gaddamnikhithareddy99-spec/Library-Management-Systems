import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# ------------------------------
# Default Data (Permanent)
# ------------------------------
books_data = [
    {"title": "Python Basics", "author": "Mark Lutz", "shelf": "A1", "status": "available"},
    {"title": "Data Structures", "author": "Narasimha Karumanchi", "shelf": "B1", "status": "available"},
    {"title": "Operating System", "author": "Galvin", "shelf": "C2", "status": "available"},
    {"title": "DBMS Concepts", "author": "Korth", "shelf": "D3", "status": "available"},
    {"title": "Java Programming", "author": "James Gosling", "shelf": "E2", "status": "available"},
]

rental_records = {}
RENT_PER_DAY = 10  # ₹10 per day


# ------------------------------
# Helper Functions
# ------------------------------
def find_book(title):
    for b in books_data:
        if b["title"].lower() == title.lower():
            return b
    return None


# ------------------------------
# Main App Class
# ------------------------------
class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Library Manager")
        self.root.geometry("850x600")
        self.create_ui()
        self.load_books()

    def create_ui(self):
        frm_top = tk.Frame(self.root)
        frm_top.pack(pady=10)

        tk.Button(frm_top, text="➕ Add Book", command=self.add_book, width=15).grid(row=0, column=0, padx=5)
        tk.Button(frm_top, text="📖 Rent Books", command=self.rent_book_prompt, width=15).grid(row=0, column=1, padx=5)
        tk.Button(frm_top, text="↩️ Return Books", command=self.return_books_prompt, width=15).grid(row=0, column=2, padx=5)
        tk.Button(frm_top, text="❌ Delete Book", command=self.delete_book, width=15).grid(row=0, column=3, padx=5)

        cols = ("Title", "Author", "Shelf", "Status")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_books(self):
        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for book in books_data:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["shelf"], book["status"]))

    def add_book(self):
        win = tk.Toplevel(self.root)
        win.title("Add Book")
        win.geometry("400x300")
        win.grab_set()

        tk.Label(win, text="Enter book details in this format:", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Label(win, text="Title  Author  ShelfNo (Example: PythonBasics Mark A1)", fg="gray").pack(pady=5)

        txt = tk.Text(win, width=45, height=8)
        txt.pack(padx=10, pady=10)

        def add_all():
            lines = txt.get("1.0", tk.END).splitlines()
            added = 0
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 3:
                    title = " ".join(parts[:-2])
                    author = parts[-2]
                    shelf = parts[-1]
                    books_data.append({"title": title, "author": author, "shelf": shelf, "status": "available"})
                    added += 1
            messagebox.showinfo("Added", f"{added} book(s) added successfully.")
            win.destroy()
            self.refresh_table()

        tk.Button(win, text="Add Books", command=add_all).pack(pady=10)

    # ------------------------------
    # Rent Multiple Books
    # ------------------------------
    def rent_book_prompt(self):
        win = tk.Toplevel(self.root)
        win.title("Rent Multiple Books")
        win.geometry("500x400")
        win.grab_set()

        tk.Label(win, text="Enter Person Name:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=4)
        person_var = tk.StringVar()
        tk.Entry(win, textvariable=person_var, width=40, font=("Arial", 11)).pack(padx=10, pady=4)

        tk.Label(win, text="Enter Book Titles (one per line):", font=("Arial", 11)).pack(anchor="w", padx=10, pady=4)
        txt = scrolledtext.ScrolledText(win, width=55, height=10)
        txt.pack(padx=10, pady=6)

        def rent_all():
            person = person_var.get().strip()
            if not person:
                messagebox.showwarning("Missing", "Please enter the person's name.")
                return
            titles = [t.strip() for t in txt.get("1.0", tk.END).splitlines() if t.strip()]
            rented_count = 0
            for title in titles:
                book = find_book(title)
                if not book or book["status"] != "available":
                    continue
                book["status"] = "rented"
                rental_records[book["title"]] = {"person": person, "rent_date": datetime.now()}
                rented_count += 1

            messagebox.showinfo("Done", f"{rented_count} book(s) rented to {person}.")
            win.destroy()
            self.refresh_table()

        tk.Button(win, text="Rent All", command=rent_all, width=12).pack(pady=10)

    # ------------------------------
    # Return Multiple Books + Rent Calculation
    # ------------------------------
    def return_books_prompt(self):
        win = tk.Toplevel(self.root)
        win.title("Return Multiple Books")
        win.geometry("450x350")
        win.grab_set()

        tk.Label(win, text="Enter Book Titles (one per line):", font=("Arial", 11)).pack(anchor="w", padx=10, pady=4)
        txt = scrolledtext.ScrolledText(win, width=50, height=10)
        txt.pack(padx=10, pady=6)

        def return_all():
            titles = [t.strip() for t in txt.get("1.0", tk.END).splitlines() if t.strip()]
            summary = ""
            total_amount = 0
            returned = 0

            for title in titles:
                book = find_book(title)
                if not book or book["status"] != "rented":
                    continue
                rent_info = rental_records.get(book["title"])
                if rent_info:
                    rent_days = (datetime.now() - rent_info["rent_date"]).days + 1
                    amount = rent_days * RENT_PER_DAY
                    total_amount += amount
                    summary += f"{title} → {rent_days} days × ₹{RENT_PER_DAY} = ₹{amount}\n"
                    book["status"] = "available"
                    rental_records.pop(book["title"], None)
                    returned += 1

            if returned == 0:
                messagebox.showinfo("No Books", "No rented books found in the list.")
                return

            summary += f"\nTotal Rent: ₹{total_amount}"
            messagebox.showinfo("Books Returned", summary)
            win.destroy()
            self.refresh_table()

        tk.Button(win, text="Return All", command=return_all, width=12).pack(pady=10)

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Book", "Please select a book to delete.")
            return
        val = self.tree.item(selected[0])["values"]
        title = val[0]
        for b in books_data:
            if b["title"] == title:
                books_data.remove(b)
                break
        messagebox.showinfo("Deleted", f"Book '{title}' deleted successfully.")
        self.refresh_table()


# ------------------------------
# Run App
# ------------------------------
root = tk.Tk()
app = LibraryApp(root)
root.mainloop()
