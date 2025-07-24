import customtkinter as ctk
from lib.CommandUI import CommandUI

class NotifierUI:
    FONT = ("Arial", 24, "normal")

    _MESSAGE_SUPPLIER = None # allows the text to update dynamically when set()
    _ACTIVE_NOTIFIER: 'NotifierUI' = None # the notifier currently being displayed
    _NOTIF_PRESENT = False
    _DELAY_FUNCTION = lambda delay_ms, end_call: None # function to delay the clearing of the notif

    def __init__(self, master, masterUI: 'CommandUI'):
        self.master = master
        self.masterUI = masterUI
        self.ui = CommandUI(master)
        self._initUI()

    def _initUI(self):
        self.frame = self.ui.add(ctk.CTkFrame, "notifier_frame",
                                 corner_radius=32,
                                 fg_color=("coral1", "red4"),
                                 bg_color="transparent",
                                 ).withGridProperties(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame.getInstance().grid_rowconfigure(0, weight=1)
        self.frame.getInstance().grid_columnconfigure(0, weight=1)

        self.ui.add(ctk.CTkLabel, "notifier_label",
                    root=self.frame.getInstance(),
                    textvariable=self._MESSAGE_SUPPLIER,
                    font=self.FONT,
                    justify="center"
                    ).withGridProperties(row=0, column=0, padx=20, pady=10, sticky="new")

    def show(self):
        self.masterUI.gridAll()
        self.ui.gridAll()
    
    def drop(self):
        self.masterUI.dropAll()
        self.ui.dropAll()
        
    def setActive(self):
        if NotifierUI._ACTIVE_NOTIFIER is not None:
            NotifierUI._ACTIVE_NOTIFIER.frame.getInstance().grid_forget()
        NotifierUI._ACTIVE_NOTIFIER = self
    
    @classmethod
    def setFont(cls, font: tuple):
        """Sets the font for the notification label."""
        cls.FONT = font

    @classmethod
    def setMessageSupplier(cls, message_supplier: ctk.StringVar):
        """Sets the StringVar that will be used to update the notification message."""
        cls._MESSAGE_SUPPLIER = message_supplier
    
    @classmethod
    def setDelayFunction(cls, delayFunction):
        """Sets the function to call when the notification should be cleared."""
        cls._DELAY_FUNCTION = delayFunction

    @classmethod
    def notify(cls, message: str, delay_ms: int = 3000):
        """Displays a notification with the given message."""
        if cls._MESSAGE_SUPPLIER is not None and message is not None and not cls._NOTIF_PRESENT:
            cls._MESSAGE_SUPPLIER.set(message)
            if cls._ACTIVE_NOTIFIER is not None:
                cls._ACTIVE_NOTIFIER.show()
                cls._NOTIF_PRESENT = True
                # clear the grid from the notification frame
                def clear_notif():
                    cls._ACTIVE_NOTIFIER.drop()
                    cls._NOTIF_PRESENT = False
                cls._DELAY_FUNCTION(delay_ms, clear_notif)
