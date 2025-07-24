import customtkinter as ctk

class CommandUIItem(list):
    def __init__(self, root, element, item, command):
        super().__init__([root, element, item, command])

    def __new__(cls, root, element, item, command):
        return super().__new__(cls, [root, element, item, command])

    @property
    def root(self):
        return self[0]

    @property
    def element(self):
        return self[1]

    @property
    def item(self):
        return self[2]

    @property
    def command(self):
        return self[3]

    @command.setter
    def command(self, value):
        self[3] = value
        if value and callable(value):
            self.item.configure(command=value)
        else:
            self.item.configure(command=None)


class CommandUI:
    def __init__(self, master):
        self.window = master
        self.items = {
            "root": CommandUIItem(None, None, master, None)
        }
    
    def add(self, element, id: str, root = None, **kwargs):
        if id in self.items:
            raise ValueError(f"UI element '{id}' already exists.")
        if not root:
            root = self.window
        item = element(root, **kwargs)
        self.items[id] = CommandUIItem(root, element, item, None if not kwargs.get("command") else kwargs["command"])
        return item

    def addCommand(self, id: str, command):
        if id not in self.items:
            raise ValueError(f"UI element '{id}' does not exist.")
        self.items[id].command = command


    def get(self, id: str):
        if id not in self.items:
            raise ValueError(f"UI element '{id}' does not exist.")
        return self.items[id][1]
