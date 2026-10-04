import tkinter as tk
from tkinter import ttk


def bmi_calculator(weight_kg, height_m):
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be greater than zero.")
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "You are below a healthy weight range.", "#1f77b4"
    if bmi < 25:
        return "Normal", "Great! You are in a healthy range.", "#2ca02c"
    if bmi < 30:
        return "Overweight", "You are above the healthy range.", "#ff9900"
    return "Obesity", "You are in the obesity range.", "#d62728"


class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("420x500")
        self.configure(bg="#f2f2f2")
        self.minsize(360, 420)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.header = tk.Label(
            self,
            text="BMI Calculator",
            font=("Arial", 22, "bold"),
            bg="#f2f2f2",
            fg="#1f1f1f",
            pady=18,
        )
        self.header.pack()

        form = tk.Frame(self, bg="#f2f2f2")
        form.pack(padx=24, pady=10, fill="x")

        tk.Label(form, text="Name", font=("Arial", 12, "bold"), bg="#f2f2f2").pack(anchor="w")
        self.name_entry = tk.Entry(form, font=("Arial", 12), width=30)
        self.name_entry.pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Weight (kg)", font=("Arial", 12, "bold"), bg="#f2f2f2").pack(anchor="w")
        self.weight_entry = tk.Entry(form, font=("Arial", 12), width=30)
        self.weight_entry.pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Height (m)", font=("Arial", 12, "bold"), bg="#f2f2f2").pack(anchor="w")
        self.height_entry = tk.Entry(form, font=("Arial", 12), width=30)
        self.height_entry.pack(fill="x", pady=(4, 12))

        button_frame = tk.Frame(self, bg="#f2f2f2")
        button_frame.pack(pady=(8, 10))

        self.calculate_button = tk.Button(
            button_frame,
            text="Calculate BMI",
            width=18,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.calculate_bmi,
        )
        self.calculate_button.pack(side="left", padx=8)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            width=10,
            height=2,
            bg="#6c757d",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.clear_fields,
        )
        self.clear_button.pack(side="left", padx=8)

        self.result_label = tk.Label(
            self,
            text="",
            font=("Arial", 13, "bold"),
            wraplength=320,
            justify="center",
            bg="#ffffff",
            fg="#1f1f1f",
            padx=18,
            pady=18,
            borderwidth=2,
            relief="solid",
        )
        self.result_label.pack(padx=24, pady=14, fill="x")

    def calculate_bmi(self):
        name = self.name_entry.get().strip()
        try:
            weight = float(self.weight_entry.get())
            height_m = float(self.height_entry.get())
        except ValueError:
            self.result_label.config(text="Please enter valid numbers.", bg="#ffe5e5", fg="#8b1e1e")
            return

        try:
            bmi = bmi_calculator(weight, height_m)
        except ValueError as exc:
            self.result_label.config(text=str(exc), bg="#ffe5e5", fg="#8b1e1e")
            return

        category, message, color = get_bmi_category(bmi)
        display_name = name if name else "User"
        self.result_label.config(
            text=f"{display_name}\nBMI: {bmi}\nCategory: {category}\n{message}",
            bg=color,
            fg="white",
        )

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.result_label.config(text="", bg="#ffffff", fg="#1f1f1f")


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()