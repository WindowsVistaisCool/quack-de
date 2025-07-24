import customtkinter as ctk

class Dialogs:
    class _DialogBase(ctk.CTkToplevel):
        def __init__(self, master, title: str, message: str, **kwargs):
            super().__init__(master, **kwargs)
            self.title(title)
            self.message = message
            self.geometry("400x200")
            self.resizable(False, False)
        
        def _initUI(self):
            ctk.CTkLabel(self, text=self.message).pack(padx=20, pady=10)

    class DialogYesNo(_DialogBase):
        def __init__(self, master, title: str, message: str, yes_command=None, no_command=None):
            super().__init__(master, title, message)
            self.yes_command = yes_command
            self.no_command = no_command