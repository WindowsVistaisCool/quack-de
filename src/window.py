import tkinter as tk

root = tk.Tk()
root.geometry("1024x768")

label = tk.Label(root, text="ts now different lol!")
label.config(width=200, height=100)

label.pack()

root.mainloop()