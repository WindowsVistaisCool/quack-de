import customtkinter as ctk
from lib.CommandUI import CommandUI, CommandUIItem
from typing import Optional

class SwappableUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        super().__init__(master, **kwargs)
        self.configure(fg_color=master.cget("fg_color"), bg_color=master.cget("bg_color"))
        self.grid(row=0, column=0, sticky="nsew")
        self.frames = {}
        self._currentFrame = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def newFrame(self, name: str):
        if name in self.frames:
            raise ValueError(f"Frame '{name}' already exists.")
        frame = SwappableUIFrame(self)
        self.frames[name] = frame
        return frame
    
    def getFrame(self, name: str) -> Optional['SwappableUIFrame']:
        if name not in self.frames:
            raise ValueError(f"Frame '{name}' does not exist.")
        return self.frames[name]

    def swap(self, name: str):
        if name not in self.frames:
            raise ValueError(f"Frame '{name}' does not exist.")
        
        if name == self._currentFrame:
            return
        
        self._currentFrame = name

        # Hide all frames
        for frame in self.frames.values():
            frame.grid_forget()
        # Show the requested frame
        self.frames[name].grid(row=0, column=0, sticky="nsew")

class SwappableUIFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ui = CommandUI(self)
        self.configure(fg_color=master.cget("fg_color"), border_color=master.cget("border_color"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

