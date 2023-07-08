import tkinter as tk
from tkinter.constants import END
import tkinter.font as tkFont
from datetime import datetime
import ScrollableFrame
import sqlTypes
from DateNote import DateNote
from typing import List
import Fonts
from dbcommands_rewrite import DBRemover, DBGetter, DBAdder


class ShooterNotes(tk.Frame):
    def __init__(self, parent, manage_shooters):
        tk.Frame.__init__(self, parent)
        self.manage_shooters = manage_shooters
        self.controller = parent
        self.date_font = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]
        self.notes = {}
        self.x = 800
        self.y = 450
        self.note_font_size = 10
        self.frame_notes = ScrollableFrame.Vertical(self)
        self.frame_input = ShooterNotesInput(self)
        self.note_colors = ["light steel blue", "steel blue"]
        self.note_colors_current_index = 0

        # <GRID> #
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3, uniform="shooter_notes_rows")
        self.rowconfigure(1, weight=1, uniform="shooter_notes_rows")
        # </GRID> #

        self.frame_notes.grid(row=0, column=0, sticky="nsew")
        self.frame_input.grid(row=1, column=0, sticky="nsew")

    def display_note(self, note_id: int, text: str, color: str):
        new_note = DateNote(
            self,
            self.frame_notes.scrollable_frame,
            note_id=note_id,
            text="\n" + text,
            color=color
        )
        new_note.set_font(self.note_font_size)
        self.notes[note_id] = new_note
        self.notes[note_id].pack(side="top", expand=True, fill="x")

    def delete_note(self, note_id: int):
        DBRemover.delete_note(note_id)
        self.notes[note_id].destroy()
        self.notes.pop(note_id)

    def update_values(self):
        self.clear_notes()
        notes = DBGetter.get_shooter_notes(self.manage_shooters.current_shooter_id)
        if notes:
            self.load_notes(notes)

    def load_notes(self, notes: List[sqlTypes.Napomena]):
        first_note = notes[0]
        current_date = first_note['Datum']
        date_lbl = tk.Label(
            self.frame_notes.scrollable_frame,
            text=datetime.strptime(first_note['Datum'], "%Y-%m-%d").strftime("%d. %m. %Y."),
            font=self.date_font,
            bg="deep sky blue"
        )
        date_lbl.pack(side="top", fill="x", expand=True)
        for note in notes:
            if note['Datum'] != current_date:
                date_lbl = tk.Label(
                    self.frame_notes.scrollable_frame,
                    bg="deep sky blue",
                    text=datetime.strptime(note['Datum'], "%Y-%m-%d").strftime("%d. %m. %Y.")
                )
                date_lbl.pack(side="top", expand=True, fill="x")
            if self.note_colors_current_index == 0:
                self.note_colors_current_index = 1
            else:
                self.note_colors_current_index = 0
            self.display_note(note['id'], note['Tekst'], self.note_colors[self.note_colors_current_index])

    def add_note(self, text: str, date: datetime.date):
        note_id = DBAdder.add_shooter_note(
            shooter_id=self.manage_shooters.current_shooter_id,
            text=text,
            date=str(date)
        )
        if not note_id:
            return
        if self.note_colors_current_index == 0:
            self.note_colors_current_index = 1
        else:
            self.note_colors_current_index = 0
        self.display_note(
            note_id=note_id,
            text=text,
            color=self.note_colors[self.note_colors_current_index]
        )

    def clear_notes(self):
        for child in self.frame_notes.scrollable_frame.winfo_children():
            child.destroy()
        self.notes = {}


class ShooterNotesInput(tk.Frame):
    def __init__(self, parent: ShooterNotes):
        tk.Frame.__init__(self, parent)
        self.controller = parent
        self.font = tkFont.Font(size=10)

        self.txt_note = tk.Text(
            self,
            width=40,
            height=6,
            font=self.font,
            wrap=tk.WORD,
            bd=8
        )

        self.scroll_txt_note = tk.Scrollbar(
            self,
            command=self.txt_note.yview
        )
        self.txt_note["yscrollcommand"] = self.scroll_txt_note.set

        self.btn_add_text_to_scroll = tk.Button(
            self,
            text="Dodaj",
            bg="lime",
            command=lambda: self.add_note()
        )

        self.scroll_txt_note.pack(side="right", fill="y")
        self.txt_note.pack(side="top", expand=True, fill="both")
        self.btn_add_text_to_scroll.pack(side="bottom", expand=True, fill="x")

    def add_note(self):
        self.controller.add_note(
            text=self.get_text(),
            date=datetime.today()
        )
        self.clear_text()

    def clear_text(self):
        self.txt_note.delete("1.0", END)

    def get_text(self) -> str:
        text = self.txt_note.get("1.0", END)
        text = text[:-1]  # last char is /n
        return text
