import traceback
import customtkinter as ctk
from typing import Generic, TypeVar

T = TypeVar('T', bound=ctk.CTkBaseClass)

class CommandUIItem(list, Generic[T]):
    def __init__(self, root, className, instance: T, command, exceptionCallback):
        super().__init__([root, className, instance, command, exceptionCallback])
        self.gridProperties = {}

    def __new__(cls, root, className, instance, command, exceptionCallback):
        return super().__new__(cls, [root, className, instance, command, exceptionCallback])

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

    @property
    def exceptionCallback(self):
        return self[4]
    
    def getInstance(self) -> T:
        return self.instance

    def setCommand(self, command):
        def commandWrapper():
            try:
                command()
            except Exception:
                ex = f"{traceback.format_exc()}"
                print(ex)
                self.exceptionCallback(ex)
        self[3] = commandWrapper
        if command and callable(command):
            self.instance.configure(command=commandWrapper)
        else:
            self.instance.configure(command=None)
        return self

    def setExceptionCallback(self, exceptionCallback):
        self[4] = exceptionCallback
    
    def withGridProperties(self, **kwargs):
        self.gridProperties.update(kwargs)
        return self
    
    def grid(self, **kwargs):
        if kwargs.__len__() != 0:
            self.gridProperties = kwargs
            self.instance.grid(**kwargs)
        elif self.gridProperties.keys().__len__() > 0:
            self.instance.grid(**self.gridProperties)
    
    def drop(self):
        """Removes the instance from the grid."""
        self.instance.grid_forget()

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
            "root": CommandUIItem(None, None, master, None, None)
        }
        self.exceptionUI: CommandUIItem = None
        self.exceptionCallback = lambda e: print(e)

    def add(self, className, id: str, root = None, **kwargs):
        if id in self.items:
            raise ValueError(f"UI element '{id}' already exists.")
        if not root:
            root = self.window
        self.items[id] = CommandUIItem(
            root,
            className,
            className(master=root, **kwargs),
            None if not kwargs.get("command") else kwargs["command"],
            self.exceptionCallback)
        return self.items[id]
    
    # def addExceptionUI(self, className, root=None, **kwargs):
    #     if self.exceptionUI is not None:
    #         raise ValueError("Exception UI already exists.")
    #     if not root:
    #         root = self.window
    #     self.exceptionUI = CommandUIItem(root, className, className(master=root, **kwargs), None if not kwargs.get("command") else kwargs["command"])
    #     return self.exceptionUI

    def addCommand(self, id: str, command):
        if id not in self.items:
            raise ValueError(f"UI element '{id}' does not exist.")
        self.items[id].setExceptionCallback(self.exceptionCallback) # re-add the exception callback
        self.items[id].command = command

    def setExceptionCallback(self, callback):
        self.exceptionCallback = callback

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
                item.drop()
            except:
                print(f"Error dropping UI element '{item.className}'")
