import os
import ApplicationProperties


needed_dirs = {
    "Config": {
        "Settings": {}
    },
    "Data": {
        "barcode": {
            "images": {},
            "pdf": {}
        },
        "BIB": {},
        "Bilteni": {},
        "Ikona": {},
        "Images": {},
        "Lijecnicki": {},
        "Oruzje": {},
        "Pozivno_pismo": {},
        "QR": {
            "images": {},
            "pdf": {}
        },
        "Startne liste": {}
    }
}


def _create_dir(path: str):
    os.mkdir(path)


def _create_missing_dirs(directory, current):
    for key, value in current.items():
        if os.path.isdir(directory + "/" + key):
            continue
        _create_dir(directory + "/" + key)
        if value:
            _create_missing_dirs(directory + "/" + key, value)


def set_all():
    _create_missing_dirs(ApplicationProperties.LOCATION, needed_dirs)
