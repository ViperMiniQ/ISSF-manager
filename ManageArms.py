import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import ApplicationProperties
import Fonts
import Changes
import ComboboxBasicManager
import JSONManager
import KeepAspectRatio
import Notification
import ScrollableFrame
import Tools
import sqlTypes
from CustomWidgets import CustomBox
from dbcommands_rewrite import DBAdder, DBUpdate, DBGetter, DBRemover
from tkinter import messagebox, filedialog
import qrcode
import PDFTools

from PIL import ImageDraw, ImageFont
from PIL import Image, ImageTk

from barcode import EAN13
from barcode.writer import ImageWriter
from ImageCrop import ImageCrop

from CustomWidgets import DateEntry2
from typing import Dict

from ResultsTree import ResultsTree


class ManageArms(tk.Frame):
    current_weapon_id: int = 0
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.details_visible = False

        # <GRID> #

        self.grid_columnconfigure(0, weight=15, uniform="manage_shooters_columns")
        self.grid_columnconfigure(1, weight=9, uniform="manage_shooters_columns")
        self.grid_columnconfigure(2, weight=16, uniform="manage_shooters_columns")

        self.grid_rowconfigure(0, weight=7, uniform="manage_shooters_rows")
        self.grid_rowconfigure(1, weight=8, uniform="manage_shooters_rows")
        self.grid_propagate(False)

        # </GRID> #

        self.weapons_list = WeaponsList(self)
        self.weapons_list.set_notify_function(self.refresh_details)
        self.weapon_commands = WeaponsCommands(self)
        self.weapons_image = WeaponImages(self)

        self.ntb_weapons_info = ttk.Notebook(
            self
        )

        self.frame_weapon_details = WeaponDetailsSaveChanges(self)
        self.ntb_weapons_info.add(self.frame_weapon_details, text="Detalji", sticky="nsew")

        self.weapon_shooter = WeaponsShooterInfo(self, height=300)
        self.ntb_weapons_info.add(self.weapon_shooter, text="Strijelac", sticky="new")

        self.frame_weapons_qr_and_barcode = WeaponsQRandBarcode(self, height=500)
        self.ntb_weapons_info.add(self.frame_weapons_qr_and_barcode, text="QR & barcode", sticky="new")

        self.weapon_service_info = WeaponServiceInformation(self)
        self.ntb_weapons_info.add(self.weapon_service_info, text="Servis", sticky="nsew")

        self.weapon_air_cylinders = WeaponAirCylinders(self)
        self.ntb_weapons_info.add(self.weapon_air_cylinders, text="Zračni cilindri", sticky="nsew")

        self.weapons_list.grid(column=2, row=0, sticky="nsew")

    def show_details(self):
        if not self.details_visible:
            self.ntb_weapons_info.grid(column=0, row=0, rowspan=2, sticky="nsew")
            for tab in self.ntb_weapons_info.tabs():
                self.ntb_weapons_info.select(tab)
            self.ntb_weapons_info.select(0)
            self.weapons_image.grid(column=1, columnspan=2, row=1, sticky="nsew")
            self.weapon_commands.grid(column=1, row=0, sticky="nsew")
            self.details_visible = True

    def refresh_details(self):
        self.configure(cursor="watch")
        self.show_details()
        self.update_idletasks()
        try:
            ManageArms.current_weapon_id = self.weapons_list.get_selected_item_id()
            self.frame_weapon_details.set_weapon_id_and_load_details(self.current_weapon_id)
            self.weapon_service_info.refresh()
            self.weapon_shooter.refresh()
            self.weapon_air_cylinders.refresh()
            self.weapons_image.refresh()
        except:
            pass
        finally:
            self.configure(cursor="")


class WeaponsCommands(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.font = tkFont.Font(size=14)

        self.columnconfigure(0, weight=1)
        for y in range(0, 5, 2):
            self.rowconfigure(y, weight=1, uniform="rows")

        for y in range(1, 5, 2):
            self.rowconfigure(y, weight=10, uniform="rows")

        self.btn_add_reminder = tk.Button(
            self,
            text="Dodaj podsjetnik",
            font=self.font,
            fg="white",
            bg="blue",
            command=lambda: self.add_reminder()
        )

        self.btn_add_reminder.grid(row=1, column=0, sticky="nsew")

    def add_reminder(self):
        weapon_details = DBGetter.get_weapon_details(weapon_id=ManageArms.current_weapon_id)
        notification = Notification.AddNotification(
            self,
            title=f"{weapon_details['manufacturer']} {weapon_details['model']} ({weapon_details['serial_no']})",
            lock_title=True
        )
        notification.grab_set()
        notification.wait_window()


# TODO: FileNotFoundError: [WinError 2] The system cannot find the file specified: 'J:\\s 15-03-2022\\novo3\\python3/Data/Bilteni/51_bilten.pdf'


class WeaponsQRandBarcode(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.btn_font = Fonts.fonts2["Weapons"]["Commands"]["font"]

        for y in range(0, 14, 2):
            self.rowconfigure(y, weight=1, uniform="rows")
        for y in range(1, 14, 2):
            self.rowconfigure(y, weight=5, uniform="rows")

        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=10, uniform="cols")
        self.columnconfigure(2, weight=1, uniform="cols")

        self.btn_generate_qr_code = tk.Button(
            self,
            text="Generiraj QR kod",
            font=self.btn_font,
            command=lambda: self.generate_qr_code()
        )

        self.btn_show_QR_PDF = tk.Button(
            self,
            text="Prikaži QR kod (PDF)",
            font=self.btn_font,
            command=lambda: self.show_qr_pdf()
        )

        self.btn_show_QR_PNG = tk.Button(
            self,
            text="Prikaži QR kod (PNG)",
            font=self.btn_font,
            command=lambda: self.show_qr_png()
        )

        self.btn_generate_barcode = tk.Button(
            self,
            text="Generiraj barcode",
            font=self.btn_font,
            command=lambda: self.generate_barcode()
        )

        self.btn_show_barcode_PNG = tk.Button(
            self,
            text="Prikaži barcode (PNG)",
            font=self.btn_font,
            command=lambda: self.show_barcode_png()
        )

        self.btn_show_barcode_PDF = tk.Button(
            self,
            text="Prikaži barcode (PDF)",
            font=self.btn_font,
            command=lambda: self.show_barcode_pdf()
        )

        self.btn_generate_qr_code.grid(row=1, column=1, sticky="nsew")
        self.btn_show_QR_PDF.grid(row=3, column=1, sticky="nsew")
        self.btn_show_QR_PNG.grid(row=5, column=1, sticky="nsew")

        self.btn_generate_barcode.grid(row=9, column=1, sticky="nsew")
        self.btn_show_barcode_PDF.grid(row=11, column=1, sticky="nsew")
        self.btn_show_barcode_PNG.grid(row=13, column=1, sticky="nsew")

    def generate_barcode(self):
        barcode_text = "001" + "0" * (9 - len(str(ManageArms.current_weapon_id))) + str(ManageArms.current_weapon_id)
        barcode = EAN13(barcode_text, writer=ImageWriter(),
                        guardbar=True)
        barcode.save(ApplicationProperties.LOCATION + f"/Data/barcode/images/{ManageArms.current_weapon_id}")

        images = [
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 75, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 145, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 215, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 285, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 355, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 425, 750, 50, 33),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 75, 681, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 170, 681, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 265, 681, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 360, 681, 75, 49),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 75, 595, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 195, 595, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 315, 595, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 435, 595, 100, 66),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 75, 493, 125, 82),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 220, 493, 125, 82),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 365, 493, 125, 82),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 75, 385, 150, 88),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 0, 245, 385, 150, 88),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 75, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 145, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 215, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 285, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 355, 750, 50, 33),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 1, 475, 750, 50, 33),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 2, 75, 651, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 2, 170, 651, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 2, 265, 651, 75, 49),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 2, 360, 651, 75, 49),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 3, 75, 514, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 3, 195, 514, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 3, 315, 514, 100, 66),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 3, 435, 514, 100, 66),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 4, 75, 498, 125, 82),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 4, 220, 498, 125, 82),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 4, 365, 498, 125, 82),

            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 5, 75, 492, 150, 88),
            (ApplicationProperties.LOCATION + f"/Data/barcode/images/{barcode_text}.png", 5, 245, 492, 150, 88),
        ]

        PDFTools.images_to_A4_size_pdf(
            filename=ApplicationProperties.LOCATION + f"/Data/barcode/pdf/{barcode_text}",
            images=images
        )

    def generate_qr_code(self):
        image = qrcode.make(
            JSONManager.load_json(ApplicationProperties.LOCATION + "/Config/QR.json")["Oruzje"][
                "Poruka"] + f"\nid:{ManageArms.current_weapon_id}"
        )
        img = Image.new("1", size=(image.size[0], image.size[1] + 50), color=1)
        img.putdata(image.getdata())
        image1 = ImageDraw.Draw(img)
        qr_code_text = "001" + "0" * (9 - len(str(ManageArms.current_weapon_id))) + str(ManageArms.current_weapon_id)
        image1.text(
            (image.size[0] // 2, image.size[1]),
            text=qr_code_text,
            font=ImageFont.truetype("arial.ttf", 30)
        )
        image1.rectangle((0, 0, img.size[0], img.size[1]), width=2)
        img.save(ApplicationProperties.LOCATION + f"/Data/QR/images/{ManageArms.current_weapon_id}.png")

        images = [
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 75, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 145, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 215, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 285, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 355, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 425, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 495, 750, 50, 50),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 75, 655, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 170, 655, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 265, 655, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 360, 655, 75, 75),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 75, 535, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 195, 535, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 315, 535, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 435, 535, 100, 100),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 75, 390, 125, 125),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 220, 390, 125, 125),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 365, 390, 125, 125),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 75, 220, 150, 150),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 0, 245, 220, 150, 150),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 75, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 145, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 215, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 285, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 355, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 425, 750, 50, 50),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 1, 495, 750, 50, 50),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 2, 75, 725, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 2, 170, 725, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 2, 265, 725, 75, 75),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 2, 360, 725, 75, 75),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 3, 75, 700, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 3, 195, 700, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 3, 315, 700, 100, 100),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 3, 435, 700, 100, 100),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 4, 75, 675, 125, 125),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 4, 220, 675, 125, 125),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 4, 365, 675, 125, 125),

            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 5, 75, 650, 150, 150),
            (ApplicationProperties.LOCATION + f"/Data/QR/images/{qr_code_text}.png", 5, 245, 650, 150, 150),
        ]

        PDFTools.images_to_A4_size_pdf(
            filename=ApplicationProperties.LOCATION + f"/Data/QR/pdf/{qr_code_text}",
            images=images
        )

    def show_barcode_png(self):
        os.startfile(ApplicationProperties.LOCATION + f"/Data/barcode/images/{ManageArms.current_weapon_id}.png")

    def show_barcode_pdf(self):
        os.startfile(ApplicationProperties.LOCATION + f"/Data/barcode/pdf/{ManageArms.current_weapon_id}.pdf")

    def show_qr_png(self):
        os.startfile(ApplicationProperties.LOCATION + f"/Data/QR/images/{ManageArms.current_weapon_id}.png")

    def show_qr_pdf(self):
        os.startfile(ApplicationProperties.LOCATION + f"/Data/QR/pdf/{ManageArms.current_weapon_id}.pdf")


