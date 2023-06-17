import datetime

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import ApplicationProperties
import Tools
from ResultsFilter import FilterTreeview
import tkinter as tk
from dbcommands_rewrite import DBGetter
from matplotlib import dates as mpl_dates


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
        #pdfkit.from_file(ApplicationProperties.LOCATION + "/test.html")
        df = pd.DataFrame(self.results)
        self.dataframe_to_pdf(df, ApplicationProperties.LOCATION + "/OUT1.pdf", 20)

    def _clean_results(self):
        keys_to_remove = ["Ime", "Prezime", "id", "Napomena"]
        for result in self.results:
            for key in keys_to_remove:
                result.pop(key)

    def _draw_as_table(self, df: pd.DataFrame, pagesize):
        alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
        alternating_colors = alternating_colors[:len(df)]
        fig, ax = plt.subplots(figsize=pagesize)
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(
            cellText=df.values,
            rowLabels=df.index + 1,
            colLabels=df.columns,
            rowColours=['lightblue'] * len(df),
            colColours=['lightblue'] * len(df.columns),
            cellColours=alternating_colors,
            loc='center',
            cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.3)
        table.auto_set_column_width(col=list(range(len(df.columns)))) # Provide integer list of columns to adjust
        return fig

    def _save_results_to_file(self, pdfpages: PdfPages, start_index: int, stop_index: int, rows_per_page: int = 25, pagesize=(8.3, 11.7)):
        for i in range(0, (stop_index - start_index) // rows_per_page + 1, 1):
            # print(start_index, stop_index)
            # print(self.results[start_index + (i * rows_per_page)
            #                    :
            #                    stop_index if stop_index < start_index + ((i+1) * rows_per_page) else start_index + ((i+1) * rows_per_page)
            #                     ]
            # )
            pdfpages.savefig(
                self._draw_as_table(
                    pd.DataFrame(
                        self.results[start_index + (i * rows_per_page)
                                     :
                                     stop_index if stop_index < start_index + ((i+1) * rows_per_page) else start_index + ((i+1) * rows_per_page)
                                    ]
                    ), pagesize
                ), bbox_inches='tight'
            )

    def _save_plot_to_file(self, file: PdfPages, dates, results, title: str = "", pagesize=(11.7, 8.3)):
        dates_list = list(map(datetime.datetime.strptime, dates, len(dates) * ["%Y-%m-%d"]))
        formatter = mpl_dates.DateFormatter("%d.%m.%Y.")

        fig = plt.Figure(figsize=pagesize)
        fig.autofmt_xdate(rotation=25)

        xy = fig.add_subplot(111, title=title)
        xy.xaxis.set_major_formatter(formatter)

        xy.plot(dates_list, results, "-", color="blue")

        fig.autofmt_xdate()

        file.savefig(fig, bbox_inches='tight')

    def get_results_to_dates(self, start_index: int, stop_index: int):
        r, d = [], []
        for result in self.results[start_index:stop_index]:
            r.append(result['Rezultat'])
            d.append(result['Datum'])
        return r, d

    def dataframe_to_pdf(self, df, filename, rows_per_page: int = 30, pagesize=(8.3, 11.7)):
        file = PdfPages(filename)
        month_for_extraction = Tools.SQL_date_to_datetime_date(self.results[0]['Datum']).month
        year_for_extraction = Tools.SQL_date_to_datetime_date(self.results[0]['Datum']).year
        start_index_month = 0
        start_index_year = 0
        for i, result in enumerate(self.results):
            if Tools.SQL_date_to_datetime_date(result['Datum']).month != month_for_extraction:
                r, d = self.get_results_to_dates(start_index_month, i)
                self._save_plot_to_file(
                    file=file,
                    results=r,
                    dates=d,
                    title=f"{self.results[0]['Strijelac']} - {month_for_extraction}. mjesec {Tools.SQL_date_to_datetime_date(self.results[start_index_month]['Datum']).year}."
                )

                self._save_results_to_file(
                    pdfpages=file,
                    start_index=start_index_month,
                    stop_index=i
                )

                month_for_extraction = Tools.SQL_date_to_datetime_date(result['Datum']).month
                start_index_month = i

            if Tools.SQL_date_to_datetime_date(result['Datum']).year != year_for_extraction:
                r, d = self.get_results_to_dates(start_index_year, i)
                self._save_plot_to_file(
                    file=file,
                    results=r,
                    dates=d,
                    title=f"{Tools.SQL_date_to_datetime_date(self.results[start_index_year]['Datum']).year}. godina"
                )

                year_for_extraction = Tools.SQL_date_to_datetime_date(result['Datum']).year
                start_index_year = i
        file.close()


class HTMLResultsToplevel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        htmlresults = HTMLResults(self)

        htmlresults.pack(expand=True, fill="both")
