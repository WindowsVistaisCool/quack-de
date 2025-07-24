import customtkinter as ctk
from lib.CommandUI import CommandUI
from typing import Type

class NavigationPage(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, title: str, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.configure(fg_color=master._fg_color)
        self.ui = CommandUI(self)
        self.grid_columnconfigure(0, weight=1)
    
    def onShow(self):
        """Override this method to handle when the page is shown."""
        pass

    def onHide(self):
        """Override this method to handle when the page is hidden."""
        pass

class NavigationManager:
    def __init__(self, contentMaster: ctk.CTkFrame):
        self.contentMaster: ctk.CTkFrame = contentMaster
        self.currentPage: 'NavigationPage' = None
        self.previousPage: 'NavigationPage' = None
        self.pages = {}

    def pageExists(self, page: Type[NavigationPage]) -> bool:
        return page in self.pages

    def registerPage(self, page: NavigationPage):
        self.pages[type(page)] = page
    
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
