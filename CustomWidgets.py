import tkinter as tk
from tkinter import ttk

import tkcalendar

import Tools
from tkcalendar import Calendar


class MenuTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        ttk.Treeview.__init__(self, *args, **kwargs)
        self.menu = None
        self.bind("<Button-3>", self.right_click)
        self.style = ttk.Style()
        self.style.configure("Treeview")
        if tk.Tcl().eval('info patchlevel') == '8.6.9':
            self.style.map("Treeview", foreground=Tools.fixed_map(self.style, "Treeview", 'foreground'),
                            background=Tools.fixed_map(self.style, "Treeview", 'background'))

    def show_menu(self, event):
        if self.menu is not None:
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def assign_menu(self, menu: tk.Menu):
        self.menu = menu

    def right_click(self, event):
        rowID = self.identify_row(event.y)
        if rowID:
            self.selection_set(rowID)
            self.focus(rowID)
            self.show_menu(event)


class CustomBox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        #   initialisation of the combobox entry
        super().__init__(*args, **kwargs)
        #   "initialisation" of the combobox popdown
        self._handle_popdown_font()

    def _handle_popdown_font(self):
        """ Handle popdown font
        Note: https://github.com/nomad-software/tcltk/blob/master/dist/library/ttk/combobox.tcl#L270
        """
        #   grab (create a new one or get existing) popdown
        popdown = self.tk.eval('ttk::combobox::PopdownWindow %s' % self)
        #   configure popdown font
        self.tk.call('%s.f.l' % popdown, 'configure', '-font', self['font'])

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget. Overridden!

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """

        #   default configure behavior
        self._configure('configure', cnf, kw)
        #   if font was configured - configure font for popdown as well
        try:  # without try, it can fail if either kw or cnf is None - TypeError
            if 'font' in kw or 'font' in cnf:
                self._handle_popdown_font()
        except TypeError:
            pass

    #   keep overridden shortcut
    config = configure


class tkcalnder_CalendarMonthYearEntry(Calendar):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self._header_year.pack_forget()
        self._header_year = ttk.Entry(self._header_year.master, width=4, style='main.%s.TLabel' % self._style_prefixe,
                                      font=self._header_font)
        self._header_year.bind("<Return>", self._set_year_from_entry)

        self._l_10_year = ttk.Button(self._l_year.master,
                                   style='L.%s.TButton' % self._style_prefixe,
                                   command=self._prev_10_year)
        self._r_10_year = self._r_10_year = ttk.Button(self._r_year.master,
                                   style='R.%s.TButton' % self._style_prefixe,
                                   command=self._next_10_year)

        self._l_year.pack_forget()
        self._r_year.pack_forget()

        self._l_10_year.pack(side="left", fill="y")
        self._l_year.pack(side="left", fill="y")

        self._header_year.pack(side='left', padx=4)

        self._r_year.pack(side="left", fill="y")
        self._r_10_year.pack(side="left", fill="y")

        self._display_calendar()

    def _set_year_from_entry(self, event):
        self._date = self._date.replace(year=int(self._header_year.get()))
        self._display_calendar()

    def _next_10_year(self):
        """Display the next year."""
        year = self._date.year
        self._date = self._date.replace(year=year + 10)
        self._display_calendar()
        self.event_generate('<<CalendarMonthChanged>>')
        self._btns_date_range()

    def _prev_10_year(self):
        """Display the previous year."""
        year = self._date.year
        self._date = self._date.replace(year=year - 10)
        self._display_calendar()
        self.event_generate('<<CalendarMonthChanged>>')
        self._btns_date_range()

    def _display_calendar(self):
        """Display the days of the current month (the one in self._date)."""
        year, month = self._date.year, self._date.month

        # update header text (Month, Year)
        header = self._month_names[month]
        self._header_month.configure(text=header.title())
        try:
            self._header_year.delete(0, tk.END)
            self._header_year.insert(0, str(year))
        except AttributeError:
            return

        # remove previous tooltips
        self.tooltip_wrapper.remove_all()

        # update calendar shown dates
        if self['showothermonthdays']:
            self._display_days_with_othermonthdays()
        else:
            self._display_days_without_othermonthdays()

        self._display_selection()
        maxdate = self['maxdate']
        mindate = self['mindate']

        if maxdate is not None:
            mi, mj = self._get_day_coords(maxdate)
            if mi is not None:
                for j in range(mj + 1, 7):
                    self._calendar[mi][j].state(['disabled'])
                for i in range(mi + 1, 6):
                    for j in range(7):
                        self._calendar[i][j].state(['disabled'])

        if mindate is not None:
            mi, mj = self._get_day_coords(mindate)
            if mi is not None:
                for j in range(mj):
                    self._calendar[mi][j].state(['disabled'])
                for i in range(mi):
                    for j in range(7):
                        self._calendar[i][j].state(['disabled'])


class DateEntry2(tkcalendar.DateEntry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        kw.pop("state", None)
        self._calendar.pack_forget()
        self._calendar = tkcalnder_CalendarMonthYearEntry(self._top_cal, **kw)
        self._calendar.pack()

        self._calendar.bind('<<CalendarSelected>>', self._select)
        # hide calendar if it looses focus
        self._calendar.bind('<FocusOut>', self._on_focus_out_cal)
