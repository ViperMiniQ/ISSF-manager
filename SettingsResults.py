import tkinter as tk
import TwoListboxes
import Tools
import Changes
from tkinter import messagebox
import Colors
from dbcommands_rewrite import DBGetter, DBUpdate, DBRemover, DBAdder
import Fonts


class ModifyResults(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_settings_dictionary = {}
        self.current = None

        self.btns_frame_top = []

        self.frame_main = TwoListboxes.TwoListboxes(self, self, Fonts.fonts2["Settings"]["twolistboxes"]["font"])  

        self.button_frame: dict[str, tk.Button] = {}
        self.button_frame_actions = {}
        self.button_frame_classes = {}

        self.active_items = {}
        self.inactive_items = {}

        self.controller = parent
        self.font = Fonts.fonts2["Settings"]["Results"]["font"]

        self.grid_propagate(False)
        self.frame_top = tk.Frame(self)

        # <GRID> #
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1, uniform="results_rows")
        self.rowconfigure(1, weight=3, uniform="results_rows")
        self.rowconfigure(2, weight=10, uniform="results_rows")
        self.rowconfigure(0, weight=1)
        # </GRID> #

        for x in range(0, 11, 2):
            self.frame_top.columnconfigure(x, weight=1, uniform="frame_results_frame_top_rows")
        for x in range(1, 11, 2):
            self.frame_top.columnconfigure(x, weight=3, uniform="frame_results_frame_top_rows")

        self.btn_targets = tk.Button(
            self.frame_top,
            text="Mete",
            font=self.font,
            command=lambda: self._change_current("Mete")
        )
        self.btns_frame_top.append(self.btn_targets)
        self.button_frame["Mete"] = self.btn_targets
        self.button_frame_classes["Mete"] = ModifyResultsTargets(self, self.frame_main)

        self.btn_program = tk.Button(
            self.frame_top,
            text="Programi",
            font=self.font,
            command=lambda: self._change_current("Programi")
        )
        self.btns_frame_top.append(self.btn_program)
        self.button_frame["Programi"] = self.btn_program
        self.button_frame_classes["Programi"] = ModifyResultsPrograms(self, self.frame_main)

        self.btn_rounds = tk.Button(
            self.frame_top,
            text="Discipline",
            font=self.font,
            command=lambda: self._change_current("Discipline")
        )
        self.btns_frame_top.append(self.btn_rounds)
        self.button_frame["Discipline"] = self.btn_rounds
        self.button_frame_classes["Discipline"] = ModifyResultsDisciplines(self, self.frame_main)

        self.btn_shooters = tk.Button(
            self.frame_top,
            text="Strijelci",
            font=self.font,
            command=lambda: self._change_current("Strijelci")
        )
        self.btns_frame_top.append(self.btn_shooters)
        self.button_frame["Strijelci"] = self.btn_shooters
        self.button_frame_classes["Strijelci"] = ModifyResultsShooters(self, self.frame_main)

        self.btn_competitions = tk.Button(
            self.frame_top,
            text="Natjecanja",
            font=self.font,
            command=lambda: self._change_current("Natjecanja")
        )
        self.btns_frame_top.append(self.btn_competitions)
        self.button_frame["Natjecanja"] = self.btn_competitions
        self.button_frame_classes["Natjecanja"] = ModifyResultsCompetitions(self, self.frame_main)

        self.btn_program.grid(row=0, column=1, sticky="nsew")
        self.btn_rounds.grid(row=0, column=3, sticky="nsew")
        self.btn_targets.grid(row=0, column=5, sticky="nsew")
        self.btn_shooters.grid(row=0, column=7, sticky="nsew")
        self.btn_competitions.grid(row=0, column=9, sticky="nsew")

        self.color_buttons(
            bg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["off"]["bg"],
            fg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["off"]["fg"]
        )

        self.frame_top.grid(row=0, column=0, sticky="nsew")

        self.frame_main.grid(row=1, rowspan=2, column=0, sticky="nsew")

        self.update_idletasks()
        self.update()

    def color_buttons(self, bg: str, fg: str):
        for key, button in self.button_frame.items():
            button.configure(bg=bg, fg=fg)

    def _change_current(self, current):
        self.current = current
        self.color_buttons(
            bg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["off"]["bg"],
            fg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["off"]["fg"]
        )
        self.button_frame[current].configure(
            bg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["on"]["bg"],
            fg=Colors.colors["Settings"]["ModifyResults"]["buttons"]["on"]["fg"]
        )
        self.button_frame_classes[current].load_items()


