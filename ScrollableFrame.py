import tkinter
import tkinter as tk
from typing import Any


class Vertical(tk.Frame):
    def __init__(self, container: Any, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.container = container
        self.canvas_width = self.canvas.winfo_width()
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.__adjust_frame_in_canvas)
        self.canvas.bind_all("<FocusIn>", self._scroll_into_view)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __mousewheel_action(self, event):
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def __canvas_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __ignore(self, event):
        pass

    def __adjust_frame_in_canvas(self, event):
        self.bind("<Configure>", self.__ignore)
        try:
            current_canvas_width = self.canvas.winfo_width()
            if current_canvas_width != self.canvas_width:
                self.canvas_width = current_canvas_width
                self.canvas.itemconfig("frame", width=self.canvas_width)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except:
            pass
        finally:
            self.bind("<Configure>", self.__adjust_frame_in_canvas)

    def _scroll_into_view(self, event):
        try:
            if issubclass(event.widget.__class__, tkinter.Toplevel) or issubclass(event.widget.__class__, tkinter.Frame):
                return
        except AttributeError:
            return
        print(event.widget.__class__.__name__, str(event.widget.__class__.__base__))
        try:
            widget_top = event.widget.winfo_rooty()
            widget_bottom = widget_top + event.widget.winfo_height()
            canvas_top = self.canvas.winfo_rooty()
            canvas_bottom = canvas_top + self.winfo_height()
        except AttributeError:
            return

        if widget_bottom > canvas_bottom:
            delta = int(canvas_bottom - widget_bottom) // 10
            self.canvas.yview_scroll(-delta, "units")
        elif widget_top < canvas_top:
            delta = int(widget_top - canvas_top) // 10
            self.canvas.yview_scroll(delta, "units")


class HorizontalAndVertical(tk.Frame):
    def __init__(self, container: Any, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = container
        self.configure(bd=0)
        self.canvas = tk.Canvas(self, bd=0)
        self.container = container
        self.scrollbar_vertical = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_horizontal = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, bd=0)
        self.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")

        self.canvas.configure(yscrollcommand=self.scrollbar_vertical.set)
        self.canvas.configure(xscrollcommand=self.scrollbar_horizontal.set)

        self.scrollbar_vertical.pack(side="right", fill="y")
        self.scrollbar_horizontal.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.__adjust_frame_in_canvas()
        self.scrollable_frame.bind("<Configure>", self.__adjust_frame_in_canvas)
        self.bind("<Configure>", self.__adjust_frame_in_canvas)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __mousewheel_action(self, event):
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def __canvas_scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __ignore(self, event):
        pass

    def __adjust_frame_in_canvas(self, event=None):
        self.bind("<Configure>", self.__ignore)
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except:
            pass
        finally:
            self.bind("<Configure>", self.__adjust_frame_in_canvas)


class Horizontal(tk.Frame):
    def __init__(self, container: Any, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = container
        self.configure(bd=0)
        self.canvas = tk.Canvas(self, bd=0)
        self.container = container
        self.scrollbar_vertical = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_horizontal = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, bd=0, bg="yellow")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")

        self.canvas.configure(xscrollcommand=self.scrollbar_horizontal.set)

        self.scrollbar_horizontal.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.__adjust_frame_in_canvas)

        self.__adjust_frame_in_canvas(None)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __mousewheel_action(self, event):
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def __canvas_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __adjust_frame_in_canvas(self, event):
        self.canvas.itemconfig("frame", height=self.canvas.winfo_height())
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_idletasks()
