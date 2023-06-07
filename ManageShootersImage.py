import tkinter as tk
from PIL import ImageTk, Image

import ApplicationProperties
import ImageCrop


class ShooterImage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.controller = parent
        self.image = None
        self.canvas_img = None
        self.no_profile_image_path = "no_profile.png"
        self.image_filename_to_save_as = ""
        self.image_path = ApplicationProperties.SHOOTER_IMAGES_DIR
        self.image_extension = ".png"

        self.shooter_id: int = 0

        self.canv_shooter_image = tk.Canvas(
            self,
            width=210,
            height=240,
            bg="gray80"
        )

        self.canv_shooter_image.pack(expand=True, fill="both")

        self.load_shooter_image("ding_dong")

    def ClassImageCrop(self, event=None):
        image_crop = ImageCrop.ImageCropToplevel(self)
        image_crop.geometry('{}x{}'.format(800, 450))
        image_crop.wait_window()
        if image_crop.frame_main.cropped_image is not None:
            self.image = image_crop.frame_main.cropped_image
            self.image.save(self.image_path + str(self.shooter_id) + self.image_extension)
            self.AdjustImages()

    def load_shooter_image(self, path: str):
        try:
            self.image = Image.open(path)
            self.AdjustImages()
        except (FileNotFoundError, PermissionError):
            self.LoadNoProfileImage()
            self.RemoveImage()

    def SetNoProfileImage(self, path):
        try:
            self.image = Image.open(path)
            self.no_profile_image_path = path
        except (FileNotFoundError, PermissionError):
            self.image = None

    def LoadNoProfileImage(self):
        try:
            self.image = Image.open(self.no_profile_image_path)
        except (FileNotFoundError, PermissionError):
            self.image = None

    def SetImageFilepath(self, image_path: str):
        self.image_path = image_path

    def UpdateValues(self, shooter_id: int):
        self.shooter_id = shooter_id
        self.load_shooter_image(ApplicationProperties.SHOOTER_IMAGES_DIR + str(shooter_id) + self.image_extension)

    def SetImageTitle(self, title: str):
        self.image_filename_to_save_as = title

    def RemoveImage(self):
        self.canv_shooter_image.delete("all")

    def ready_image_select(self):
        self.canv_shooter_image.bind("<Button-1>", self.ClassImageCrop)

    def WaitImageSelect(self):
        self.canv_shooter_image.unbind_all("<Button-1>")

    def AdjustImages(self):
        self.update()
        x_cropped = self.canv_shooter_image.winfo_width()
        y_cropped = self.canv_shooter_image.winfo_height()
        self.canvas_img = self.image.resize((x_cropped,y_cropped), Image.ANTIALIAS)
        self.canvas_img = ImageTk.PhotoImage(self.canvas_img)
        self.canv_shooter_image.create_image(0,0, image=self.canvas_img, anchor="nw")