class TwoListboxesManipular:
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        self.twolistboxes = twolistboxes
        self.parent = parent

        self.active_items_positions = {}
        self.inactive_items_positions = {}
        self.all_items = {}
        self.item_to_rename_to = {}
        self.item_to_rename_from = ""
        self.deleted_items = {}
        self.new_items = {}
        self.items_descriptions = {}

    def event_generate_refresh_lbxs(self):
        self.twolistboxes.lbx_right.event_generate("<Configure>")
        self.twolistboxes.lbx_left.event_generate("<Configure>")

    def clear_all_dictionaries(self):
        # dict.clear() doesn't work because it breaks the reference, the way to keep the reference
        # is by going through dict keys and deleting them one by one
        for key in list(self.active_items_positions):
            self.active_items_positions.pop(key)
        for key in list(self.inactive_items_positions):
            self.inactive_items_positions.pop(key)
        for key in list(self.all_items):
            self.all_items.pop(key)
        for key in list(self.items_descriptions):
            self.items_descriptions.pop(key)

    def check_for_renamed_items(self):
        self.item_to_rename_from = self.twolistboxes.item_to_rename_from
        self.item_to_rename_to = self.twolistboxes.item_to_rename_to

    def check_for_deleted_items(self):
        dictionary = dict(self.active_items_positions, **self.inactive_items_positions)
        self.deleted_items = {key: self.all_items[key] for key in set(self.all_items) - set(dictionary)}

    def check_for_new_items(self):
        dictionary = dict(self.active_items_positions, **self.inactive_items_positions)
        self.new_items = {key: dictionary[key] for key in set(dictionary) - set(self.all_items)}

    def set_readonly(self):
        self.twolistboxes.set_readonly()

    def set_manipulateonly(self):
        self.twolistboxes.set_manipulateonly()

    def set_fullcontrol(self):
        self.twolistboxes.set_fullcontrol()

    def on_delete(self):
        pass

    def on_add(self):
        pass

    def on_update(self):
        pass

    def load_items(self):
        pass
        """implementation missing"""

    def refresh_twolistboxes_config(self):
        self.set_twolistboxes_notify_function()
        self.update_active_values()
        self.update_inactive_values()
        self.update_items_descriptions()

    def set_twolistboxes_notify_function(self):
        self.twolistboxes.set_notify_function(self.on_update)

    def update_active_values(self):
        self.twolistboxes.update_right_listbox_values(self.active_items_positions)

    def update_inactive_values(self):
        self.twolistboxes.update_left_listbox_values(self.inactive_items_positions)

    def update_items_descriptions(self):
        self.twolistboxes.update_listbox_descriptions(self.items_descriptions)


class ModifyResultsShooters(TwoListboxesManipular):
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        TwoListboxesManipular.__init__(self, parent, twolistboxes)
        Changes.subscribe_to_shooters(self)

    def update_shooters(self):
        self.load_items()

    def save_shooter_states(self):
        for key, value in self.active_items_positions.items():
            shooter_id = self.all_items[key]
            DBUpdate.update_shooter_position(shooter_id, value)
        for name, shooter_position in self.inactive_items_positions.items():
            shooter_id = self.all_items[name]
            DBUpdate.update_shooter_position(shooter_id, 0)

    def on_update(self):
        self.save_shooter_states()
        self.load_items()
        Changes.set_shooters()

    def load_items(self):
        self.clear_all_dictionaries()
        active_shooters = DBGetter.get_active_shooters_with_position()
        inactive_shooters = DBGetter.get_inactive_shooters()
        retired_shooters = DBGetter.get_retired_shooters()
        for shooter in active_shooters:
            name = f"{shooter['Ime']} {shooter['Prezime']}"
            date = f"{shooter['Datum']}"
            self.all_items[name] = shooter['id']
            self.items_descriptions[name] = f"{name}\n{date}"
            self.active_items_positions[name] = shooter['Pozicija']
        for i, shooter in enumerate(inactive_shooters):
            name = f"{shooter['Ime']} {shooter['Prezime']}"
            date = f"{shooter['Datum']}"
            self.all_items[name] = shooter['id']
            self.items_descriptions[name] = f"{name}\n{date}"
            self.inactive_items_positions[name] = i
        for i, shooter in enumerate(retired_shooters):
            name = f"(BIVŠI) {shooter['Ime']} {shooter['Prezime']}"
            date = f"{shooter['Datum']}"
            self.all_items[name] = shooter['id']
            self.items_descriptions[name] = f"{name}\n{date}"
            self.inactive_items_positions[name] = i + len(inactive_shooters)
        self.set_manipulateonly()
        self.refresh_twolistboxes_config()
        self.event_generate_refresh_lbxs()


