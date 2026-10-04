import secrets
import string
import tkinter as tk
from tkinter import messagebox, ttk


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("430x500")
        self.root.minsize(380, 440)
        self.root.configure(bg="#f2f2f2")

        self.length_var = tk.StringVar(value="12")
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=False)
        self.symbols_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()

        self.style = ttk.Style(root)
        self.style.configure("Accent.TButton", background="#16b6b0", foreground="white")
        self.style.configure("Copy.TButton", background="#079bc1", foreground="white")

        form = tk.Frame(root, bg="#f2f2f2")
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form,
            text="Password Length:",
            bg="#f2f2f2",
            font=("Arial", 11),
        ).grid(row=0, column=0, sticky="e", padx=(0, 8), pady=(0, 12))

        self.length_entry = ttk.Entry(
            form,
            textvariable=self.length_var,
            width=18,
            font=("Arial", 11),
        )
        self.length_entry.grid(row=0, column=1, sticky="w", pady=(0, 12))

        options = (
            ("Uppercase", self.uppercase_var),
            ("Lowercase", self.lowercase_var),
            ("Digits", self.digits_var),
            ("Symbols", self.symbols_var),
        )
        for row, (label, variable) in enumerate(options, start=1):
            ttk.Checkbutton(form, text=label, variable=variable).grid(
                row=row, column=0, columnspan=2, sticky="w", padx=(4, 0), pady=3
            )

        ttk.Button(
            form,
            text="Generate Password",
            style="Accent.TButton",
            command=self.generate_password,
        ).grid(row=5, column=0, columnspan=2, pady=(16, 14))

        self.password_entry = ttk.Entry(
            form,
            textvariable=self.password_var,
            width=30,
            justify="center",
            font=("Arial", 11),
            state="readonly",
        )
        self.password_entry.grid(row=6, column=0, columnspan=2, pady=(0, 8), ipady=3)

        ttk.Button(
            form,
            text="Copy Password",
            style="Copy.TButton",
            command=self.copy_password,
        ).grid(row=7, column=0, columnspan=2, pady=3)

        self.length_entry.focus_set()

    def generate_password(self):
        try:
            length = int(self.length_var.get())
        except ValueError:
            messagebox.showerror("Invalid Length", "Enter a whole number for password length.")
            return

        if length < 8:
            messagebox.showerror("Invalid Length", "Password length must be at least 8.")
            return

        character_groups = []
        if self.uppercase_var.get():
            character_groups.append(string.ascii_uppercase)
        if self.lowercase_var.get():
            character_groups.append(string.ascii_lowercase)
        if self.digits_var.get():
            character_groups.append(string.digits)
        if self.symbols_var.get():
            character_groups.append(string.punctuation)

        if not character_groups:
            messagebox.showerror("No Character Types", "Select at least one character type.")
            return

        if length < len(character_groups):
            messagebox.showerror(
                "Invalid Length",
                "Password length is too short for the selected character types.",
            )
            return

        password_characters = [secrets.choice(group) for group in character_groups]
        available_characters = "".join(character_groups)
        password_characters.extend(
            secrets.choice(available_characters)
            for _ in range(length - len(password_characters))
        )
        secrets.SystemRandom().shuffle(password_characters)
        self.password_var.set("".join(password_characters))

    def copy_password(self):
        password = self.password_var.get()
        if not password:
            messagebox.showinfo("No Password", "Generate a password before copying it.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        messagebox.showinfo("Copied", "Password copied to the clipboard.")


def main():
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
