import customtkinter as ctk
from lib.CommandUI import CommandUI
from typing import Type

class NavigationPage(ctk.CTkFrame):
    def __init__(self, navigator: 'NavigationManager', master: ctk.CTkFrame, title: str, **kwargs):
        super().__init__(master, **kwargs)
        self.navigator = navigator
        self.navigator.registerPage(self)
        self.title = title
        self.configure(fg_color=master._fg_color)
        self.ui = CommandUI(self)

        if self.navigator.exceptionPage:
            def exception_navigator(exception: str):
                self.navigator.exceptionMessage.set(exception)
                self.navigator.navigate(type(self.navigator.exceptionPage))
            self.ui.setExceptionCallback(exception_navigator)
        self.grid_columnconfigure(0, weight=1)
    
    def onShow(self):
        """Override this method to handle when the page is shown."""
        pass

    def onHide(self):
        """Override this method to handle when the page is hidden."""
        pass

class DefaultExceptionPage(NavigationPage):
    def __init__(self, navigator, master: ctk.CTkFrame, error: ctk.StringVar, **kwargs):
        super().__init__(navigator, master, title="Error", **kwargs)
        self.error = error
        self.ui = CommandUI(self)

        self._initUI()
        self._initCommands()
    
    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.configure(fg_color="black", bg_color="black")

        self.ui.add(ctk.CTkLabel, "error_label",
                    text=":( An unexpected error occurred!",
                    fg_color="red",
                    bg_color="black",
                    text_color="white",
                    font=("Arial", 24, "bold")
                    ).grid(row=0, column=0, padx=20, pady=20, sticky="nw")
        self.ui.add(ctk.CTkButton, "error_button",
                    text="Return to Previous Page",
                    fg_color="blue",
                    bg_color="blue",
                    text_color="white",
                    corner_radius=0
                    ).grid(row=1, column=0, padx=20, pady=5, sticky="nw")
        self.ui.add(ctk.CTkLabel, "error_message",
                    textvariable=self.error,
                    text_color="white",
                    font=("Arial", 12),
                    justify="left"
                    ).grid(row=2, column=0, padx=20, pady=20, sticky="nw")

    def _initCommands(self):
        self.ui.get("error_button").setCommand(self.navigator.navigateBack)

class NavigationManager:
    def __init__(self, contentMaster: ctk.CTkFrame):
        self.contentMaster: ctk.CTkFrame = contentMaster
        self.currentPage: 'NavigationPage' = None
        self.previousPage: 'NavigationPage' = None
        self.pages = {}

        self.exceptionPage = None
        self.exceptionMessage = ctk.StringVar(value="")

    def pageExists(self, page: Type[NavigationPage]) -> bool:
        return page in self.pages

    def registerPage(self, page: NavigationPage):
        self.pages[type(page)] = page
    
    def registerExceptionHandling(self, exceptionPage: 'NavigationPage' = None):
        if self.exceptionPage:
            raise ValueError(f"An exception handler was already created! Type: {type(self.exceptionPage)}")
        if not exceptionPage:
            exceptionPage = DefaultExceptionPage(
                navigator=self,
                master=self.contentMaster,
                error=self.exceptionMessage
            )
        self.exceptionPage = exceptionPage
    
    def navigate(self, page: Type[NavigationPage]):
        if page not in self.pages:
            raise ValueError(f"Page {page} is not registered.")
        
        if self.currentPage == self.pages[page]:
            return
        
        if self.currentPage is not None:
            self.previousPage = self.currentPage
            self.currentPage.onHide()
            self.currentPage.grid_forget()

        self.currentPage = self.pages[page]
        self.currentPage.grid(row=0, column=0, sticky="nsew")
        self.currentPage.onShow()
    
    def navigateBack(self):
        if self.previousPage is not None:
            self.navigate(type(self.previousPage))

# class NavigationContentRoot(ctk.CTkFrame):
#     def __init__(self, master: ctk.CTkFrame, **kwargs):
#         super().__init__(master, **kwargs)
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#         self.getInstance().grid(row=0, column=0, sticky="nsew")
#         self.ui = CommandUI(self)