class ModifyResultsTargets(TwoListboxesManipular):
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        TwoListboxesManipular.__init__(self, parent, twolistboxes)
        self.refresh = False

    def on_rename(self):
        if self.item_to_rename_from:
            name = list(self.item_to_rename_to.keys())[0]
            if DBUpdate.update_mete(
                target_id=DBGetter.get_target_id_from_name(self.item_to_rename_from),
                name=name,
                description=self.item_to_rename_to[name]
            ):
                self.refresh = True
                return 1
            tk.messagebox.showerror(
                title="Greška",
                message="Greška prilikom preimenovanja mete!"
            )
            return -1
        return 0

    def save_target_states(self):
        for key, value in self.active_items_positions.items():
            target_id = self.all_items[key]
            DBUpdate.update_target_position(target_id, value)
        for target, target_position in self.inactive_items_positions.items():
            target_id = self.all_items[target]
            DBUpdate.update_target_position(target_id, 0)

    def on_delete(self):
        for key, value in self.deleted_items.items():
            target_id = self.all_items[key]
            DBRemover.delete_target(target_id)

    def on_add(self):
        for key, value in self.new_items.items():
            DBAdder.add_target(name=key, description=self.items_descriptions[key])

    def on_update(self):
        self.check_for_renamed_items()
        if not self.on_rename():
            self.check_for_deleted_items()
            self.on_delete()
            self.check_for_new_items()
            self.on_add()
        self.save_target_states()
        self.load_items()
        Changes.set_targets()

    def load_items(self):
        self.clear_all_dictionaries()
        active_targets = DBGetter.get_active_targets_with_positions()
        inactive_targets = DBGetter.get_inactive_targets()
        for target in active_targets + inactive_targets:
            self.all_items[target['Naziv']] = target['id']
            self.items_descriptions[target['Naziv']] = target['Opis']
        for target in active_targets:
            self.active_items_positions[target['Naziv']] = target['Pozicija']
        for i, target in enumerate(inactive_targets):
            self.inactive_items_positions[target['Naziv']] = i
        self.set_fullcontrol()
        self.refresh_twolistboxes_config()
        self.event_generate_refresh_lbxs()


class ModifyResultsDisciplines(TwoListboxesManipular):
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        TwoListboxesManipular.__init__(self, parent, twolistboxes)
        self.refresh = False

    def on_rename(self):
        if self.item_to_rename_from:
            name = list(self.item_to_rename_to.keys())[0]
            if DBUpdate.update_discipline(
                discipline_id=DBGetter.get_discipline_details(self.item_to_rename_from)['id'],
                name=name,
                description=self.item_to_rename_to[name]
            ):
                self.refresh = True
                return 1
            tk.messagebox.showerror(
                title="Greška",
                message="Greška prilikom preimenovanja discipline!"
            )
            return -1
        return 0

    def save_discipline_states(self):
        for key, value in self.active_items_positions.items():
            discipline_id = self.all_items[key]
            DBUpdate.update_discipline_position(discipline_id, value)
        for discipline, discipline_position in self.inactive_items_positions.items():
            discipline_id = self.all_items[discipline]
            DBUpdate.update_discipline_position(discipline_id, 0)

    def on_delete(self):
        for key, value in self.deleted_items.items():
            target_id = self.all_items[key]
            DBRemover.delete_discipline(target_id)

    def on_add(self):
        for key, value in self.new_items.items():
            DBAdder.add_discipline(name=key, description=self.items_descriptions[key])

    def on_update(self):
        self.check_for_renamed_items()
        if not self.on_rename():
            self.check_for_deleted_items()
            self.on_delete()
            self.check_for_new_items()
            self.on_add()
        self.save_discipline_states()
        self.load_items()
        self.twolistboxes.select_item("right", self.twolistboxes.last_selected_item_index_listbox_right)
        Changes.set_disciplines()

    def load_items(self):
        self.clear_all_dictionaries()
        active_disciplines = DBGetter.get_active_disciplines_with_positions()
        inactive_disciplines = DBGetter.get_inactive_disciplines()
        for discipline in active_disciplines + inactive_disciplines:
            self.all_items[discipline['Naziv']] = discipline['id']
            self.items_descriptions[discipline['Naziv']] = discipline['Opis']
        for discipline in active_disciplines:
            self.active_items_positions[discipline['Naziv']] = discipline['Pozicija']
        for i, discipline in enumerate(inactive_disciplines):
            self.inactive_items_positions[discipline['Naziv']] = i
        self.set_fullcontrol()
        self.refresh_twolistboxes_config()
        self.event_generate_refresh_lbxs()


