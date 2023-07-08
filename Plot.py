import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib as mpl
from matplotlib import cbook
from matplotlib.backend_bases import _safe_pyplot_import
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import mplcursors
from matplotlib import dates as mpl_dates

from contextlib import ExitStack

import Fonts
import ScrollableFrame
from matplotlib.figure import Figure
import matplotlib.widgets as widgets
import ResultsFilter
import Tools
from dbcommands_rewrite import DBGetter

from tkinter import messagebox


class PlotResults2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.x = 800
        self.y = 450
        self.graph_horizontal_expanded = False
        self.graph_vertical_expanded = False

        self.pan_vertical = ttk.PanedWindow(self, orient=tk.VERTICAL)

        self.pan_horizontal = ttk.PanedWindow(self.pan_vertical, orient=tk.HORIZONTAL)

        self.style = ttk.Style()
        self.style.configure("Plot.TNotebook.Tab")
        # self.style.layout('Plot.TNotebook.Tab', [])  # turn off tabs

        self.frame_top = tk.Frame(self)
        self.frame_bottom = tk.Frame(self)

        self.notebook_statistics = ttk.Notebook(self.pan_horizontal, style="Plot.TNotebook")
        self.notebook_graphs = ttk.Notebook(self.pan_horizontal, style="Plot.TNotebook")

        self.frame_other = tk.Frame(self.pan_vertical)
        self.frame_controls = PlotResultsControls(self.frame_other)
        self.graph_control = GraphControls(self.frame_other)

        self.frame_other.grid_propagate(False)
        self.frame_other.columnconfigure(0, weight=5, uniform="cols")
        self.frame_other.columnconfigure(1, weight=1, uniform="cols")
        self.frame_other.rowconfigure(0, weight=1)

        self.frame_controls.grid(column=0, row=0, sticky="nsew")
        self.graph_control.grid(column=1, row=0, sticky="nsew")

        self.manipulator = GraphManipulator(self, self.notebook_graphs,
                                            self.notebook_statistics, self.graph_control, self.frame_controls)

        self.notebook_frames = []
        self.notebook_statistics_frames = []

        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=30, uniform="plot2_rows")
        self.grid_rowconfigure(1, weight=1, uniform="plot2_rows")
        self.grid_rowconfigure(2, weight=9, uniform="plot2_rows")
        self.grid_rowconfigure(3, weight=1, uniform="plot2_rows")

        self.frame_top.grid_rowconfigure(0, weight=1)
        self.frame_top.grid_columnconfigure(0, weight=1, uniform="top_column")
        self.frame_top.grid_columnconfigure(1, weight=10, uniform="top_column")
        self.frame_top.grid_columnconfigure(2, weight=33, uniform="top_column")

        self.frame_bottom.pack_propagate(False)

        self.pan_horizontal.add(self.notebook_statistics, weight=2)
        self.pan_horizontal.add(self.notebook_graphs, weight=10)

        self.pan_vertical.add(self.pan_horizontal, weight=3)
        self.pan_vertical.add(self.frame_other, weight=1)

        self.pan_vertical.pack(expand=True, fill="both")

    def delete_graph_at_index(self, index):
        self.notebook_graphs.forget(self.notebook_frames[index])
        self.notebook_statistics.forget(self.notebook_statistics_frames[index])
        del self.notebook_frames[index]
        del self.notebook_statistics_frames[index]


