from tkinter.filedialog import asksaveasfilename
from xlsxwriter.workbook import Workbook
import Tools


def create_workbook(filepath):
    return Workbook(filepath)


def write_to_workbook_sheet(worksheet, data, data_columns=None):
    # write headers

    if data_columns is None:
        y = 0
        for i, key in enumerate(data[0]):
            worksheet.write(y, i, key)

        for y, dictionary in enumerate(data):
            row_values = Tools.dict_to_list(dictionary, "value")
            for x, cell_value in enumerate(row_values):
                worksheet.write(y + 1, x, cell_value)

    else:
        y = 1
        for key, value in data_columns.items():
            worksheet.write(value + str(y), key)
        for y, dictionary in enumerate(data):
            for key, value in data_columns.items():
                worksheet.write(data_columns[key] + str(y + 2), dictionary[key])


def write_dictionaries_to_excel(dictionaries_list, sheet="Dnevnik", columns=None):
    location = asksaveasfilename(title="Izaberite odredište", filetypes=[('Excel', ('.xlsx'))])
    if location:
        if location[-5:] != ".xlsx":
            location += ".xlsx"
        try:
            excel_workbook: Workbook = create_workbook(location)
            worksheet = excel_workbook.add_worksheet(name=sheet)

            write_to_workbook_sheet(worksheet, dictionaries_list, columns)
            excel_workbook.close()
            return True
        except Exception:
            return False


def add_workbook_sheet(workbook: Workbook, sheet_name: str):
    Workbook.add_worksheet(workbook, name=sheet_name)


def close_workbook(workbook: Workbook):
    workbook.close()
