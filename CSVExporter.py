import csv
import Tools
from typing import List, Dict


def write_to_csv(path: str, headers: List = None, data: List[List] = None):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if headers:
            writer.writerow(headers)
        if data:
            for row in data:
                writer.writerow(row)


def write_dict_to_csv(path: str, data: Dict):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(Tools.dict_to_list(data[0], "key"))
        for row in data:
            writer.writerow(Tools.dict_to_list(row, "value"))