class StatisticsFrame(ScrollableFrame.HorizontalAndVertical):
    # ukupno ispaljeno probe
    # najbolji rezultat (na datum)
    # ukupno sesija ispaljeno
    # prosjek
    # za svaku disciplinu posebno navesti statistiku
    # za svaki program posebno navesti statistiku (kartezijev produkt)
    def __init__(self, parent):
        ScrollableFrame.HorizontalAndVertical.__init__(self, parent)
        self.font_title = Fonts.fonts2["StatisticsFrame"]["title"]["font"]
        self.font_info = Fonts.fonts2["StatisticsFrame"]["sub_title"]["font"]
        self.title_lbls = []
        self.info_lbls = []

    def set_title(self, title, anchor="center", color="gray40"):
        lbl = tk.Label(
            self.scrollable_frame,
            text=title,
            anchor=anchor,
            font=self.font_title,
            bg=color
        )
        self.title_lbls.append(lbl)
        self.title_lbls[-1].pack(side="top", fill="x")

    def set_info(self, info, anchor="center", color="gray40"):
        lbl = tk.Label(
            self.scrollable_frame,
            text=info,
            anchor=anchor,
            font=self.font_info,
            bg=color
        )
        self.info_lbls.append(lbl)
        self.info_lbls[-1].pack(side="top", fill="x")