class ModifyResultsPrograms(TwoListboxesManipular):
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        TwoListboxesManipular.__init__(self, parent, twolistboxes)
        self.refresh = False

    def save_programs_states(self):
        for key, value in self.active_items_positions.items():
            program_id = self.all_items[key]
            DBUpdate.update_program_position(program_id, value)
        for program, program_position in self.inactive_items_positions.items():
            program_id = self.all_items[program]
            DBUpdate.update_program_position(program_id, 0)

    def on_rename(self):
        if self.item_to_rename_from:
            name = list(self.item_to_rename_to.keys())[0]
            if DBUpdate.update_programi(
                program_id=DBGetter.get_program_details(self.item_to_rename_from)['id'],
                name=name,
                description=self.item_to_rename_to[name]
            ):
                self.refresh = True
                return 1
            tk.messagebox.showerror(
                title="Greška",
                message="Greška prilikom preimenovanja discipline!"
            )
            return -1
        return 0

    def on_delete(self):
        for key, value in self.deleted_items.items():
            program_id = self.all_items[key]
            DBRemover.delete_program(program_id)

    def on_add(self):
        for key, value in self.new_items.items():
            DBAdder.add_program(name=key, description=self.items_descriptions[key])

    def on_update(self):
        self.check_for_renamed_items()
        if not self.on_rename():
            self.check_for_deleted_items()
            self.on_delete()
            self.check_for_new_items()
            self.on_add()
        self.save_programs_states()
        self.load_items()
        Changes.set_programs()

    def load_items(self):
        self.clear_all_dictionaries()
        active_programs = DBGetter.get_active_programs_with_positions()
        inactive_programs = DBGetter.get_inactive_programs()
        for program in active_programs + inactive_programs:
            self.all_items[program['Naziv']] = program['id']
            self.items_descriptions[program['Naziv']] = program['Opis']
        for program in active_programs:
            self.active_items_positions[program['Naziv']] = program['Pozicija']
        for i, program in enumerate(inactive_programs):
            self.inactive_items_positions[program['Naziv']] = i
        self.set_fullcontrol()
        self.refresh_twolistboxes_config()
        self.event_generate_refresh_lbxs()


class ModifyResultsCompetitions(TwoListboxesManipular):
    def __init__(self, parent, twolistboxes: TwoListboxes.TwoListboxes):
        TwoListboxesManipular.__init__(self, parent, twolistboxes)
        Changes.subscribe_to_competitions(self)

    def update_competitions(self):
        self.load_items()

    def save_competitions_states(self):
        for key, value in self.active_items_positions.items():
            competition_id = self.all_items[key]
            DBUpdate.update_competition_position(competition_id, value)
        for competition, competition_position in self.inactive_items_positions.items():
            competition_id = self.all_items[competition]
            DBUpdate.update_competition_position(competition_id, 0)

    def on_update(self):
        self.save_competitions_states()
        Changes.set_competitions()

    def get_competition_description(self, competition_id: int):
        details = DBGetter.get_competition_details(competition_id)
        categories = ", ".join(Tools.TranslateCategoriesToList(details['Kategorija']))
        description = f"{details['Naziv'] + details['Datum']}\n {categories}\n {details['Adresa']}, {details['Mjesto']}"
        return description

    def load_items(self):
        self.clear_all_dictionaries()
        active_competitions = DBGetter.get_active_competitions()
        inactive_competitions = DBGetter.get_inactive_competitions()
        for competition in active_competitions + inactive_competitions:
            competition_name = f"({Tools.SQL_date_format_to_croatian(competition['Datum'])}) {competition['Naziv']}"
            self.all_items[competition_name] = competition['id']
            self.items_descriptions[competition_name] = competition['id']
        for competition in active_competitions:
            competition_name = f"({Tools.SQL_date_format_to_croatian(competition['Datum'])}) {competition['Naziv']}"
            self.active_items_positions[competition_name] = competition['Pozicija']
        for i, competition in enumerate(inactive_competitions):
            competition_name = f"({Tools.SQL_date_format_to_croatian(competition['Datum'])}) {competition['Naziv']}"
            self.inactive_items_positions[competition_name] = i
        self.set_manipulateonly()
        self.refresh_twolistboxes_config()
        self.event_generate_refresh_lbxs()
