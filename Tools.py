from typing import List
from datetime import datetime
from tkinter import colorchooser
import ApplicationProperties
import os


croatian_date_format = "%d. %m. %Y."
sql_date_format = "%Y-%m-%d"


def Unicode32to16(utf_32):
    # convert/encode it to UTF-16 (big endiann), to get a bytes object

    utf_16 = utf_32.encode('utf-16-be')

    # obtain the hex representation
    utf_16 = utf_16.hex()

    # format it to be an escaped UTF-16 tcl string
    utf_16_out = '\\u{}\\u{}'.format(utf_16[0:4], utf_16[4:8])
    return utf_16_out


def TranslateCategoriesToList(categories: int):
    categories_list = ["KAD", "JUN", "SEN", "VET"]
    array = []
    for i in range(3, -1, -1):
        if categories // pow(2, i) > 0:
            categories -= pow(2, i)
            array.append(categories_list[i])
    array.reverse()
    return array

def TranslateCategoriesToInt(categories: List):
    """ KAD = 2^0, JUN = 2^1, SEN = 2^2, VET = 2^3 """
    categories_list = ["KAD", "JUN", "SEN", "VET"]
    value = 0
    for element in categories:
        value += pow(2, categories_list.index(element))
    return value


def dict_to_list(dictionary: dict, by: str):
    """by = 'key" or 'value' """
    supported = ["key", "value"]
    if by not in supported:
        return f"Error, '{by}' is not a supported keyword"
    values = []
    for key, value in dictionary.items():
        if by == "key":
            values.append(key)
        elif by == "value":
            values.append(value)
    return values


def longest_string_in_list(elements):
    try:
        return max(elements, key=len)
    except ValueError:
        return ""


def SQL_date_format_to_croatian(date: str):
    """'%Y-%m-%d -> '%d. %m. %Y.'"""
    result = ""
    if date == "1000-01-01":
        return result
    try:
        result = datetime.strptime(date, sql_date_format).strftime(croatian_date_format)
    except:
        result = ""
    finally:
        return result


def SQL_date_to_datetime_date(date: str):
    """'%Y-%m-%d' -> datetime.date"""
    return datetime.strptime(date, sql_date_format).date()


def croatian_date_from_utc_milliseconds(utc_: int):
    return datetime.fromtimestamp(utc_ // 1000).strftime(croatian_date_format)


def croatian_date_format_to_SQL(date: str):
    """"%d. %m. %Y. -> %Y-%m-%d"""
    result = ""
    try:
        result = datetime.strptime(date, croatian_date_format).strftime(sql_date_format)
    except:
        result = ""
    finally:
        return result


def color_picker():
    color = colorchooser.askcolor(title="Izaberite boju")
    if color:
        return color[1]
    return ""


def fixed_map(style, style_name, option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map(style_name, query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]

    # style = ttk.Style()
    # style.map('Treeview', foreground=fixed_map('foreground'),
    #   background=fixed_map('background'))


def allow_only_integer(P):
    # self.validate_integer = (self.register(self.allow_only_integer))
    if not P:
        return True
    try:
        int(P)
        return True
    except (AttributeError, ValueError):
        return False


def allow_only_positive_integer(P):
    if allow_only_integer(P):
        if P > 0:
            return True
    return False


def check_all_elements_contained_in_list1(all_elements: List, list1: List):
    total = len(all_elements)
    no_of = 0

    for x in all_elements:
        if x in list1:
            no_of += 1

    return total == no_of


def clone_widget(widget, master=None):
    """
    Create a cloned version o a widget

    Parameters
    ----------
    widget : tkinter widget
        tkinter widget that shall be cloned.
    master : tkinter widget, optional
        Master widget onto which cloned widget shall be placed. If None, same master of input widget will be used. The
        default is None.

    Returns
    -------
    cloned : tkinter widget
        Clone of input widget onto master widget.

    """
    # Get main info
    parent = master if master else widget.master
    cls = widget.__class__

    # Clone the widget configuration
    cfg = {key: widget.cget(key) for key in widget.configure()}
    cloned = cls(parent, **cfg)

    # Clone the widget's children
    for child in widget.winfo_children():
        child_cloned = clone_widget(child, master=cloned)
        if child.grid_info():
            grid_info = {k: v for k, v in child.grid_info().items() if k not in {'in'}}
            child_cloned.grid(**grid_info)
        elif child.place_info():
            place_info = {k: v for k, v in child.place_info().items() if k not in {'in'}}
            child_cloned.place(**place_info)
        else:
            print(child)
            pack_info = {k: v for k, v in child.pack_info().items() if k not in {'in'}}
            child_cloned.pack(**pack_info)

    return cloned


def remove_weapon_images(weapon_id: int):
    for path in os.listdir(ApplicationProperties.WEAPON_IMAGES_DIR):
        if path[0:len(str(weapon_id)) + 1] == str(weapon_id) + "_":
            os.remove(path)


def string_to_datetime_date(date: str, date_format: str = sql_date_format):
    return datetime.strptime(date, date_format).date()
