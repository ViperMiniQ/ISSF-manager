import tkinter


class RightClickMenuListbox(tkinter.Listbox):
    def __init__(self, *args, **kwargs):
        tkinter.Listbox.__init__(self, *args, **kwargs)
        self.menu = None
        self.bind("<Button-3>", self.right_click)

    def show_menu(self, event):
        if self.menu is not None:
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def assign_menu(self, menu: tkinter.Menu):
        self.menu = menu

    def right_click(self, event):
        self.selection_clear(0, tkinter.END)
        self.selection_set(self.nearest(event.y))
        self.activate(self.nearest(event.y))
        self.show_menu(event)
