import datetime
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json


class CompetitionNotExists(Exception):
    def __init__(self, competition_id, *args):
        super().__init__(args)
        self.competition_id = competition_id

    def __str__(self):
        return f"Webpage for competition with id={self.competition_id} does not exist"


HSS = "https://hss-csf.hr"

COMPETITION_PAGE = "/Public/Natjecanje.aspx?id="
CALENDAR_PAGE = "/Public/KalendarDogadaji.aspx"

COMPETITION_PAGE_DATE_FORMAT = "%d.%m.%Y."
SQL_DATE_FORMAT = "%Y-%m-%d"

DOCUMENTS = ['Startne liste', 'Pozivno pismo', 'Bilten']


def download_and_save_competition_documents(competition_id: int, filename: str, path: str, document: str) -> str:
    if document not in DOCUMENTS:
        raise f"Wrong document argument, possible {[d for d in DOCUMENTS]}"

    page = requests.get(HSS + COMPETITION_PAGE + str(competition_id))

    soup = BeautifulSoup(page.text, 'html.parser')

    links = soup.find_all('a')

    document_link = ""
    for link in links:
        if link.text.strip() == document:
            document_link = link['href']

    if not document_link:
        return ""

    document_content = requests.get(HSS + document_link)
    extension = ""

    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        extension = document_link.split('.')[-1]
        filename = Path(path + filename + '.' + extension)
        filename.write_bytes(document_content.content)
    except Exception:
        extension = ""
    finally:
        return extension


def get_competitions(utc_start: int, utc_end: int):
    payload = {
        "from=": utc_start,
        "to=": utc_end,
        "utc_offset_from=": -60,
        "utc_offset_to=": -60,
        "browser_timezone=": "Europe%2FBerlin"
    }

    link = HSS + CALENDAR_PAGE + "?"
    link_payload = link
    for key, value in payload.items():
        link_payload += str(key) + str(value) + "&"
    link_payload = link_payload[:-1]

    web_competitions = json.loads(requests.get(url=link_payload).text)

    # competition = {
    #     "id": int,
    #     "Naslov": str,
    #     "DatumPocetak": datetime.datetime,
    #     "DatumKraj": datetime.datetime,
    #     "Mjesto": str,
    # }

    competitions = []

    for c in web_competitions["result"]:
        if "Natjecanje" in c["url"]:
            competition = {
                "id": c['id'],
                "Naziv": c['title'].split('|')[1],
                "utc_start": c['start'], 
                "utc_end": c['end'], 
                "Mjesto": c['title'].split('|')[2]
            }
            competitions.append(competition)

    return competitions


def get_competition_details(competition_id: int):
    page = requests.get(HSS + COMPETITION_PAGE + str(competition_id))
    soup = BeautifulSoup(page.text, "html.parser")

    if "Invalid attempt to read when no data is present" in soup.text:
        raise CompetitionNotExists(competition_id) 

    name = soup.find(attrs={"class": "lang", "id": "msg_clanak"}).text
    date_n_place = soup.find(attrs={"class": "event_date"}).text

    try:
        if len(date_n_place.split()) > 2:
            date = date_n_place.split()[2] + date_n_place.split()[3]
        else:
            date = date_n_place.split()[0]
    except Exception:
        date = datetime.date.today().strftime(COMPETITION_PAGE_DATE_FORMAT)

    place = date_n_place.split()[-1]
    date = datetime.datetime.strptime(date, COMPETITION_PAGE_DATE_FORMAT).strftime(SQL_DATE_FORMAT)

    return name, date, place
