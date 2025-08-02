import customtkinter as ctk
from lib.CommandUI import CommandUI


class NotifierService:
    _MESSAGE_SUPPLIER = None  # allows the text to update dynamically when set()
    _ACTIVE_NOTIFIER: "NotifierUI" = None  # the notifier currently being displayed
    _NOTIF_PRESENT = False

    _DELAY_ID = ""  # the id returned by _DELAY_FUNCTION (needed to cancel the delay)
    _DELAY_FUNCTION = (
        lambda delay_ms, end_call: ""
    )  # function to delay the clearing of the notif
    _CLEAR_DELAY = lambda id: None  # function to clear the delay, if needed

    @classmethod
    def init(cls):
        """Sets the StringVar that will be used to update the notification message."""
        cls._MESSAGE_SUPPLIER = ctk.StringVar(value="")

    @classmethod
    def setDelayFuncs(cls, delayFunction, clearDelay):
        """Sets the function to call when the notification should be cleared."""
        cls._DELAY_FUNCTION = delayFunction
        cls._CLEAR_DELAY = clearDelay

    @classmethod
    def setActiveUI(cls, notifier: "NotifierUI"):
        if NotifierService._ACTIVE_NOTIFIER is not None:
            NotifierService._ACTIVE_NOTIFIER.frame.getInstance().grid_forget()
        NotifierService._ACTIVE_NOTIFIER = notifier

    @classmethod
    def notify(cls, message: str, delay_ms: int = 3000):
        """Displays a notification with the given message."""
        if cls._MESSAGE_SUPPLIER is not None and message is not None:
            if cls._NOTIF_PRESENT:
                cls.clear()

            cls._MESSAGE_SUPPLIER.set(message)
            if cls._ACTIVE_NOTIFIER is not None:
                cls._ACTIVE_NOTIFIER.show()
                cls._NOTIF_PRESENT = True

                # clear the grid from the notification frame
                def clear_notif():
                    cls._ACTIVE_NOTIFIER.drop()
                    cls._NOTIF_PRESENT = False

                cls._DELAY_ID = cls._DELAY_FUNCTION(delay_ms, clear_notif)

    @classmethod
    def clear(cls):
        """Clears the current notification."""
        if cls._ACTIVE_NOTIFIER is not None:
            cls._CLEAR_DELAY(cls._DELAY_ID)
            cls._ACTIVE_NOTIFIER.drop()
            cls._NOTIF_PRESENT = False
            if cls._MESSAGE_SUPPLIER is not None:
                cls._MESSAGE_SUPPLIER.set("")


class NotifierUI(CommandUI):
    FONT = ("Arial", 24, "normal")

    def __init__(self, master, masterUI: "CommandUI"):
        super().__init__(master)
        self.master = master
        self.masterUI = masterUI
        self._initUI()

    def _initUI(self):
        self.frame = self.add(
            ctk.CTkFrame,
            "notifier_frame",
            corner_radius=32,
            fg_color=("coral1", "red4"),
            bg_color="transparent",
        ).withGridProperties(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame.getInstance().grid_rowconfigure(0, weight=1)
        self.frame.getInstance().grid_columnconfigure(0, weight=1)

        self.add(
            ctk.CTkLabel,
            "notifier_label",
            root=self.frame.getInstance(),
            textvariable=NotifierService._MESSAGE_SUPPLIER,
            font=self.FONT,
            justify="center",
        ).withGridProperties(row=0, column=0, padx=20, pady=10, sticky="new")

    def show(self):
        self.masterUI.gridAll()
        self.gridAll()

    def drop(self):
        self.masterUI.dropAll()
        self.dropAll()

    @classmethod
    def setFont(cls, font: tuple):
        """Sets the font for the notification label."""
        cls.FONT = font