class WeaponsList(ComboboxBasicManager.ItemBasicManager):
    def __init__(self, parent):
        ComboboxBasicManager.ItemBasicManager.__init__(self, parent)

        self.cartesian_product_type_kind = {"Nema oružja za prikaz": []}

        self.lbx_menu = tk.Menu(self, tearoff=0)
        self.lbx_menu.add_command(label="Prikaži informacije", command=self.notify)

        Changes.subscribe_to_weapons(self)

        self.refresh()
        self._update_values()

    def update_weapons(self):
        self.refresh()

    def refresh(self):
        self.cartesian_product_type_kind = DBGetter.get_weapon_type_kind_cartesian_product()
        cbx_values = [key for key in self.cartesian_product_type_kind]
        self._refresh_cbx_values(cbx_values)
        self._update_values()

    def _update_values(self, event=None):
        self._clear_lbx()

        if not self.cbx.get():
            return

        for weapon_id in self.cartesian_product_type_kind[self.cbx.get()]:
            weapon_details = DBGetter.get_weapon_details(weapon_id=weapon_id)
            if not weapon_details:
                continue
            weapon_display = f"{weapon_details['manufacturer']} {weapon_details['model']} ({weapon_details['serial_no']})"
            self.items[weapon_display] = weapon_id
            self._append_to_lbx(weapon_display)

    def _delete_selected(self):
        if not self.get_item_in_focus():
            return
        if not messagebox.askyesno(
            title="Brisanje oružja",
            message=f"Jeste li sigurni da želite obrisati {self.get_item_in_focus()}?"
        ):
            return
        if not DBRemover.delete_weapon(self.get_selected_item_id()):
            messagebox.showerror(
                title="Greška",
                message="Greška prilikom brisanja oružja."
            )
            return
        Tools.remove_weapon_images(self.get_selected_item_id())
        self._update_values()
        Changes.call_refresh_weapons()

    def _add_new(self):
        new_shooter = NewWeapon(self)
        new_shooter.focus()
        new_shooter.wait_window()
        Changes.call_refresh_weapons()


