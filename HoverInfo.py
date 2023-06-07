import _tkinter
import tkinter as tk
import tkinter.font as tkFont
from Logger import benchmark

tooltips = []
_state = False


class ToolTip(object):
    def __init__(self, widget, text, font_size, anchor: str = "n", under_cursor: bool = False, orientation: str = "right"):
        self.widget = widget
        self.text = text
        self.check_anchor(anchor)
        self.anchor = anchor
        self.under_cursor = under_cursor
        self.orientation = orientation
        self.font = tkFont.Font(family="tahoma", size=font_size)
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.enter_event_function = None
        self.leave_event_function = None

    def showtip(self):
        """Display text in tooltip window"""
        if self.tipwindow:
            return
        text_height = tkFont.Font(font=self.font).metrics("linespace")  # TODO: multiply by number of newlines
        text_width = self.font.measure(self.get_longest_line_in_text()) #, displayof=self.tipwindow)
        offset = 5
        if not self.under_cursor:
            widget_topleft_x = self.widget.winfo_rootx()
            widget_topleft_y = self.widget.winfo_rooty()
            widget_width = self.widget.winfo_width()
            widget_height = self.widget.winfo_height()
            if "n" in self.anchor:
                if self.orientation == "right":
                    x = widget_topleft_x + (widget_width // 2) + offset
                else:
                    x = widget_topleft_x + (widget_width // 2) - text_width - offset
                y = widget_topleft_y - text_height - offset
            elif self.anchor == "w":
                if self.orientation == "right":
                    x = widget_topleft_x + offset
                else:
                    x = widget_topleft_x - text_width - offset
                y = widget_topleft_y + (widget_height // 2)
            elif self.anchor == "e":
                if self.orientation == "right":
                    x = widget_topleft_x + widget_width
                else:
                    x = widget_topleft_x + widget_width - text_width - offset
                y = widget_topleft_y + (widget_height // 2) + offset
            elif self.anchor == "s":
                if self.orientation == "right":
                    x = widget_topleft_x + (widget_width // 2) + offset
                else:
                    x = widget_topleft_x + (widget_width // 2) - text_width - offset
                y = widget_topleft_y + widget_height + offset
        else:
            x = self.get_cursor_x() + 10
            y = self.get_cursor_y() + 10
        self.tipwindow = tk.Toplevel(self.widget, bd=0)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_attributes("-topmost", True)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tipwindow,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=self.font,
            bd=0
        )
        label.pack(ipadx=1)
        self.tipwindow.update_idletasks()
        self.tipwindow.lift()

    def get_longest_line_in_text(self) -> str:
        return max(self.text.splitlines(), key=len)

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

    def get_cursor_x(self):
        return self.widget.winfo_pointerx()

    def get_cursor_y(self):
        return self.widget.winfo_pointery()

    def enter(self, event):
        self.showtip()

    def leave(self, event):
        self.hidetip()

    def activate(self):
        try:
            self.enter_event_function = self.widget.bind('<Enter>', self.enter, add="+")
            self.leave_event_function = self.widget.bind('<Leave>', self.leave, add="+")
        except _tkinter.TclError:
            pass
        global _state
        _state = True

    def deactivate(self):
        try:
            self.widget.unbind("<Enter>", self.enter_event_function)
            self.widget.unbind("<Leave>", self.leave_event_function)
        except tk.TclError:  # error occurs when widget has been destroyed and binding cannot happen
            pass
        global _state
        _state = False

    def set_text(self, text):
        self.text = text

    def check_anchor(self, anchor):
        valid_anchors = ["n", "w", "s", "e", "ne", "nw", "se", "sw"]
        if anchor not in valid_anchors:
            raise AttributeError("unsupported anchor option")


def remove_all_widget_tooltips(widget):
    for tooltip in tooltips:
        if tooltip.widget == widget:
            tooltips.remove(tooltip)


def remove_tooltip(tooltip):  # every toplevel widget on .destroy() needs to remove any tooltips it created
    tooltips.remove(tooltip)


def create_tooltip(widget, text, font_size, anchor: str = "center", under_cursor: bool = False, orientation = "right"):
    tooltip = ToolTip(widget, text, font_size, anchor, under_cursor, orientation)
    tooltips.append(tooltip)
    if _state:
        tooltips[-1].activate()
    return tooltip


def activate_all_tooltips():
    for tooltip in tooltips:
        try:
            tooltip.activate()
        except TypeError:
            pass


def deactivate_all_tooltips():
    for tooltip in tooltips:
        try:
            tooltip.deactivate()
        except TypeError:
            pass


class BaseTooltip(object):
    def __init__(self, parent, font_size):
        self.widget = parent
        self.font = tkFont.Font(family="tahoma", size=font_size)
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.enter_event_functions = []
        self.leave_event_functions = []

    def showtip(self, x, y, text):
        """Display text in tooltip window"""
        self.tipwindow = tk.Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_attributes("-topmost", True)
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tipwindow,
            text=text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=self.font
        )
        label.pack(ipadx=1)
        self.tipwindow.update_idletasks()
        self.tipwindow.lift()

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

"""
def activate_all_tooltips():
    for tooltip in tooltips:
        tooltip.schedule()


def deactivate_all_tooltips():
    for tooltip in tooltips:
        tooltip.unschedule()


def create_tooltip(widget, text: str, font_size: int = 100):
    hovertip = Hovertip(widget, text, font_size)
    #hovertip.schedule()
    tooltips.append(hovertip)
"""