class PlotResultsControls(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.font = Fonts.fonts2["PlotResultsControls"]["buttons"]["font"]

        self.grid_propagate(False)
        for x in range(0, 10, 1):
            self.grid_columnconfigure(x, weight=1, uniform="contorls2_cols")
        for y in range(0, 10, 1):
            self.grid_rowconfigure(y, weight=1, uniform="controls2_rows")

        self.lbx_frame = tk.Frame(self)
        self.lbx_frame.pack_propagate(False)

        self.lbx_configurations = tk.Listbox(
            self.lbx_frame,
            selectmode="single",
            font=self.font
        )

        self.scr_lbx_configuration_vertical = tk.Scrollbar(
            self.lbx_frame,
            orient="vertical",
            command=self.lbx_configurations.yview
        )
        self.lbx_configurations.configure(yscrollcommand=self.scr_lbx_configuration_vertical.set)

        self.scr_lbx_configuration_horizontal = tk.Scrollbar(
            self.lbx_frame,
            orient="horizontal",
            command=self.lbx_configurations.xview
        )
        self.lbx_configurations.configure(xscrollcommand=self.scr_lbx_configuration_horizontal.set)

        self.btn_add_new_configuration = tk.Button(
            self,
            text="Dodaj",
            bg="lime",
            fg="black",
            font=self.font
        )

        self.btn_remove_configuration = tk.Button(
            self,
            text="Ukloni",
            bg="red",
            fg="black",
            font=self.font
        )

        self.btn_show_configuration = tk.Button(
            self,
            text="Prikaži",
            bg="yellow",
            fg="black",
            font=self.font
        )

        self.lbx_frame.grid(row=0, rowspan=10, column=1, columnspan=6, sticky="nsew")

        self.scr_lbx_configuration_horizontal.pack(side="bottom", fill="x")
        self.scr_lbx_configuration_vertical.pack(side="right", fill="y")
        self.lbx_configurations.pack(side="right", expand=True, fill="both")

        self.btn_add_new_configuration.grid(row=0, rowspan=2, column=0, sticky="nsew")
        self.btn_show_configuration.grid(row=2, rowspan=2, column=0, sticky="nsew")
        self.btn_remove_configuration.grid(row=4, rowspan=2, column=0, sticky="nsew")
        
    def set_commands(self, add_func, delete_func, show_func):
        self.btn_add_new_configuration.configure(command=add_func)
        self.btn_remove_configuration.configure(command=delete_func)
        self.btn_show_configuration.configure(command=show_func)

    def add_item_to_listbox(self, item):
        self.lbx_configurations.insert(tk.END, item)
        if self.lbx_configurations.size() == 1:
            self.lbx_configurations.itemconfig(0, bg="yellow")

    def get_current_selection(self):
        return self.lbx_configurations.curselection()[0]

    def color_listbox_item_at_index(self, index: int, color: str = "yellow"):
        self.lbx_configurations.itemconfig(index, bg=color)

    def color_all_listbox_items(self, color: str = "white"):
        for index in range(0, self.lbx_configurations.size(), 1):
            self.lbx_configurations.itemconfig(index, bg=color)

    def remove_listbox_item_at_index(self, index: int):
        self.lbx_configurations.delete(index)


class Graph(tk.Frame):
    def __init__(self, parent, controller, dates, results, title):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.title = title
        self.dates = dates
        self.dates_list = list(map(datetime.datetime.strptime, self.dates, len(self.dates)*["%Y-%m-%d"]))
        self.formatter = mpl_dates.DateFormatter("%d.%m.%Y.")
        self.results = results
        self.actives = []
        self.step_dots = False
        self.bar_dots = False
        self.plot_dots = False
        self.plot_active = False
        self.step_active = False
        self.bar_active = False
        self.dots = None
        self.dots_active = False
        self.pack_propagate(False)

        self.figure = Figure(dpi=200)
        self.figure.autofmt_xdate(rotation=25)

        self.xy = self.figure.add_subset_style_plot(111, title=self.title)
        self.xy.xaxis.set_major_formatter(self.formatter)

        self.graph = FigureCanvasTkAgg(self.figure, master=self)
        self.toolbar = NavigationToolbar2TkHR(self.graph, self)
        self.toolbar.update()
        self.graph.get_tk_widget().pack(expand=True, fill="both")
        self.set_style_plot()

    @staticmethod
    def adjust_plot_font(x):
        mpl.rcParams.update({"font.size": int(x/150)})

    def set_style_plot(self):
        if self.plot_active:
            return
        self.clear_plot()
        self.lines, = self.xy.plot(self.dates_list, self.results, "-",  color="blue")

        self.actives.append(self.lines)
        self.figure.autofmt_xdate()

        self.graph.draw_idle()
        self.toolbar.update()
        self.bar_active = False
        self.step_active = False
        self.plot_active = True

    def trigger_dots(self):
        if self.dots_active:
            self._remove_dots()
            self.dots_active = False
        else:
            self._show_dots()
            self.dots_active = True

    def _show_dots(self):
        self.dots = self.xy.scatter(self.dates_list, self.results, color="blue")
        self.graph.draw_idle()
        mplcursors.cursor(self.dots)

    def _remove_dots(self):
        try:
            self.dots.remove()
            self.graph.draw_idle()
        except AttributeError:
            pass
        finally:
            self.dots = None

    def set_style_bar(self):
        if self.bar_active:
            return
        self.clear_plot()
        self.bar = self.xy.bar(self.dates_list, self.results, color="blue")
        self.actives.append(self.bar)

        self.graph.draw_idle()
        self.toolbar.update()
        self.bar_active = True
        self.step_active = False
        self.plot_active = False

    def set_style_step(self):
        if self.step_active:
            return
        self.clear_plot()
        self.step, = self.xy.step(self.dates_list, self.results, color="blue")
        self.actives.append(self.step)
        self.graph.draw_idle()

        self.toolbar.update()
        self.bar_active = False
        self.step_active = True
        self.plot_active = False

    def clear_plot(self):
        if not self.actives:
            return
        for active in self.actives:
            active.remove()
        self.actives = []


class GraphControls(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.graph: Graph = None

        self.font = Fonts.fonts2["PlotResultsControls"]["buttons"]["font"]

        for y in range(0, 4, 1):
            self.rowconfigure(y, weight=1)
        self.columnconfigure(0, weight=1)

        self.btn_bar_graph = tk.Button(
            self,
            text="Stupčasti",
            font=self.font,
            bd=4,
            command=lambda: self._set_graph_set_style_bar()
        )

        self.btn_plot_graph = tk.Button(
            self,
            text="Linijski",
            font=self.font,
            bd=4,
            command=lambda: self._set_graph_set_style_plot()
        )

        self.btn_step_graph = tk.Button(
            self,
            text="Koračni",
            font=self.font,
            bd=4,
            command=lambda: self._set_graph_set_style_step()
        )

        self.btn_dots_graph = tk.Button(
            self,
            text="Točke",
            font=self.font,
            bd=4,
            command=lambda: self._set_graph_trigger_dots()
        )

        self.btn_bar_graph.grid(row=0, column=0, sticky="nsew")
        self.btn_plot_graph.grid(row=1, column=0, sticky="nsew")
        self.btn_step_graph.grid(row=2, column=0, sticky="nsew")
        self.btn_dots_graph.grid(row=3, column=0, sticky="nsew")

    def set_graph(self, graph: Graph):
        self.graph = graph

    def _set_graph_trigger_dots(self):
        self.graph.trigger_dots()

    def _set_graph_set_style_bar(self):
        self.graph.set_style_bar()

    def _set_graph_set_style_plot(self):
        self.graph.set_style_plot()

    def _set_graph_set_style_step(self):
        self.graph.set_style_step()


class GraphManipulator(tk.Frame):
    def __init__(self, parent, graph_notebook: ttk.Notebook, statistics_notebook: ttk.Notebook,
                 graph_control: GraphControls, data_control: PlotResultsControls):
        super().__init__(parent)

        self.previously_selected_listbox_item_index = 0

        self.graph_notebook = graph_notebook
        self.graph_control = graph_control
        self.data_control = data_control

        self.statistics_notebook = statistics_notebook

        self.data_control.set_commands(
            add_func=self.add_configuration,
            show_func=self.show_graph,
            delete_func=self._delete_selected_configuration
        )

        self.graph_notebook.bind("<<NotebookTabChanged>>", self._notebook_graphs_tab_selected)

    def _delete_selected_configuration(self):
        index = self.data_control.get_current_selection()
        if index < 0:
            return
        for tab in self.graph_notebook.tabs():
            if self.graph_notebook.tab(tab)["text"] == str(index):
                self.graph_notebook.forget(tab)
                self.graph_notebook.nametowidget(tab).destroy()
        self.data_control.remove_listbox_item_at_index(index)
        self._rename_graph_notebook_tabs()
        self._rename_statistics_notebook_tabs()

    def show_graph(self):
        # color selected listbox item
        index = self.data_control.get_current_selection()
        if index != self.previously_selected_listbox_item_index:
            self.graph_notebook.select(self.graph_notebook.tabs()[index])
            self.data_control.color_listbox_item_at_index(index)
            self.data_control.color_listbox_item_at_index(self.previously_selected_listbox_item_index, "white")
            self.previously_selected_listbox_item_index = index

    @classmethod
    def get_results_on_dates(cls, shooter_id, date_from, date_to, programs, disciplines, targets, competitions):
        """(results: [float], dates: [str 'yyyy-mm-dd'])"""
        values = DBGetter.get_results(
            date_from=date_from,
            date_to=date_to,
            shooter_ids=[shooter_id],
            programs=programs,
            competition_ids=competitions,
            targets=targets,
            disciplines=disciplines
        )
        results = []
        dates = []
        for result in values:
            results.append(result["Rezultat"])
            dates.append(result["Datum"])
        return dates, results

    def add_configuration(self):
        r_filter = ResultsFilter.FilterTreeview(self, True)
        r_filter.focus()
        r_filter.wait_window()

        try:
            shooter_id = next(iter(r_filter.active_shooters.values()))
        except StopIteration:
            return

        program_ids = [int(value) for key, value in r_filter.active_programs.items()]
        if not program_ids:
            program_ids = [program['id'] for program in DBGetter.get_distinct_shooter_programs(shooter_id)]

        target_ids = [int(value) for key, value in r_filter.active_targets.items()]
        if not target_ids:
            target_ids = [target['id'] for target in DBGetter.get_distinct_shooter_targets(shooter_id)]

        discipline_ids = [int(value) for key, value in r_filter.active_disciplines.items()]
        if not discipline_ids:
            discipline_ids = [discipline['id'] for discipline in DBGetter.get_distinct_shooter_disciplines(shooter_id)]

        competition_ids = [value for key, value in r_filter.active_competitions.items()]

        shooter = DBGetter.get_shooter_basic_info(shooter_id)
        shooter_name = f"{shooter['Ime']} {shooter['Prezime']}"

        dates, results = self.get_results_on_dates(
            shooter_id=shooter_id,
            date_from=r_filter.date["from"],
            date_to=r_filter.date["to"],
            programs=program_ids,
            targets=target_ids,
            competitions=competition_ids,
            disciplines=discipline_ids
        )

        if not dates or not results:
            messagebox.showinfo(title="Rezultati", message="Nema rezultata za prikaz.")
            return

        starting_date = Tools.SQL_date_format_to_croatian(dates[0])
        final_date = Tools.SQL_date_format_to_croatian(dates[-1])

        new_statistics_frame = StatisticsFrame(self.statistics_notebook)

        for program_id in program_ids:
            row_color = False
            new_statistics_frame.set_title(
                DBGetter.get_program_details(program_id)["Naziv"] + ":", anchor="w", color="gray50"
            )
            for discipline_id in discipline_ids:
                new_statistics_frame.set_title(
                    " " * 8 + DBGetter.get_discipline_details(discipline_id)['Naziv'], anchor="w", color="gray60"
                )
                for target_id in target_ids:
                    row_color = not row_color
                    max_result = DBGetter.get_shooter_best_result(
                        shooter_id=shooter_id,
                        target_ids=[target_id],
                        discipline_ids=[discipline_id],
                        program_ids=[program_id]
                    )
                    if not max_result:
                        continue  # result is None
                    if row_color:
                        info_color = "gray70"
                    else:
                        info_color = "gray75"
                    new_statistics_frame.set_info(
                        DBGetter.get_target_details(
                            target_id)['Naziv'] + ":" + " " + str(
                            max_result['Rezultat']) + " (" + Tools.SQL_date_format_to_croatian(max_result['Datum']),
                        anchor="w",
                        color=info_color
                    )

        title = shooter_name + " (" + starting_date + " - " + final_date + ")" + "\n " + ", ".join(
            [DBGetter.get_program_details(program_id)['Naziv'] for program_id in program_ids]) \
                + ", " + ", ".join(
            [DBGetter.get_discipline_details(discipline_id)['Naziv'] for discipline_id in discipline_ids]) \
                + ", " + ", ".join([DBGetter.get_target_details(target_id)['Naziv'] for target_id in target_ids])

        graph = Graph(self.graph_notebook, self, dates, results, title)
        self.data_control.add_item_to_listbox(title)
        self.graph_notebook.add(graph)
        self.statistics_notebook.add(new_statistics_frame)
        
        self._rename_graph_notebook_tabs()
        self._rename_statistics_notebook_tabs()

    def _rename_graph_notebook_tabs(self):
        for i, tab in enumerate(self.graph_notebook.tabs()):
            self.graph_notebook.tab(tab, text=str(i))
            
    def _rename_statistics_notebook_tabs(self):
        for i, tab in enumerate(self.statistics_notebook.tabs()):
            self.statistics_notebook.tab(tab, text=str(i))

    def _notebook_graphs_tab_selected(self, event):
        # change statistics as well
        selected_tab_index = self.graph_notebook.index(self.graph_notebook.select())
        self.statistics_notebook.select(selected_tab_index)
        # set controls to new graph
        self.graph_control.set_graph(
            self.graph_notebook.nametowidget(self.graph_notebook.select())
        )
        self.data_control.color_all_listbox_items()
        self.data_control.color_listbox_item_at_index(selected_tab_index)


class NavigationToolbar2TkHR(NavigationToolbar2Tk):
    # only display the buttons we need
    NavigationToolbar2Tk.toolitems = (
        ('Home', 'Vrati prvotni izgled', 'home', 'home'),
        # ('Back', 'Back to previous view', 'back', 'back'),
        # ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan',
         'Lijevi gumb pomiče, desni povećava/smanjuje',
         'move', 'pan'),
        # ('Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Uredi prikaz', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Spremi prikaz', 'filesave', 'save_figure'),
    )

    def configure_subplots(self, *args):
        if hasattr(self, "subplot_tool"):
            self.subplot_tool.figure.canvas.manager.show()
            return
        plt = _safe_pyplot_import()
        with mpl.rc_context({"toolbar": "none"}):  # No navbar for the toolfig
            # Use new_figure_manager() instead of figure() so that the figure
            # doesn't get registered with pyplot.
            manager = plt.new_figure_manager(-1, (6, 3))
        manager.set_window_title("Postavke prikaza")
        tool_fig = manager.canvas.figure
        tool_fig.subplots_adjust(top=0.9)
        self.subplot_tool = SubplotToolHR(self.canvas.figure, tool_fig)
        tool_fig.canvas.mpl_connect(
            "close_event", lambda e: delattr(self, "subplot_tool"))
        self.canvas.mpl_connect(
            "close_event", lambda e: manager.destroy())
        manager.show()
        return self.subplot_tool
    """
    NavigationToolbar2Tk.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan',
         'Left button pans, Right button zooms\n'
         'x/y fixes axis, CTRL fixes aspect',
         'move', 'pan'),
        ('Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )"""

#class SubplotToolHR(widgets.SubplotTool):
#    widgets.SubplotTool.names = ["lijevo", "dolje", "desno", "gore", "wspace", "hspace"]


class SubplotToolHR(widgets.Widget):
    """
    A tool to adjust the subplot params of a `matplotlib.figure.Figure`.
    """

    def __init__(self, targetfig, toolfig):
        """
        Parameters
        ----------
        targetfig : `.Figure`
            The figure instance to adjust.
        toolfig : `.Figure`
            The figure instance to embed the subplot tool into.
        """

        self.figure = toolfig
        self.targetfig = targetfig
        toolfig.subplots_adjust(left=0.2, right=0.9)
        toolfig.suptitle("Koristite klizače za namještanje prikaza sadržaja grafa")
        # toolfig.suptitle("Click on slider to adjust subplot param")
        self._sliders = []
        self.names_hr = ["lijevo", "dolje", "desno", "gore", "wspace", "hspace"]
        self.names = ["left", "bottom", "right", "top", "wspace", "hspace"]
        # The last subplot, removed below, keeps space for the "Reset" button.
        i = 0
        for name, ax in zip(self.names, toolfig.subplots(len(self.names) + 1)):
            ax.set_navigate(False)
            slider = widgets.Slider(ax, self.names_hr[i],
                            0, 1, getattr(targetfig.subplotpars, name))
            slider.on_changed(self._on_slider_changed)
            self._sliders.append(slider)
            i += 1
        toolfig.axes[-1].remove()
        (self.sliderleft, self.sliderbottom, self.sliderright, self.slidertop,
         self.sliderwspace, self.sliderhspace) = self._sliders
        for slider in [self.sliderleft, self.sliderbottom,
                       self.sliderwspace, self.sliderhspace]:
            slider.closedmax = False
        for slider in [self.sliderright, self.slidertop]:
            slider.closedmin = False

        # constraints
        self.sliderleft.slidermax = self.sliderright
        self.sliderright.slidermin = self.sliderleft
        self.sliderbottom.slidermax = self.slidertop
        self.slidertop.slidermin = self.sliderbottom

        bax = toolfig.add_axes([0.8, 0.05, 0.15, 0.075])
        self.buttonreset = widgets.Button(bax, 'Reset')
        self.buttonreset.on_clicked(self._on_reset)

    def _on_slider_changed(self, _):
        self.targetfig.subplots_adjust(
            **{self.names[i]: slider.val
               for i, slider in enumerate(self._sliders)})
        if self.drawon:
            self.targetfig.canvas.draw()

    def _on_reset(self, event):
        with ExitStack() as stack:
            # Temporarily disable drawing on self and self's sliders, and
            # disconnect slider events (as the subplotparams can be temporarily
            # invalid, depending on the order in which they are restored).
            stack.enter_context(cbook._setattr_cm(self, drawon=False))
            for slider in self._sliders:
                stack.enter_context(
                    cbook._setattr_cm(slider, drawon=False, eventson=False))
            # Reset the slider to the initial position.
            for slider in self._sliders:
                slider.reset()
        if self.drawon:
            event.canvas.draw()  # Redraw the subplottool canvas.
        self._on_slider_changed(None)  # Apply changes to the target window.
