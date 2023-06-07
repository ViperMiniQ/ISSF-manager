from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4
from typing import List


def single_image_A4_size_pdf(image_path: str, filename: str, image_pixel_width: int, image_pixel_height: int):
    """A4 size is (595.2755905511812, 841.8897637795277) pixels"""
    image_x = 75
    image_y = 700

    pdf_canvas = canvas.Canvas(
        filename=f"{filename}.pdf",
        pagesize=A4
    )

    pdf_canvas.drawImage(image_path, image_x, image_y, width=image_pixel_width, height=image_pixel_height)
    pdf_canvas.showPage()
    pdf_canvas.save()


def images_to_A4_size_pdf(filename: str, images: List[tuple]):
    """A4 size is (595.2755905511812, 841.8897637795277) pixels"""
    pdf_canvas = canvas.Canvas(
        filename=f"{filename}.pdf",
        pagesize=A4
    )

    page = 0
    for coords in images:
        if coords[1] > page:
            pdf_canvas.showPage()
            page = coords[1]
        pdf_canvas.drawImage(coords[0], coords[2], coords[3], width=coords[4], height=coords[5])
    pdf_canvas.save()

