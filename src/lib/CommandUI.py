import customtkinter as ctk
from typing import Generic, TypeVar

T = TypeVar('T', bound=ctk.CTkBaseClass)

class CommandUIItem(list, Generic[T]):
    def __init__(self, root, className, instance: T, command):
        super().__init__([root, className, instance, command])
        self.gridProperties = {}

    def __new__(cls, root, className, instance, command):
        return super().__new__(cls, [root, className, instance, command])

    @property
    def root(self):
        return self[0]

    @property
    def className(self):
        return self[1]

    @property
    def instance(self) -> T:
        return self[2]
    
    @property
    def command(self):
        return self[3]
    
    def getInstance(self) -> T:
        return self.instance
    
    def setCommand(self, command):
        self[3] = command
        if command and callable(command):
            self.instance.configure(command=command)
        else:
            self.instance.configure(command=None)
        return self
    
    def withGridProperties(self, **kwargs):
        self.gridProperties.update(kwargs)
        return self
    
    def grid(self, **kwargs):
        if kwargs.__len__() != 0:
            self.gridProperties = kwargs
            self.instance.grid(**kwargs)
        elif self.gridProperties.keys().__len__() > 0:
            self.instance.grid(**self.gridProperties)

    @command.setter
    def command(self, value):
        self[3] = value
        if value and callable(value):
            self.instance.configure(command=value)
        else:
            self.instance.configure(command=None)


class CommandUI:
    def __init__(self, master):
        self.window = master
        self.items = {
            "root": CommandUIItem(None, None, master, None)
        }
    
    def add(self, className, id: str, root = None, **kwargs):
        if id in self.items:
            raise ValueError(f"UI element '{id}' already exists.")
        if not root:
            root = self.window
        self.items[id] = CommandUIItem(root, className, className(master=root, **kwargs), None if not kwargs.get("command") else kwargs["command"])
        return self.items[id]

    def addCommand(self, id: str, command):
        if id not in self.items:
            raise ValueError(f"UI element '{id}' does not exist.")
        self.items[id].command = command

    def get(self, id: str):
        if id not in self.items:
            raise ValueError(f"UI element '{id}' does not exist.")
        return self.items[id]

    def gridAll(self):
        for item in self.items.values():
            item.grid()
    
    def dropAll(self):
        for item in self.items.values():
            if item.className is None:
                continue
            try:
                item.getInstance().grid_forget()
            except:
                print(f"Error dropping UI element '{item.className}'")