class WeaponNote(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.font = tkFont.Font(size=14)

        self.lbl_note = tk.Label(
            self,
            text="Napomena:",
            font=self.font
        )

        self.txt_note = tk.Text(
            self,
            font=self.font
        )

        self.lbl_note.pack(side="top", fill="x", anchor="w")
        self.txt_note.pack(side="top", expand=True, fill="both")

    def get_note(self):
        return self.txt_note.get("1.0", tk.END)[:-1]

    def set_note(self, text: str):
        self.txt_note.delete("1.0", tk.END)
        self.txt_note.insert("1.0", str(text))


class WeaponsDetails(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.parent = parent

        self.font = tkFont.Font(size=20)

        self.frame_main = ScrollableFrame.Vertical(self)

        self.frame_main.scrollable_frame.columnconfigure(0, weight=1)

        self.frame_type = NewWeaponTypeFrame(self.frame_main.scrollable_frame, bd=2, relief="solid", height=80,
                                             width=600)
        self.frame_necessary = NewWeaponNecessaryFrame(self.frame_main.scrollable_frame, bd=2, relief="solid",
                                                         height=200, width=600)
        self.frame_dimensions = NewWeaponDimensionsFrame(self.frame_main.scrollable_frame, bd=2, relief="solid",
                                                         height=160, width=600)
        self.frame_handle = NewWeaponHandleFrame(self.frame_main.scrollable_frame, bd=2, relief="solid", height=120,
                                                 width=600)
        self.frame_barrel = NewWeaponBarrelFrame(self.frame_main.scrollable_frame, bd=2, relief="solid", height=160,
                                                 width=600)
        self.frame_trigger = NewWeaponTriggerFrame(self.frame_main.scrollable_frame, bd=2, relief="solid", height=120,
                                                   width=600)
        self.frame_note = WeaponNote(self.frame_main.scrollable_frame, bd=2, relief="solid", height=50)

        self.frame_main.pack(side="top", expand=True, fill="both")

        self.frame_type.grid(column=0, row=0, sticky="nsew")
        self.frame_necessary.grid(column=0, row=1, sticky="nsew")
        self.frame_dimensions.grid(column=0, row=2, sticky="nsew")
        self.frame_handle.grid(column=0, row=3, sticky="nsew")
        self.frame_barrel.grid(column=0, row=5, sticky="nsew")
        self.frame_trigger.grid(column=0, row=6, sticky="nsew")
        self.frame_note.grid(column=0, row=7, sticky="nsew")

    def load(self, weapon_id: int):
        details = DBGetter.get_weapon_details(weapon_id=weapon_id)
        if not details:
            return
        # set trigger
        self.frame_trigger.set_values(
            {
                "max_mass": details['trigger_mass_to'],
                "min_mass": details['trigger_mass_from']
            }
        )
        # type & kind
        self.frame_type.set_values(
            {
                "kind": details['kind'],
                "type": details['type']
            }
        )
        # necessary
        self.frame_necessary.set_values(
            {
                "serial_no": details["serial_no"],
                "model": details["model"],
                "manufacturer": details["manufacturer"],
                "id": 0
            }
        )
        # handle
        self.frame_handle.set_values(
            {
                "hand": details['handle_hand'],
                "size": details['handle_size']
            }
        )
        # barrel
        self.frame_barrel.set_values(
            {
                "length": details['barrel_length'],
                "material": details['material'],
                "caliber": details['caliber']
            }
        )
        # dimensions
        self.frame_dimensions.set_values(
            {
                "length": details['length'],
                "width": details['width'],
                "height": details['height']
            }
        )
        # note
        self.frame_note.set_note(details['note'])

    def save(self, weapon_id: int = 0):
        necessary = self.frame_necessary.get_values()

        if not weapon_id:
            if not (self.frame_necessary.check_data_present_in_entries() and self.frame_type.check_data_present_in_entries()):
                messagebox.showerror(title="Greška", message="Obavezni podaci nisu unešeni.")
                return False
            if not DBAdder.add_weapon(
                    serial_no=necessary["serial number"],
                    manufacturer=necessary["manufacturer"],
                    model=necessary["model"]
            ):
                messagebox.showerror(title="Greška", message="Greška prilikom kreiranja profila oružja.")
                return False
            weapon_id = DBGetter.get_weapon_details(serial_no=necessary["serial number"])['id']

        handle = self.frame_handle.get_values()
        w_type = self.frame_type.get_values()
        dimensions = self.frame_dimensions.get_values()
        barrel = self.frame_barrel.get_values()
        trigger = self.frame_trigger.get_values()
        
        if not DBUpdate.update_weapon(
            weapon_id=weapon_id,
            details={
                "kind": w_type["kind"],
                "type": w_type["type"],
                "length": dimensions["length"],
                "height": dimensions["height"],
                "width": dimensions["width"],
                "caliber": barrel["caliber"],
                "material": barrel["material"],
                "trigger_mass_to": trigger["trigger mass max"],
                "trigger_mass_from": trigger["trigger mass min"],
                "barrel_length": barrel["length"],
                "id": 0,
                "handle_hand": handle["hand"],
                "handle_size": handle["size"],
                "serial_no": necessary["serial number"],
                "manufacturer": necessary["manufacturer"],
                "model": necessary["model"],
                "note": self.frame_note.get_note()
            }
        ):
            messagebox.showerror(title="Greška", message="Greška prilikom spremanja parametara oružja. Profil oružja je kreiran.")
            return False
        Changes.call_refresh_weapons()
        return True


class WeaponDetailsSaveChanges(WeaponsDetails):
    def __init__(self, parent):
        super().__init__(parent)

        self.weapon_id = 0

        self.btn_save = tk.Button(
            self,
            text="Spremi promjene",
            bg="lime",
            fg="black",
            font=self.font,
            command=lambda: self.save_changes()
        )
        self.btn_save.pack(side="bottom", fill="x")

    def save_changes(self):
        if self.weapon_id:
            self.save(self.weapon_id)

    def set_weapon_id_and_load_details(self, weapon_id: int):
        self.weapon_id = weapon_id
        self.load(self.weapon_id)


class NewWeapon(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.grab_set()

        self.frame_main = WeaponsDetails(self)

        self.btn_confirm = tk.Button(
            self,
            text="Dodaj",
            bg="lime",
            fg="black",
            font=tkFont.Font(size=14),
            command=lambda: self.add_new()
        )

        self.frame_main.pack(side="top", fill="both", expand=True)
        self.btn_confirm.pack(side="bottom", fill="x")

        self.geometry("{}x{}".format(600, 800))
        self.resizable(False, True)

    def add_new(self):
        if self.frame_main.save():
            self.destroy()


class NewWeaponTypeFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.grid_propagate(False)

        cbx_category_values = ['Zračno', 'Vatreno']
        cbx_type_values = ['Puška', 'Pištolj', 'Samostrel', 'Sačmarica']

        self.font_title = tkFont.Font(size=14)
        self.font_cbx = tkFont.Font(size=14)

        self.lbl_title = tk.Label(
            self,
            text="Vrsta:",
            fg="red",
            font=self.font_title
        )

        self.cbx_category = CustomBox(
            self,
            values=cbx_category_values,
            font=self.font_cbx,
            state="readonly",
            width=10
        )

        self.lbl_type = tk.Label(
            self,
            text="Tip:",
            font=self.font_title,
            fg="red"
        )

        self.cbx_type = CustomBox(
            self,
            values=cbx_type_values,
            font=self.font_cbx,
            state="readonly",
            width=15
        )

        self.lbl_title.place(relx=0.1, rely=0.45, anchor="sw")
        self.cbx_category.place(relx=0.1, rely=0.55, anchor="nw")
        self.lbl_type.place(relx=0.5, rely=0.45, anchor="sw")
        self.cbx_type.place(relx=0.5, rely=0.55, anchor="nw")

    def set_values(self, values: sqlTypes.WeaponTypeKind):
        self.cbx_type.set(values['type'])
        self.cbx_category.set(values['kind'])

    def get_values(self):
        return {
            "kind": self.cbx_category.get(),
            "type": self.cbx_type.get()
        }

    def check_data_present_in_entries(self):
        if not self.cbx_type.get():
            return False
        if not self.cbx_category.get():
            return False
        return True


class NewWeaponNecessaryFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.grid_propagate(False)

        self.font_title = tkFont.Font(size=16)
        self.font_lbl = tkFont.Font(size=14)
        self.font_ent = tkFont.Font(size=14)

        self.columnconfigure(0, weight=1, uniform="cols")
        for x in range(1, 21, 1):
            self.columnconfigure(x, weight=2, uniform="cols")
        self.columnconfigure(21, weight=1, uniform="cols")

        self.lbl_title = tk.Label(
            self,
            text="Obavezno:",
            font=self.font_title,
            fg="#ff0000"
        )

        self.lbl_serial_number = tk.Label(
            self,
            text="Serijski broj:",
            font=self.font_lbl,
            fg="#ff0000"
        )

        self.ent_serial_number = tk.Entry(
            self,
            font=self.font_ent,
            bd=2,
            width=27
        )

        self.lbl_company = tk.Label(
            self,
            text="Proizvođač:",
            font=self.font_lbl,
            fg="#ff0000"
        )

        self.ent_company = tk.Entry(
            self,
            font=self.font_ent,
            bd=2,
            width=28
        )

        self.lbl_model = tk.Label(
            self,
            text="Model:",
            font=self.font_lbl,
            fg="#ff0000"
        )

        self.ent_model = tk.Entry(
            self,
            font=self.font_ent,
            bd=2,
            width=20
        )

        self.lbl_title.place(relx=0.5, rely=0.1, anchor="center")

        self.lbl_serial_number.place(relx=0.05, rely=0.3, anchor="w")
        self.ent_serial_number.place(relx=0.3, rely=0.3, anchor="w")

        self.lbl_company.place(relx=0.05, rely=0.55, anchor="w")
        self.ent_company.place(relx=0.28, rely=0.55, anchor="w")

        self.lbl_model.place(relx=0.05, rely=0.8, anchor="w")
        self.ent_model.place(relx=0.2, rely=0.8, anchor="w")

    def check_data_present_in_entries(self):
        if not self.ent_model.get():
            return False
        if not self.ent_company.get():
            return False
        if not self.ent_serial_number.get():
            return False
        return True

    def set_values(self, values: sqlTypes.Weapon):
        self.ent_serial_number.delete(0, tk.END)
        self.ent_serial_number.insert(0, values['serial_no'])

        self.ent_model.delete(0, tk.END)
        self.ent_model.insert(0, values['model'])

        self.ent_company.delete(0, tk.END)
        self.ent_company.insert(0, values['manufacturer'])


    def get_values(self):
        return {
            "serial number": self.ent_serial_number.get(),
            "manufacturer": self.ent_company.get(),
            "model": self.ent_model.get()
        }


class NewWeaponDimensionsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.font_title = tkFont.Font(size=14)
        self.font_lbl = tkFont.Font(size=14)
        self.font_ent = tkFont.Font(size=14)

        self.lbl_title = tk.Label(
            self,
            text="Dimenzije",
            font=self.font_lbl
        )

        self.lbl_length = tk.Label(
            self,
            text="Duljina:",
            font=self.font_lbl
        )

        self.ent_length = tk.Entry(
            self,
            font=self.font_ent,
            width=8
        )

        self.lbl_height = tk.Label(
            self,
            text="Visina:",
            font=self.font_lbl
        )

        self.ent_height = tk.Entry(
            self,
            font=self.font_ent,
            width=8
        )

        self.lbl_width = tk.Label(
            self,
            text="Širina:",
            font=self.font_lbl
        )

        self.ent_width = tk.Entry(
            self,
            font=self.font_ent,
            width=8
        )

        self.lbl_mm1 = tk.Label(
            self,
            text="mm",
            font=self.font_ent
        )

        self.lbl_mm2 = tk.Label(
            self,
            text="mm",
            font=self.font_ent
        )

        self.lbl_mm3 = tk.Label(
            self,
            text="mm",
            font=self.font_ent
        )

        self.lbl_title.place(relx=0.5, rely=0.1, anchor="center")

        self.lbl_length.place(relx=0.1, rely=0.3, anchor="w")
        self.ent_length.place(relx=0.45, rely=0.3, anchor="e")
        self.lbl_mm1.place(relx=0.45, rely=0.3, anchor="w")

        self.lbl_height.place(relx=0.1, rely=0.55, anchor="w")
        self.ent_height.place(relx=0.45, rely=0.55, anchor="e")
        self.lbl_mm2.place(relx=0.45, rely=0.55, anchor="w")

        self.lbl_width.place(relx=0.1, rely=0.8, anchor="w")
        self.ent_width.place(relx=0.45, rely=0.8, anchor="e")
        self.lbl_mm3.place(relx=0.45, rely=0.8, anchor="w")

    def set_values(self, values: sqlTypes.WeaponDimensions):
        self.ent_length.delete(0, tk.END)
        self.ent_length.insert(0, str(values['length']))

        self.ent_width.delete(0, tk.END)
        self.ent_width.insert(0, str(values['width']))

        self.ent_height.delete(0, tk.END)
        self.ent_height.insert(0, str(values['height']))

    def get_values(self):
        return {
            "length": self.ent_length.get(),
            "width": self.ent_width.get(),
            "height": self.ent_height.get()
        }


class NewWeaponHandleFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.font_title = tkFont.Font(size=14)
        self.font_lbl = tkFont.Font(size=14)
        self.font_cbx = tkFont.Font(size=14)

        cbx_hand_values = ['ljevake', 'dešnjake']
        cbx_size_values = ['S', 'M', 'L', 'XL']

        self.lbl_title = tk.Label(
            self,
            text="Drška",
            font=self.font_lbl
        )

        self.lbl_hand = tk.Label(
            self,
            text="Za:",
            font=self.font_lbl
        )

        self.cbx_hand = CustomBox(
            self,
            font=self.font_cbx,
            values=cbx_hand_values,
            state="readonly",
            width=9
        )

        self.lbl_size = tk.Label(
            self,
            text="Veličina:",
            font=self.font_lbl
        )

        self.cbx_size = CustomBox(
            self,
            font=self.font_cbx,
            values=cbx_size_values,
            state="readonly",
            width=2
        )

        self.lbl_title.place(relx=0.5, rely=0.15, anchor="center")

        self.lbl_hand.place(relx=0.1, rely=0.4, anchor="w")
        self.cbx_hand.place(relx=0.25, rely=0.4, anchor="w")

        self.lbl_size.place(relx=0.1, rely=0.75, anchor="w")
        self.cbx_size.place(relx=0.35, rely=0.75, anchor="w")

    def set_values(self, values: sqlTypes.WeaponHandle):
        self.cbx_size.set(values['size'])
        self.cbx_hand.set(values['hand'])

    def get_values(self):
        return {
            "hand": self.cbx_hand.get(),
            "size": self.cbx_size.get()
        }


class NewWeaponBarrelFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.font_title = tkFont.Font(size=14)
        self.font_lbl = tkFont.Font(size=14)
        self.font_ent = tkFont.Font(size=14)

        self.lbl_title = tk.Label(
            self,
            text="Cijev",
            font=self.font_title
        )

        self.lbl_length = tk.Label(
            self,
            text="Duljina:",
            font=self.font_lbl
        )

        self.ent_length = tk.Entry(
            self,
            font=self.font_ent,
            width=6
        )

        self.lbl_caliber = tk.Label(
            self,
            font=self.font_lbl,
            text="Kalibar:"
        )

        self.ent_caliber = tk.Entry(
            self,
            font=self.font_ent,
            width=4
        )

        self.lbl_material = tk.Label(
            self,
            text="Materijal:",
            font=self.font_lbl
        )

        self.ent_material = tk.Entry(
            self,
            font=self.font_ent,
            width=25
        )

        self.lbl_mm1 = tk.Label(
            self,
            text="mm",
            font=self.font_ent
        )

        self.lbl_mm2 = tk.Label(
            self,
            text="mm",
            font=self.font_ent
        )

        self.lbl_title.place(relx=0.5, rely=0.1, anchor="center")

        self.lbl_length.place(relx=0.1, rely=0.3, anchor="w")
        self.ent_length.place(relx=0.4, rely=0.3, anchor="e")
        self.lbl_mm1.place(relx=0.4, rely=0.3, anchor="w")

        self.lbl_caliber.place(relx=0.1, rely=0.55, anchor="w")
        self.ent_caliber.place(relx=0.4, rely=0.55, anchor="e")
        self.lbl_mm2.place(relx=0.4, rely=0.55, anchor="w")

        self.lbl_material.place(relx=0.1, rely=0.8, anchor="w")
        self.ent_material.place(relx=0.35, rely=0.8, anchor="w")

    def set_values(self, values: sqlTypes.WeaponBarrel):
        self.ent_length.delete(0, tk.END)
        self.ent_length.insert(0, str(values['length']))

        self.ent_material.delete(0, tk.END)
        self.ent_material.insert(0, str(values['material']))

        self.ent_caliber.delete(0, tk.END)
        self.ent_caliber.insert(0, str(values['caliber']))

    def get_values(self):
        return {
            "length": self.ent_length.get(),
            "caliber": self.ent_caliber.get(),
            "material": self.ent_material.get()
        }


class NewWeaponTriggerFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.font_title = tkFont.Font(size=14)
        self.font_lbl = tkFont.Font(size=14)
        self.font_ent = tkFont.Font(size=14)

        self.lbl_title = tk.Label(
            self,
            text="Okidač",
            font=self.font_title
        )

        self.lbl_from = tk.Label(
            self,
            text="od:",
            font=self.font_ent
        )

        self.lbl_to = tk.Label(
            self,
            text="do:",
            font=self.font_ent
        )

        self.lbl_g1 = tk.Label(
            self,
            text="g",
            font=self.font_ent
        )

        self.lbl_g2 = tk.Label(
            self,
            text="g",
            font=self.font_ent
        )

        self.ent_trigger_mass_min = tk.Entry(
            self,
            font=self.font_ent,
            width=4
        )

        self.ent_trigger_mass_max = tk.Entry(
            self,
            font=self.font_ent,
            width=4
        )

        self.lbl_trigger_mass = tk.Label(
            self,
            text="Masa okidanja:",
            font=self.font_lbl
        )

        self.lbl_title.place(relx=0.5, rely=0.2, anchor="center")

        self.lbl_trigger_mass.place(relx=0.05, rely=0.7, anchor="w")

        self.lbl_from.place(relx=0.5, rely=0.7, anchor="e")
        self.ent_trigger_mass_min.place(relx=0.5, rely=0.7, anchor="w")
        self.lbl_g1.place(relx=0.62, rely=0.7, anchor="center")

        self.lbl_to.place(relx=0.8, rely=0.7, anchor="e")
        self.ent_trigger_mass_max.place(relx=0.8, rely=0.7, anchor="w")
        self.lbl_g2.place(relx=0.92, rely=0.7, anchor="center")

    def set_values(self, values: sqlTypes.WeaponTrigger):
        self.ent_trigger_mass_max.delete(0, tk.END)
        self.ent_trigger_mass_max.insert(0, str(values['max_mass']))

        self.ent_trigger_mass_min.delete(0, tk.END)
        self.ent_trigger_mass_min.insert(0, str(values['min_mass']))

    def get_values(self):
        return {
            "trigger mass min": self.ent_trigger_mass_min.get(),
            "trigger mass max": self.ent_trigger_mass_max.get(),
        }


class WeaponAirCylinders(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.font = tkFont.Font(size=20)

        self.parent = parent
        self.initial_state = []

        self.frame_main = ScrollableFrame.Vertical(self)

        self.air_cylinders = {}

        self.frames_air_cylinders = []

        self.btn_add = tk.Button(
            self,
            text="Pridruži oružju",
            font=self.font,
            command=lambda: self.add_weapon_air_cylinder()
        )

        self.btn_add.pack(side="top", fill="x")

        self.frame_main.pack(side="top", expand=True, fill="both")

        self.update_air_cylinders()
        Changes.subscribe_to_air_cylinders(self)

    def save_air_cylinder_weapon_information(self):
        pass

    def create_new_air_cylinder(self):
        AddNewAirCylinderToplevel(self, cylinder_id=0).wait_window()

    def add_weapon_air_cylinder(self):
        self.frames_air_cylinders.append(
            WeaponAirCylinder(
                self.frame_main.scrollable_frame,
                cylinder_id=0,
                height=600
            )
        )
        self.frames_air_cylinders[-1].set_save_mode()
        self.frames_air_cylinders[-1].pack(side="top", expand=True, fill="x")
        self.frames_air_cylinders[-1].refresh(self.air_cylinders)

    def update_air_cylinders(self):
        air_cylinders = DBGetter.get_available_air_cylinders()

        self.air_cylinders.clear()

        for air_cylinder in air_cylinders:
            self.air_cylinders[f"{air_cylinder['serial_no']} ({air_cylinder['manufacturer']})"] = air_cylinder['id']

        self.refresh()

    def refresh(self):
        for frame in self.frames_air_cylinders:
            frame.destroy()

        self.frames_air_cylinders.clear()

        self.initial_state = DBGetter.get_weapon_air_cylinders(ManageArms.current_weapon_id)

        print("inišal stejt", self.initial_state)
        for air_cylinder_id in self.initial_state:
            self.frames_air_cylinders.append(
                WeaponAirCylinder(
                    self.frame_main.scrollable_frame,
                    cylinder_id=air_cylinder_id,
                    height=600,
                    pady=50
                )
            )
            self.frames_air_cylinders[-1].cbx_air_cylinders.configure(state="disabled")
            self.frames_air_cylinders[-1].pack(side="top", fill="x")
            self.frames_air_cylinders[-1].refresh(self.air_cylinders)


class WeaponAirCylinder(tk.Frame):
    def __init__(self, parent, cylinder_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent

        self.air_cylinders = {}

        self.font = tkFont.Font(size=14)

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=5, uniform="rows")
        self.rowconfigure(1, weight=1, uniform="rows")

        self.rowconfigure(2, weight=30, uniform="rows")
        self.rowconfigure(3, weight=1, uniform="rows")
        self.rowconfigure(4, weight=5, uniform="rows")
        self.rowconfigure(5, weight=5, uniform="rows")

        self.cbx_air_cylinders = CustomBox(
            self,
            font=self.font,
            justify="center",
            state="readonly"
        )
        self.grid_propagate(False)
        self.frame_details = AirCylinderDetails(self, cylinder_id=cylinder_id)

        self.btn_remove = tk.Button(
            self,
            text="Ukloni",
            font=self.font,
            bg="red",
            command=lambda: self.remove_air_cylinder_from_weapon()
        )

        self.cbx_air_cylinders.grid(row=0, column=0, sticky="ew")
        self.frame_details.grid(row=2, column=0, sticky="nsew")
        self.btn_remove.grid(row=4, column=0, sticky="nsew")

        self.cbx_air_cylinders.bind("<<ComboboxSelected>>", self.update_air_cylinder_details)

    def set_save_mode(self):
        self.btn_remove.configure(
            text="Spremi",
            bg="lime",
            command=lambda: self.update_air_cylinder_weapon()
        )

    def update_air_cylinder_weapon(self):
        if not DBUpdate.update_air_cylinder_weapon(
            air_cylinder_id=self.frame_details.cylinder_id,
            weapon_id=ManageArms.current_weapon_id
        ):
            messagebox.showerror(title="Greška", message="Greška prilikom pridruživanja zračnog cilindra oružju.")

        Changes.call_refresh_air_cylinders()

    def remove_air_cylinder_from_weapon(self):
        if DBUpdate.update_air_cylinder_weapon(air_cylinder_id=self.frame_details.cylinder_id, weapon_id=0):
            self.destroy()
            Changes.call_refresh_air_cylinders()

    def update_air_cylinder_details(self, event=None):
        self.frame_details.load(air_cylinder_id=self.air_cylinders[self.cbx_air_cylinders.get()])

    def show_air_cylinder_details(self):
        self.frame_details.load(air_cylinder_id=self.air_cylinders[self.cbx_air_cylinders.get()])

    def refresh(self, air_cylinders: Dict[str, int]):
        self.air_cylinders = air_cylinders
        self.cbx_air_cylinders.configure(values=[key for key in self.air_cylinders])

        if self.frame_details.cylinder_id:
            for key, value in self.air_cylinders.items():
                if value == self.frame_details.cylinder_id:
                    self.cbx_air_cylinders.set(key)
                    return


class AddNewAirCylinderToplevel(tk.Toplevel):
    def __init__(self, parent, cylinder_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grab_set()

        self.geometry(f"{500}x{450}")

        self.frame_main = AirCylinderDetails(self, cylinder_id=cylinder_id)

        self.btn_add = tk.Button(
            self,
            text="Spremi",
            font=tkFont.Font(size=14),
            bg="lime",
            fg="black",
            command=lambda: self.save_and_exit()
        )

        self.frame_main.pack(side="top", expand=True, fill="both")
        self.btn_add.pack(side="bottom", fill="x")

    def save_and_exit(self):
        self.frame_main.save()
        self.destroy()


class AirCylinderDetails(tk.Frame):
    def __init__(self, parent, cylinder_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.cylinder_id = cylinder_id

        self.font_title = tkFont.Font(size=14, underline=True)
        self.font_lbl = tkFont.Font(size=14)
        self.font_ent = tkFont.Font(size=14)

        self.validate_integer = (self.register(Tools.allow_only_integer))

        self.lbl_title = tk.Label(
            self,
            text="Cilindar za zrak",
            font=self.font_title
        )

        self.lbl_length = tk.Label(
            self,
            text="Duljina: ",
            font=self.font_lbl
        )

        self.ent_length = tk.Entry(
            self,
            font=self.font_ent,
            width=6,
            validate="all",
            validatecommand=(self.validate_integer, "%P")
        )

        self.lbl_mm1 = tk.Label(
            self,
            text="mm",
            font=self.font_lbl
        )

        self.lbl_capacity = tk.Label(
            self,
            text="Kapacitet: ",
            font=self.font_lbl
        )

        self.ent_capacity = tk.Entry(
            self,
            font=self.font_ent,
            width=9,
            validate="all",
            validatecommand=(self.validate_integer, "%P")
        )

        self.lbl_mass = tk.Label(
            self,
            text="Masa: ",
            font=self.font_lbl
        )

        self.ent_mass = tk.Entry(
            self,
            font=self.font_ent,
            width=6,
            validate="all",
            validatecommand=(self.validate_integer, "%P")
        )

        self.lbl_max_pressure = tk.Label(
            self,
            text="Maksimalni pritisak: ",
            font=self.font_lbl
        )

        self.ent_max_pressure = tk.Entry(
            self,
            font=self.font_ent,
            width=5,
            validate="all",
            validatecommand=(self.validate_integer, "%P")
        )

        self.lbl_shots = tk.Label(
            self,
            text="hitaca",
            font=self.font_ent
        )

        self.lbl_g = tk.Label(
            self,
            text="g",
            font=self.font_ent
        )

        self.lbl_bar = tk.Label(
            self,
            text="bar",
            font=self.font_ent
        )

        self.lbl_serial_number = tk.Label(
            self,
            font=self.font_lbl,
            text="Serijski broj: "
        )

        self.ent_serial_number = tk.Entry(
            self,
            font=self.font_ent,
            width=20
        )

        self.lbl_producer = tk.Label(
            self,
            text="Proizvođač: ",
            font=self.font_lbl
        )

        self.ent_producer = tk.Entry(
            self,
            width=18,
            font=self.font_ent
        )

        self.lbl_diameter = tk.Label(
            self,
            text="Promjer: ",
            font=self.font_lbl
        )

        self.ent_diameter = tk.Entry(
            self,
            width=9,
            font=self.font_ent,
            validate="all",
            validatecommand=(self.validate_integer, "%P")
        )

        self.lbl_mm2 = tk.Label(
            self,
            text="mm",
            font=self.font_lbl
        )

        self.lbl_date = tk.Label(
            self,
            text="Vrijedi do:",
            font=self.font_lbl
        )

        self.date_expire = DateEntry2(
            self,
            font=self.font_ent,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )

        self.lbl_title.place(relx=0.5, rely=0.075, anchor="center")

        self.lbl_serial_number.place(relx=0.35, rely=0.2, anchor="e")
        self.ent_serial_number.place(relx=0.35, rely=0.2, anchor="w")

        self.lbl_producer.place(relx=0.35, rely=0.3, anchor="e")
        self.ent_producer.place(relx=0.35, rely=0.3, anchor="w")

        self.lbl_length.place(relx=0.3, rely=0.4, anchor="e")
        self.ent_length.place(relx=0.3, rely=0.4, anchor="w")
        self.lbl_mm1.place(relx=0.45, rely=0.4, anchor="w")

        self.lbl_capacity.place(relx=0.3, rely=0.5, anchor="e")
        self.ent_capacity.place(relx=0.3, rely=0.5, anchor="w")
        self.lbl_shots.place(relx=0.5, rely=0.5, anchor="w")

        self.lbl_mass.place(relx=0.3, rely=0.6, anchor="e")
        self.ent_mass.place(relx=0.3, rely=0.6, anchor="w")
        self.lbl_g.place(relx=0.5, rely=0.6, anchor="w")

        self.lbl_max_pressure.place(relx=0.6, rely=0.7, anchor="e")
        self.ent_max_pressure.place(relx=0.6, rely=0.7, anchor="w")
        self.lbl_bar.place(relx=0.8, rely=0.7, anchor="w")

        self.lbl_diameter.place(relx=0.3, rely=0.8, anchor="e")
        self.ent_diameter.place(relx=0.3, rely=0.8, anchor="w")
        self.lbl_mm2.place(relx=0.65, rely=0., anchor="center")

        self.lbl_date.place(relx=0.3, rely=0.9, anchor="e")
        self.date_expire.place(relx=0.3, rely=0.9, anchor="w")

        if self.cylinder_id:
            self.load()

    def load(self, air_cylinder_id: int = 0):
        if air_cylinder_id:
            self.cylinder_id = air_cylinder_id

        details = DBGetter.get_air_cylinder_details(cylinder_id=self.cylinder_id)
        if not details:
            return

        self.ent_serial_number.delete(0, tk.END)
        self.ent_serial_number.insert(0, str(details['serial_no']))

        self.ent_length.delete(0, tk.END)
        self.ent_length.insert(0, str(details['length']))

        self.ent_mass.delete(0, tk.END)
        self.ent_mass.insert(0, str(details['mass']))

        self.ent_diameter.delete(0, tk.END)
        self.ent_diameter.insert(0, str(details['diameter']))

        self.ent_producer.delete(0, tk.END)
        self.ent_producer.insert(0, str(details['manufacturer']))

        self.ent_max_pressure.delete(0, tk.END)
        self.ent_max_pressure.insert(0, str(details['max_pressure']))

        self.ent_capacity.delete(0, tk.END)
        self.ent_capacity.insert(0, str(details['capacity']))

        self.date_expire.set_date(Tools.SQL_date_format_to_croatian(details['date_expire']))

    def get_details(self) -> sqlTypes.AirCylinder:
        return {
            "id": self.cylinder_id,
            "serial_no": self.ent_serial_number.get(),
            "manufacturer": self.ent_producer.get(),
            "length": self.ent_length.get(),
            "capacity": self.ent_capacity.get(),
            "mass": self.ent_mass.get(),
            "max_pressure": self.ent_max_pressure.get(),
            "diameter": self.ent_diameter.get(),
            "date_expire": str(self.date_expire.get_date())
        }

    def save(self):
        if not self.cylinder_id:
            if not DBAdder.add_air_cylinder( # should be equals False
                serial_no=self.ent_serial_number.get()
            ):
                messagebox.showerror(title="Greška", message="Greška prilikom kreiranja profila zračnog cilindra.")
                return
            self.cylinder_id = DBGetter.get_air_cylinder_details(serial_no=self.ent_serial_number.get())['id']

        if not DBUpdate.update_air_cylinder(
            details={
                "id": 0,
                "serial_no": self.ent_serial_number.get(),
                "manufacturer": self.ent_producer.get(),
                "length": self.ent_length.get(),
                "capacity": self.ent_capacity.get(),
                "mass": self.ent_mass.get(),
                "max_pressure": self.ent_max_pressure.get(),
                "diameter": self.ent_diameter.get(),
                "date_expire": str(self.date_expire.get_date())
            },
            cylinder_id=self.cylinder_id
        ):
            messagebox.showerror(title="Greška", message="Greška prilikom spremanja parametara zračnog cilindra.")
        Changes.call_refresh_air_cylinders()


class WeaponsShooterInfo(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.image = None
        self.canvas_image = None
        self.canvas_img = None

        self.shooters = {}

        self.grid_propagate(False)

        Changes.subscribe_to_shooters(self)

        self.font = Fonts.fonts2["Weapons"]["WeaponsShooterInfo"]["font"]

        self.columnconfigure(0, weight=10, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")
        self.columnconfigure(2, weight=20, uniform="cols")
        self.columnconfigure(3, weight=1, uniform="cols")

        for y in range(0, 6, 1):
            self.rowconfigure(y, weight=1, uniform="rows")

        self.canv_shooter_image = tk.Canvas(
            self,
            background="black"
        )

        self.cbx_shooters = CustomBox(
            self,
            font=self.font,
            state="readonly"
        )

        self.lbl_title = tk.Label(
            self,
            text="Oružje pridruženo:",
            font=self.font
        )

        self.btn_save = tk.Button(
            self,
            text="Spremi",
            fg="black",
            bg="lime",
            font=self.font,
            command=lambda: self.save()
        )

        self.lbl_title.grid(row=1, column=2, sticky="nsew")
        self.cbx_shooters.grid(row=3, column=2, sticky="nsew")
        self.canv_shooter_image.grid(row=0, rowspan=5, column=0, sticky="nsew")
        self.btn_save.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.cbx_shooters.bind("<<ComboboxSelected>>", self.load_shooter_image)

        self.canv_shooter_image.bind("<Map>", lambda event=None: self.after(50, self.load_shooter_image()))
        # on the first app opening and weapon selection, shooter image
        # won't appear on the canvas since the canvas object is not visible, so winfo_width() is 1

        self.update_shooters()

    def refresh(self):
        self.cbx_shooters.set("")
        self.canv_shooter_image.delete("all")

        shooter_id = DBGetter.get_weapon_shooter(ManageArms.current_weapon_id)

        # if not shooter_id:
        #    return

        for s_name, s_id in self.shooters.items():
            if s_id == shooter_id:
                self.cbx_shooters.set(s_name)
                break

        self.load_shooter_image()

    def load_shooter_image(self, event=None):
        try:
            shooter_id = self.shooters[self.cbx_shooters.get()]
        except KeyError:
            self.canv_shooter_image.delete("all")
            return
        # self.canv_shooter_image.wait_visibility(self.parent)
        x_cropped = self.canv_shooter_image.winfo_width()
        y_cropped = self.canv_shooter_image.winfo_height()
        try:
            self.image = Image.open(ApplicationProperties.SHOOTER_IMAGES_DIR + str(shooter_id) + ".png")
            self.canvas_img = self.image.resize((x_cropped, y_cropped), Image.ANTIALIAS)
            self.canvas_img = ImageTk.PhotoImage(self.canvas_img)
            self.canv_shooter_image.create_image(0, 0, image=self.canvas_img, anchor="nw")
        except (FileNotFoundError, PermissionError):
            self.canv_shooter_image.delete("all")

    def save(self):
        if not DBUpdate.update_weapon_shooter(
            weapon_id=ManageArms.current_weapon_id,
            shooter_id=self.shooters[self.cbx_shooters.get()]
        ):
            messagebox.showerror(title="Greška", message="Greška prilikom postavljanja strijelca.")

    def update_shooters(self):
        shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters()

        for shooter in shooters:
            self.shooters[f"{shooter['Ime']} {shooter['Prezime']} ({shooter['Datum']})"] = shooter['id']

        self.cbx_shooters.configure(
            values=[name for name in self.shooters]
        )
        self.refresh()
        # ovdje ce biti problema kod refresha


class WeaponImages(ImageCrop):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.images = []
        self.index = 0

        self.frame_cropped.grid_forget()
        self.frame_buttons.grid(row=0, column=1, sticky="nsew")

        self.frame_additional = tk.Frame(self)

        self.btn_load_image.configure(text="Dodaj")

        self.btn_delete = tk.Button(
            self.frame_additional,
            text="Obriši",
            font=self.font,
            command=lambda: self.remove()
        )

        self.btn_next = tk.Button(
            self.frame_additional,
            text=">",
            font=self.font,
            command=lambda: self.next()
        )

        self.btn_previous = tk.Button(
            self.frame_additional,
            text="<",
            font=self.font,
            command=lambda: self.previous()
        )

        self.lbl_no_of_images = tk.Label(
            self.frame_additional,
            text="/",
            font=self.font
        )

        for y in range(0, 5, 1):
            self.frame_additional.rowconfigure(y, weight=1, uniform="rows")

        self.frame_additional.columnconfigure(0, weight=3, uniform="cols")
        self.frame_additional.columnconfigure(1, weight=3, uniform="cols")

        self.btn_delete.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.btn_next.grid(row=2, column=1, sticky="nsew")
        self.btn_previous.grid(row=2, column=0, sticky="nsew")

        self.lbl_no_of_images.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.btn_save_cropped.grid_forget()

        self.frame_additional.grid(row=1, column=1, sticky="nsew")

        self.columnconfigure(0, weight=10, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")

        self.btn_load_image.configure(command=lambda: self.add_image())

        self.canvas_full.bind("<Double-Button-1>", self.open_image_in_default_os_application)

    def open_image_in_default_os_application(self, event=None):
        os.startfile(ApplicationProperties.WEAPON_IMAGES_DIR + self.images[self.index])

    def remove(self):
        if not self.images:
            return

        if not messagebox.askyesnocancel(title="Brisanje", message="Jeste li sigurni da želite obrisati trenutnu sliku?"):
            return

        os.remove(ApplicationProperties.WEAPON_IMAGES_DIR + self.images[self.index])
        self.refresh()

    def refresh(self):
        self.load_images()
        self.set_no_of_images_lbl()

    def previous(self):
        if not self.images:
            return
        if self.index == 0:
            self.index = len(self.images) - 1
        else:
            self.index -= 1
        self.load_image()
        self.set_no_of_images_lbl()

    def next(self):
        if not self.images:
            return
        if self.index == len(self.images) - 1:
            self.index = 0
        else:
            self.index += 1
        self.load_image()
        self.set_no_of_images_lbl()

    def load_images(self):
        self.images.clear()
        self.index = 0
        for path in os.listdir(ApplicationProperties.WEAPON_IMAGES_DIR):
            if path[0:len(str(ManageArms.current_weapon_id)) + 1] == str(ManageArms.current_weapon_id) + "_":
                self.images.append(path)

        if not self.images:
            self.canvas_full.delete("all")
            return

        self.load_image()

    def set_no_of_images_lbl(self):
        self.lbl_no_of_images.configure(text=f"{self.index + 1}/{len(self.images)}")

    def load_image(self):
        try:
            self.image = Image.open(
                ApplicationProperties.WEAPON_IMAGES_DIR + self.images[self.index]
            ).convert('RGBA')
        except (FileNotFoundError, PermissionError):
            return

        image_topleft_x_pos, image_topleft_y_pos, self.image_width, self.image_height = self.image.getbbox()

        self.adjust_image_in_canvas_full()

    def add_image(self):
        """Returns True if image is added, False if not"""
        file = filedialog.askopenfilename(title="Choose image", filetypes=[('Image', self.supported_load_filetypes)])
        if file:
            self.image = Image.open(file)
            self.image.save(
                ApplicationProperties.WEAPON_IMAGES_DIR + f"{ManageArms.current_weapon_id}_{os.path.basename(file)}"
            )
            self.refresh()
            return True
        return False


class WeaponServiceInformation(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.bg_colors = {
            True: "#ffff00",
            False: "#ffffff"
        }
        self.bg_color = True

        self.font = tkFont.Font(size=14)

        self.btn_add_service_detail = tk.Button(
            self,
            text="Dodaj servis",
            bg="lime",
            font=self.font,
            command=lambda: self.add_service_detail()
        )

        self.frame_main = ScrollableFrame.Vertical(self)

        self.btn_add_service_detail.pack(side="top", fill="x")
        self.frame_main.pack(side="bottom", expand=True, fill="both")

    def list_services(self):
        for child in self.frame_main.scrollable_frame.winfo_children():
            child.destroy()

        services = DBGetter.get_weapon_services(ManageArms.current_weapon_id)
        for service in services:
            s = WeaponServiceDetailsReadonly(
                self.frame_main.scrollable_frame,
                service_id=service['id'],
                note=service['note'],
                date=service['date'],
                height=300,
                pady=50
            )
            s.pack(side="top", fill="x")
            s.set_bg(self.bg_colors[self.bg_color])
            self.bg_color = not self.bg_color
            s.keep_aspect_ratio()

    def refresh(self):
        self.list_services()

    def add_service_detail(self):
        w = WeaponServiceDetailsToplevel(
            self,
            weapon_id=ManageArms.current_weapon_id
        )
        w.grab_set()
        w.wait_window()
        self.refresh()


class WeaponServiceDetailsToplevel(tk.Toplevel):
    def __init__(self, parent, weapon_id: int, service_id=0, note="", date=str(ApplicationProperties.CURRENT_DATE), **kwargs):
        super().__init__(parent, **kwargs)

        self.font = tkFont.Font(size=14)

        self.geometry("{}x{}".format(600, 400))

        self.btn_save = tk.Button(
            self,
            text="Spremi",
            bg="lime",
            font=self.font,
            command=lambda: self.save_and_exit()
        )

        self.frame_main = WeaponServiceDetails(
            self,
            service_id=service_id,
            weapon_id=weapon_id,
            note=note,
            date=date
        )

        self.frame_main.pack(side="top", expand=True, fill="both")
        self.btn_save.pack(side="bottom", fill="x")

    def save_and_exit(self):
        self.frame_main.save()
        self.destroy()


class WeaponServiceDetailsReadonly(tk.Frame):
    def __init__(self, parent, note: str, date: str, service_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.service_id = service_id

        self.font = Fonts.fonts2["WeaponServiceDetailsReadonly"]["font"]

        self.menu = tk.Menu(self, tearoff=0, font=self.font)
        self.menu.add_command(label="Uredi", command=lambda: self.edit())
        self.menu.add_separator()
        self.menu.add_command(label="Obriši", command=lambda: self.delete())

        self.lbl_note = tk.Label(
            self,
            font=self.font,
            text=note,
            justify="left",
            anchor="w",
            bd=5
        )

        self.lbl_date = tk.Label(
            self,
            font=self.font,
            text=Tools.SQL_date_format_to_croatian(date),
            justify="left",
            bd=5
        )

        self.lbl_date.pack(side="top", fill="x")
        self.lbl_note.pack(side="top", fill="x", pady=20)

        for child in self.winfo_children():
            child.bind("<Button-3>", self.show_menu)
        self.bind("<Button-3>", self.show_menu)

        KeepAspectRatio.subscribe(self)

    def refresh(self):
        details = DBGetter.get_service_details(self.service_id)
        if not details:
            return
        self.lbl_note.configure(text=details['note'])
        self.lbl_date.configure(text=Tools.SQL_date_format_to_croatian(details['date']))
        self.keep_aspect_ratio()

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def delete(self):
        if not DBRemover.delete_weapon_service(self.service_id):
            messagebox.showerror(
                title="Greška",
                message="Greška prilikom uklanjanja servisa oružja."
            )
        
    def edit(self):
        w = WeaponServiceDetailsToplevel(
            self,
            service_id=self.service_id,
            weapon_id=ManageArms.current_weapon_id,
            note=self.lbl_note.cget("text"),
            date=Tools.croatian_date_format_to_SQL(self.lbl_date.cget("text"))
        )
        w.grab_set()
        w.wait_window()
        self.refresh()

    def keep_aspect_ratio(self):
        self.lbl_note.configure(wraplength=self.winfo_width() - 20)

    def set_bg(self, bg: str):
        self.lbl_note.configure(bg=bg)
        self.lbl_date.configure(bg=bg)
        self.configure(bg=bg)


class WeaponServiceDetails(tk.Frame):
    def __init__(self, parent, service_id, weapon_id: int, note: str, date: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.weapon_id = weapon_id
        self.service_id = service_id

        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=10, uniform="cols")
        self.columnconfigure(2, weight=20, uniform="cols")
        self.columnconfigure(3, weight=1, uniform="cols")

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=4, uniform="rows")
        self.rowconfigure(2, weight=4, uniform="rows")
        self.rowconfigure(3, weight=4, uniform="rows")
        self.rowconfigure(4, weight=24, uniform="rows")
        self.rowconfigure(5, weight=1, uniform="rows")

        self.font = tkFont.Font(size=14)

        self.grid_propagate(False)

        self.lbl_date = tk.Label(
            self,
            text="Datum:",
            font=self.font
        )

        self.lbl_note = tk.Label(
            self,
            text="Napomena:",
            font=self.font
        )

        self.txt_note = tk.Text(
            self,
            font=self.font,
            bd=5,
        )
        self.date_service = DateEntry2(
            self,
            selectmode="day",
            locale="hr_HR",
            font=self.font
        )
        self.txt_note.insert("1.0", note)
        self.date_service.set_date(Tools.SQL_date_format_to_croatian(date))

        self.lbl_date.grid(row=1, column=1, sticky="nsw")
        self.date_service.grid(row=2, column=1, sticky="nsew")

        self.lbl_note.grid(row=3, column=1, sticky="nsw")
        self.txt_note.grid(row=4, column=1, columnspan=2, sticky="nsew")

    def save(self):
        if self.service_id:
            DBUpdate.update_weapon_service(
                weapon_id=self.weapon_id,
                service_id=self.service_id,
                note=self.txt_note.get("1.0", tk.END)[:-1],
                date=str(self.date_service.get_date())
            )
            return
        DBAdder.add_weapon_service(
            weapon_id=self.weapon_id,
            note=self.txt_note.get("1.0", tk.END)[:-1],
            date=str(self.date_service.get_date())
        )


class AirCylindersToplevel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.mouse_click = False

        self.geometry("{}x{}".format(800, 600))
        #self.resizable(False, False)

        self.frame_main = AirCylinders(self)

        self.frame_main.pack(expand=True, fill="both")
        self.after(10, self.frame_main.load_air_cylinders)


class AirCylinders(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.font = tkFont.Font(size=14)

        #self.grid_propagate(False)

        self.treeview_columns_dict = {
            "Serijski broj": 1,
            "Proizvođač": 1,
            "Duljina (mm)": 1,
            "Kapacitet (hitaca)": 1,
            "Masa (g)": 1,
            "Maksimalni pritisak (bar)": 1,
            "Promjer (mm)": 1,
            "id": 0,
            "Vrijedi do": 1
        }

        self.treeview_column_widths = {
            "Serijski broj": 100,
            "Proizvođač": 100,
            "Duljina (mm)": 100,
            "Kapacitet (hitaca)": 100,
            "Masa (g)": 100,
            "Maksimalni pritisak (bar)": 100,
            "Promjer (mm)": 100,
            "id": 1,
            "Vrijedi do": 100
        }

        self.treeview_column_types = {
            "Serijski broj": "str",
            "Proizvođač": "str",
            "Duljina (mm)": "int",
            "Kapacitet (hitaca)": "int",
            "Masa (g)": "int",
            "Maksimalni pritisak (bar)": "int",
            "Promjer (mm)": "int",
            "id": "int",
            "Vrijedi do": "date"
        }

        self.tree_air_cylinders = ResultsTree(
            self,
            self,
            self.treeview_columns_dict,
            self.treeview_column_widths,
            self.treeview_column_types, "AirCylindersTree",
            Fonts.fonts2["AirCylinders"]["treeview"]["font"]
        )

        self.tree_air_cylinders.set_colors(
            odd_row_bg="#ffffff",
            even_row_bg="#aaaaaa",
            odd_row_fg="#000000",
            even_row_fg="#000000"
        )

        self.frame_commands = tk.Frame(self)

        self.frame_commands.rowconfigure(0, weight=1)
        for x in range(0, 8, 1):
            self.frame_commands.columnconfigure(x, weight=1, uniform="cols")

        self.btn_add = tk.Button(
            self.frame_commands,
            text="Dodaj",
            bg="lime",
            font=self.font,
            command=lambda: self.add_air_cylinder()
        )

        self.btn_remove = tk.Button(
            self.frame_commands,
            text="Obriši",
            bg="red",
            font=self.font,
            command=lambda: self.delete_air_cylinder()
        )

        self.btn_edit = tk.Button(
            self.frame_commands,
            text="-- UREDI --",
            font=self.font,
            bg="yellow",
            command=lambda: self.update_air_cylinder_details()
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=18, uniform="rows")
        self.rowconfigure(1, weight=1, uniform="rows")

        self.btn_add.grid(row=0, column=7, sticky="nsew")
        self.btn_edit.grid(row=0, column=3, columnspan=2, sticky="nsew")
        self.btn_remove.grid(row=0, column=0, sticky="nsew")

        self.tree_air_cylinders.grid(row=0, column=0, sticky="nsew")
        self.frame_commands.grid(row=1, column=0, sticky="ew")

    def update_air_cylinder_details(self):
        details = self.tree_air_cylinders.get_values_of_selected_row()
        if not details:
            return
        ac = AddNewAirCylinderToplevel(self, details['id'])
        ac.title("Uredi zračni cilindar")
        ac.grab_set()
        ac.wait_window()
        self.load_air_cylinders()
        Changes.call_refresh_air_cylinders()

    def delete_air_cylinder(self):
        values = self.tree_air_cylinders.get_values_of_selected_row()
        if not values:
            return
        if not messagebox.askyesno(
            title="Brisanje zračnog cilindra",
            message=f"Jeste li sigurni da želite obrisati cilindar {values['Serijski broj']} - {values['Proizvođač']}?"
        ):
            return
        if not DBRemover.delete_air_cylinder(values['id']):
            messagebox.showerror(title="Greška", message="Greška prilikom brisanja zračnog cilindra.")
            return
        self.load_air_cylinders()
        Changes.call_refresh_air_cylinders()

    def add_air_cylinder(self):
        a = AddNewAirCylinderToplevel(self, 0)
        a.grab_set()
        a.wait_window()
        self.load_air_cylinders()
        Changes.call_refresh_air_cylinders()

    def load_air_cylinders(self):
        self.tree_air_cylinders.ClearTree()
        for air_cylinder in DBGetter.get_air_cylinders():
            self.tree_air_cylinders.AddResultToTree(
                {
                    "Serijski broj": air_cylinder['serial_no'],
                    "Proizvođač": air_cylinder['manufacturer'],
                    "Duljina (mm)": air_cylinder['length'],
                    "Kapacitet (hitaca)": air_cylinder['capacity'],
                    "Masa (g)": air_cylinder['mass'],
                    "Maksimalni pritisak (bar)": air_cylinder['max_pressure'],
                    "Promjer (mm)": air_cylinder['diameter'],
                    "id": air_cylinder['id'],
                    "Vrijedi do": Tools.SQL_date_format_to_croatian(air_cylinder['date_expire'])
                }
            )
        self.tree_air_cylinders.keep_aspect_ratio()
