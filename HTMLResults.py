import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import ApplicationProperties
from ResultsFilter import FilterTreeview
import tkinter as tk
from dbcommands_rewrite import DBGetter


class HTMLResults(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.results = None

        self.btn_results = tk.Button(
            self,
            text="Rezultati",
            command=lambda: self._get_results()
        )

        self.btn_save_to_html = tk.Button(
            self,
            text="Spremi kao html",
            command=lambda: self._convert_and_save_as_html(ApplicationProperties.LOCATION + "/test.html")
        )

        self.btn_save_as_pdf = tk.Button(
            self,
            text="Spremi kao PDF",
            command=lambda: self._save_as_pdf()
        )

        self.btn_results.grid(row=0, column=0)
        self.btn_save_to_html.grid(row=1, column=0)
        self.btn_save_as_pdf.grid(row=2, column=0)

    def _convert_and_save_as_html(self, filename: str):
        if not self.results:
            return
        df = pd.DataFrame(data=self.results)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(df.to_html())

    def _get_results(self):
        r_filter = FilterTreeview(self)
        r_filter.wait_window()

        if r_filter.user_closed:
            return

        self.results = DBGetter.get_results(
            date_from=r_filter.date["from"],
            date_to=r_filter.date["to"],
            shooter_ids=[value for key, value in
                         r_filter.active_shooters.items()] if r_filter.active_shooters else None,
            competition_ids=[value for key, value in
                             r_filter.active_competitions.items()] if r_filter.active_competitions else None,
            programs=[value for key, value in
                      r_filter.active_programs.items()] if r_filter.active_programs else None,
            targets=[value for key, value in r_filter.active_targets.items()] if r_filter.active_targets else None,
            disciplines=[value for key, value in
                         r_filter.active_disciplines.items()] if r_filter.active_disciplines else None
        )
        self._clean_results()

    def _save_as_pdf(self):
        df = pd.DataFrame(self.results)
        self.dataframe_to_pdf(df, ApplicationProperties.LOCATION + "/OUT1.pdf", (20, 1))

    def _clean_results(self):
        keys_to_remove = ["Ime", "Prezime", "id"]
        for result in self.results:
            for key in keys_to_remove:
                result.pop(key)

    def _draw_as_table(self, df, pagesize):
        alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
        alternating_colors = alternating_colors[:len(df)]
        fig, ax = plt.subplots(figsize=pagesize)
        ax.axis('tight')
        ax.axis('off')
        the_table = ax.table(cellText=df.values,
                             rowLabels=df.index,
                             colLabels=df.columns,
                             rowColours=['lightblue'] * len(df),
                             colColours=['lightblue'] * len(df.columns),
                             cellColours=alternating_colors,
                             loc='center')
        return fig

    def dataframe_to_pdf(self, df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
        with PdfPages(filename) as pdf:
            nh, nv = numpages
            rows_per_page = len(df) // nh
            cols_per_page = len(df.columns) // nv
            for i in range(0, nh):
                for j in range(0, nv):
                    page = df.iloc[(i * rows_per_page):min((i + 1) * rows_per_page, len(df)),
                           (j * cols_per_page):min((j + 1) * cols_per_page, len(df.columns))]
                    fig = self._draw_as_table(page, pagesize)
                    if nh > 1 or nv > 1:
                        # Add a part/page number at bottom-center of page
                        fig.text(0.5, 0.5 / pagesize[0],
                                 "Part-{}x{}: Page-{}".format(i + 1, j + 1, i * nv + j + 1),
                                 ha='center', fontsize=8)
                    pdf.savefig(fig, bbox_inches='tight')

                    plt.close()


class HTMLResultsToplevel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        htmlresults = HTMLResults(self)

        htmlresults.pack(expand=True, fill="both")
