import customtkinter as ctk
from lib.CommandUI import CommandUI
from typing import Type

class NavigationPage(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title
        self.ui = CommandUI(self)

class NavigationManager:
    def __init__(self, navDisplay: ctk.CTkFrame):
        self.navDisplay: ctk.CTkFrame = navDisplay
        self.currentPage: 'NavigationPage' = None
        self.pages = {}

    def registerPage(self, page: NavigationPage):
        self.pages[type(page)] = page
    
    def setInitialPage(self, page: Type[NavigationPage]):
        if page not in self.pages:
            raise ValueError(f"Page {page} is not registered.")
        self.currentPage = self.pages[page]
        self.navigate(page)

    def navigate(self, page: Type[NavigationPage]):
        if page not in self.pages:
            raise ValueError(f"Page {page} is not registered.")
        
        if self.currentPage is None:
            raise ValueError("No current page to navigate from. (Use setInitialPage first.)")
        
        self.currentPage.grid_forget()
        self.currentPage = self.pages[page]
        self.currentPage.grid(row=0, column=0, sticky="nsew")
