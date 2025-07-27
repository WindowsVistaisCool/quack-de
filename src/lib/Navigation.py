import customtkinter as ctk
from lib.CommandUI import CommandUI
from datetime import datetime
from typing import Type, Optional

"""
[TODO]
idea for nav pages in the future.
all pages rn import an approot, so bascially have a
NavigationPage<T> where T is the app root `ctk.CTk` instance
boom genius
"""
class NavigationPage(ctk.CTkFrame):
    def __init__(self, navigator: 'NavigationManager', master: ctk.CTkFrame, title: str, **kwargs):
        self.is_ephemeral = "ephemeral" in kwargs and kwargs["ephemeral"]
        if self.is_ephemeral:
            kwargs.pop("ephemeral")

        super().__init__(master, **kwargs)

        self.navigator = navigator
        if not self.is_ephemeral:
            self.navigator.registerPage(self)

        self.title = title
        self.configure(fg_color=master._fg_color) # copy the master frame's color
        self.ui = CommandUI(self)

        # if the navigator has an exception page, set the exception callback
        if self.navigator.exceptionPage:
            def exception_navigator(exception: str):
                self.navigator.exceptionMessageSupplier.set(exception)
                self.navigator.navigate(type(self.navigator.exceptionPage))
            self.ui.setExceptionCallback(exception_navigator)
        
        # [TODO] this was here at one point, but I don't remember why
        self.grid_columnconfigure(0, weight=1)
    
    def onShow(self):
        """Override this method to handle when the page is shown."""
        pass

    def onHide(self) -> Optional[bool]:
        """
        Override this method to handle when the page is hidden.
        Return True if the navigation should be cancelled, False or None to continue.
        currently not functional [TODO]
        """
        pass

class EphemeralNavigationPage(NavigationPage):
    def __init__(self, navigator: 'NavigationManager', master: ctk.CTkFrame, title: str, **kwargs):
        super().__init__(navigator, master, title, ephemeral=True, **kwargs)
        self.is_ephemeral = True

# TODO: CONVERT TO EPHEMERAL PAGE
class DefaultExceptionPage(NavigationPage):
    def __init__(self, navigator, master: ctk.CTkFrame, errorSupplier: ctk.StringVar, **kwargs):
        super().__init__(navigator, master, title="Error", **kwargs)
        self.errorSupplier = errorSupplier
        self.ui = CommandUI(self)

        # A string variable to hold the error class name that is shown on error
        self.navPageClass = ctk.StringVar(value="")

        self._initUI()
        self._initCommands()
    
    def _initUI(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.configure(fg_color="black", bg_color="black")

        self.ui.add(ctk.CTkLabel, "error_label",
                    text=f"An error occurred!",
                    fg_color="red",
                    bg_color="black",
                    text_color="white",
                    font=("Arial", 24, "bold")
                    ).grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nw")
        self.ui.add(ctk.CTkLabel, "error_class",
                    textvariable=self.navPageClass,
                    text_color="white",
                    font=("Arial", 12),
                    justify="left"
                    ).grid(row=1, column=0, padx=20, pady=5, sticky="nw")
        self.ui.add(ctk.CTkButton, "error_button",
                    text="Return to Previous Page",
                    fg_color="blue",
                    bg_color="blue",
                    hover_color="darkblue",
                    text_color="white",
                    corner_radius=0
                    ).grid(row=2, column=0, padx=20, pady=5, sticky="nw")
        self.ui.add(ctk.CTkTextbox, "error_message",
                    font=("Arial", 12),
                    state="disabled",
                    ).grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

    def _initCommands(self):
        self.ui.get("error_button").setCommand(self.navigator.navigateBack)
    
    def onShow(self):
        self.navPageClass.set(f"{datetime.now()} {type(self.navigator.previousPage)}")

        # need to re-enable and disable or else it will not update the text
        self.ui.get("error_message").getInstance().configure(state="normal")
        self.ui.get("error_message").getInstance().delete("0.0", "end")
        self.ui.get("error_message").getInstance().insert("0.0", self.errorSupplier.get())
        self.ui.get("error_message").getInstance().configure(state="disabled")

class NavigationManager:
    def __init__(self, contentMaster: ctk.CTkFrame):
        self.contentMaster: ctk.CTkFrame = contentMaster
        self.currentPage: 'NavigationPage' = None
        self.previousPage: 'NavigationPage' = None
        self.pages = {}

        self.exceptionPage = None
        self.exceptionMessageSupplier = ctk.StringVar(value="")

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
                errorSupplier=self.exceptionMessageSupplier
            )
        self.exceptionPage = exceptionPage
    
    def getPage(self, page: Type[NavigationPage]) -> Optional[NavigationPage]:
        if not self.pageExists(page):
            if self.exceptionPage:
                self.exceptionMessageSupplier.set(f"Page {page} is not registered with navigator {self.__class__}!")
                return self.getPage(type(self.exceptionPage))
            else:
                raise ValueError(f"Page {page} is not registered.")
        return self.pages.get(page, None)
    
    def navigate(self, page: Type[NavigationPage]):
        if page not in self.pages:
            if self.exceptionPage:
                self.exceptionMessageSupplier.set(f"Page {page} is not registered with navigator {self.__class__}!")
                self.navigate(type(self.exceptionPage))
            else:
                raise ValueError(f"Page {page} is not registered.")
            return
        
        if self.currentPage == self.pages[page]:
            return
        
        if self.currentPage is not None:
            if not self.currentPage.is_ephemeral:
                self.previousPage = self.currentPage

            self._pageUnload(self.currentPage) # give any page a chance to unload, regardless of ephemeral status
            
            if self.currentPage.is_ephemeral:
                self.currentPage.destroy()

        self.currentPage = self.pages[page]
        self._pageLoad(self.currentPage)
    
    def navigateEphemeral(self, page: 'NavigationPage'):
        """
        Navigates to a temporary page that does not persist in the navigation history.
        This is useful for pages that are meant to be transient, such as dialogs or popups.
        """
        if not page.is_ephemeral:
            raise ValueError("Ephemeral navigation can only be used with ephemeral pages.")
        if self.currentPage is not None:
            self.previousPage = self.currentPage
            self._pageUnload(self.currentPage)
        self.currentPage = page
        self._pageLoad(self.currentPage)
    
    def navigateBack(self):
        if self.previousPage is not None:
            self.navigate(type(self.previousPage))
    
    @staticmethod
    def _pageLoad(page: 'NavigationPage'):
        page.grid(row=0, column=0, sticky="nsew")
        page.onShow()

    @staticmethod
    def _pageUnload(page: 'NavigationPage'):
        """
        unloads a page from view
        """
        page.onHide()
        page.grid_forget()
    
# [TODO] i was smoking again apparently!
# class NavigationContentRoot(ctk.CTkFrame):
#     def __init__(self, master: ctk.CTkFrame, **kwargs):
#         super().__init__(master, **kwargs)
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#         self.getInstance().grid(row=0, column=0, sticky="nsew")
#         self.ui = CommandUI(self)
