import logging
import sqlite3

import ApplicationProperties
import Tools
import sqlTypes
from typing import List
import datetime


# should replace entire module with SQLALCHEMY module for database manipulation


class DBConnector:
    filepath = ""

    @classmethod
    def set_db_filepath(cls, filepath):
        cls.filepath = filepath

    @classmethod
    def create_connection(cls):
        return sqlite3.connect(cls.filepath, check_same_thread=False)


class DBRemover:
    @classmethod
    def delete_weapon(cls, weapon_id: int):
        query = f"""
        DELETE FROM oruzje WHERE id={weapon_id}
        """

        if not DBManipulator.execute_query(query):
            return False

        query_remove_from_air_cylinders = f"""
        UPDATE cilindar_za_zrak
        SET id_oruzje=0
        WHERE id_oruzje={weapon_id}
        """

        return DBManipulator.execute_query(query_remove_from_air_cylinders)

    @classmethod
    def delete_weapon_service(cls, service_id: int):
        query = f"""
        DELETE FROM oruzja_servis WHERE id={service_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def delete_air_cylinder(cls, air_cylinder_id: int):
        query = f"""
        DELETE FROM cilindar_za_zrak WHERE id={air_cylinder_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def delete_program(cls, program) -> bool:
        if isinstance(program, int):
            query = f"""
            DELETE FROM programi WHERE id_program={program}
            """
        elif isinstance(program, str):
            query = f"""
            DELETE FROM programi WHERE naziv='{program}'
            """
        else:
            return False
        return DBManipulator.execute_query(query)

    @classmethod
    def delete_discipline(cls, discipline) -> bool:
        if isinstance(discipline, int):
            query = f"""
            DELETE FROM discipline WHERE id_disciplina={discipline}
            """
        elif isinstance(discipline, str):
            query = f"""
            DELETE FROM discipline WHERE naziv='{discipline}'
            """
        else:
            return False
        return DBManipulator.execute_query(query)

    @classmethod
    def delete_target(cls, target) -> bool:
        if isinstance(target, int):
            query = f"""
            DELETE FROM mete WHERE id_meta={target}
            """
        elif isinstance(target, str):
            query = f"""
            DELETE FROM mete WHERE naziv='{target}'
            """
        else:
            return False
        return DBManipulator.execute_query(query)


    @classmethod
    def delete_note(cls, note_id: int):
        query = f"""DELETE FROM napomene WHERE id_napomena={note_id}"""
        return DBManipulator.execute_query(query)

    @classmethod
    def delete_all_shooter_results(cls, shooter_id: int):
        delete = f"""
        DELETE FROM dnevnik WHERE strijelac_id={shooter_id}
        """
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_all_shooters_at_competition(cls, competition_id: int, rifle: int):
        delete = f"""
        DELETE FROM strijelci_na_natjecanju 
        WHERE id_natjecanja={competition_id} 
            AND kategorija={rifle}
        """
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_all_downloaded_hss_natjecanja(cls):
        delete = "DELETE FROM hss_natjecanja"
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_competition_bilten_path(cls, competition_id: int):
        delete = f"""
        UPDATE natjecanja SET bilten_path=NULL WHERE id_natjecanja={competition_id}
        """
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_competition_startne_liste_path(cls, competition_id: int):
        delete = f"""
        UPDATE natjecanja SET startne_liste_path=NULL WHERE id_natjecanja={competition_id}
        """
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_competition_pozivno_pismo(cls, competition_id: int):
        delete = f"""
        UPDATE natjecanja SET pozivno_pismo_path=NULL WHERE id_natjecanja={competition_id}
        """
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_shooter(cls, shooter_id: int):
        if DBChecker.check_shooter_id_exists(shooter_id):
            delete = f"""
            DELETE FROM strijelci WHERE id_strijelac={shooter_id}
            """
            return DBManipulator.execute_query(delete)
        return False

    @classmethod
    def delete_shooter_additional_info(cls, shooter_id: int):  # pff... too tired, needs something better
        delete_hss_info_query = (f"UPDATE strijelci_hss SET oib='', mjesto_rod='', adresa='', mjesto_stan='', hss='', "
                                 f"oi='', oi_trajna=0, oi_datum='1970-01-01', oi_mjesto='', putovnica='', "
                                 f"putovnica_datum='1970-01-01', putovnica_postoji=1, putovnica_mjesto='', "
                                 f"drzavljanstvo='', strucna_sprema='', zaposlenje='', hobi='', banka='', ziro='', "
                                 f"telefon_kuca='', telefon_posao='', mobitel_1='', mobitel_2='', email='', "
                                 f"registracija=0, obavijesti=0, lijecnicki='1970-01-01' WHERE id_strijelac={shooter_id}")
        return DBManipulator.execute_query(delete_hss_info_query)

    @classmethod
    def remove_doctors_pdf(cls, pdf_id: int):
        delete = f"DELETE FROM pdf_lijecnicki WHERE id={pdf_id}"
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_season(cls, pdf_id: int):
        delete = f"DELETE FROM registracije WHERE id={pdf_id}"
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_result(cls, result_id: int):
        delete = f"DELETE FROM dnevnik WHERE id={result_id}"
        return DBManipulator.execute_query(delete)

    @classmethod
    def delete_competition_from_results(cls, competition_id: int):
        update = f"UPDATE dnevnik SET natjecanje=0 WHERE natjecanje={competition_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def delete_competition(cls, competition_id: int):
        delete = f"DELETE FROM natjecanja WHERE natjecanja.id_natjecanja={competition_id}"
        if DBManipulator.execute_query(delete):
            return cls.delete_competition_from_results(competition_id)
        return False


class DBTriggers:
    @classmethod
    def create_trigger_novi_profil_strijelci_pozicije_nakon_novog_strijelca(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_strijelci_pozicije_nakon_novog_strijelca AFTER INSERT ON strijelci 
        BEGIN
            INSERT INTO strijelci_pozicije (id_strijelac, pozicija) VALUES (
                NEW.id_strijelac, (SELECT MAX(pozicija)+1 FROM strijelci_pozicije));
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_novi_profil_mete_pozicije_nakon_nove_mete(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_mete_pozicije_nakon_nove_mete AFTER INSERT ON mete
        BEGIN
            INSERT INTO mete_pozicije (id_meta, pozicija) VALUES (
                NEW.id_meta, (SELECT MAX(pozicija)+1 FROM mete_pozicije));
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_novi_profil_programi_pozicije_nakon_novog_programa(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_programi_pozicije_nakon_novog_programa AFTER INSERT ON programi
        BEGIN
            INSERT INTO programi_pozicije (id_program, pozicija) VALUES (
                NEW.id_program, (SELECT MAX(pozicija)+1 FROM programi_pozicije));
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_novi_profil_discipline_pozicije_nakon_nove_discipline(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_discipline_pozicije_nakon_nove_discipline AFTER INSERT ON discipline
        BEGIN
            INSERT INTO discipline_pozicije (id_disciplina, pozicija) VALUES (
                NEW.id_disciplina, (SELECT MAX(pozicija)+1 FROM discipline_pozicije));
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_novi_profil_natjecanja_pozicije_nakon_novog_natjecanja(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_natjecanja_pozicije_nakon_novog_natjecanja AFTER INSERT ON natjecanja
        BEGIN
            INSERT INTO natjecanja_pozicije (id_natjecanja, pozicija) VALUES (
                NEW.id_natjecanja, (SELECT MAX(pozicija)+1 FROM natjecanja_pozicije));
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_hss_info_nakon_novog_strijelca(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_strijelci_hss_nakon_novog_strijelca AFTER INSERT ON strijelci
        BEGIN
            INSERT INTO strijelci_hss VALUES( --9
                NEW.id_strijelac, '', '', -- 0
                '', '', '',  -- 1
                '', 1, '1970-01-01', -- 2 
                '', '', '1970-01-01',  -- 3
                1, '',  -- 4
                '', '', '', -- 5
                '', '', '', -- 6
                '', '', '', -- 7
                '', '', 1, --8 
                0, '1970-01-01'); -- 9
        END;
        """
        DBManipulator.execute_query(trigger)

    @classmethod
    def create_trigger_novi_profil_strijelci_obavijesti_nakon_novog_strijelca(cls):
        trigger = """
        CREATE TRIGGER IF NOT EXISTS novi_profil_strijelci_obavijesti_nakon_novog_strijelca AFTER INSERT ON strijelci
        BEGIN
            INSERT INTO strijelci_obavijesti (id_strijelac, osobna, lijecnicki, putovnica, rodjendan) VALUES (
                NEW.id_strijelac, 1, 1, 0, 1);
        END;
        """
        DBManipulator.execute_query(trigger)


class DBMisc:
    @classmethod
    def weapons_table_with_headers(cls):
        query = f"""
        SELECT 
            id, -- 0
            vrsta, -- 1
            tip, -- 2
            serijski_broj, -- 3
            proizvodjac, -- 4
            model, -- 5
            duljina, -- 6
            visina, -- 7
            sirina, -- 8
            duljina_cijevi, -- 9
            kalibar, -- 10
            materijal, -- 11
            masa_okidanja_od, -- 12
            masa_okidanja_do, -- 13
            drska_ruka, -- 14
            drska_velicina, -- 15
            napomena, -- 16
            strijelci.prezime || ' ' || strijelci.ime AS strijelac -- 17
        FROM oruzje
        LEFT JOIN strijelci ON strijelci.id_strijelac=oruzje.id_strijelac
        """
        return {
            "data": DBManipulator.fetch_row(query),
            "headers": [
                "ID",  # 0
                "Vrsta",  # 1
                "Tip",  # 2,
                "Serijski broj",  # 3
                "Proizvođač",  # 4
                "Model",  # 5
                "Duljina",  # 6
                "Visina",  # 7
                "Širina",  # 8
                "Duljina cijevi",  # 9
                "Kalibar",  # 10
                "Materijal",  # 11
                "Min. masa okidanja",  # 12
                "Max. masa okidanja",  # 13
                "Drška za",  # 14
                "Veličina drške",  # 15
                "Napomena",  # 16
                "Strijelac",  # 17
            ]
        }

    @classmethod
    def retire_shooter(cls, shooter_id: int):
        query = f"""
        INSERT INTO strijelci_bivsi 
        (
            id_strijelac, 
            datUmirovljenja
        ) 
        VALUES 
        (
            {shooter_id}, 
            DATE('now')
        );
        """
        if DBManipulator.execute_query(query):
            query2 = f"""
            DELETE FROM strijelci_pozicije WHERE id_strijelac={shooter_id}
            """
            return DBManipulator.execute_query(query2)

    @classmethod
    def move_shooter_from_retired_to_active(cls, shooter_id: int):
        if DBChecker.check_ex_shooter_id_exists(shooter_id):
            query = f"""
            DELETE FROM strijelci_bivsi WHERE id_strijelac={shooter_id}
            """
            DBManipulator.execute_query(query)


class DBChecker:
    @classmethod
    def check_shooter_id_exists(cls, shooter_id: int):
        """Returns True if shooter_id exists, False if not"""
        check = f"""
        SELECT EXISTS(SELECT 1 FROM strijelci WHERE id_strijelac={shooter_id});
        """
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_target_id_exists(cls, target_id: int):
        """Returns True if taget_id exists, False if not"""
        check = f"SELECT EXISTS(SELECT 1 FROM mete WHERE id_meta={target_id});"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_discipline_id_exists(cls, discipline_id: int):
        """Returns True if discipline_id exists, False if not"""
        check = f"SELECT EXISTS(SELECT 1 FROM discipline WHERE id_disciplina={discipline_id});"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_program_id_exists(cls, program_id: int):
        """Returns True if program_id exists, False if not"""
        check = f"SELECT EXISTS(SELECT 1 FROM programi WHERE id_program={program_id});"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_ex_shooter_id_exists(cls, shooter_id: int):
        """Returns True if ex shooter_id exists, False if not"""
        check = f"SELECT EXISTS(SELECT 1 FROM strijelci_bivsi WHERE id_strijelac={shooter_id});"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_competition_id_exists(cls, competition_id: int):
        check = f"SELECT EXISTS(SELECT 1 FROM natjecanja WHERE id_natjecanja={competition_id});"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_program_name_exists(cls, name: str):
        check = f"SELECT EXISTS(SELECT 1 FROM programi WHERE naziv='{name}'"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_target_name_exists(cls, name: str):
        check = f"SELECT EXISTS(SELECT 1 FROM mete WHERE naziv='{name}'"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_discipline_name_exists(cls, name: str):
        check = f"SELECT EXISTS(SELECT 1 FROM discipline WHERE naziv='{name}')"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_shooter_name_exists(cls, name: str, lastname: str):
        check = f"SELECT EXISTS(SELECT 1 FROM strijelci WHERE ime='{name}' AND prezime='{lastname}')"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_competition_title_date_exists(cls, title: str, date: str):
        check = f"SELECT EXISTS(SELECT 1 FROM natjecanja WHERE naziv='{title}' AND datum='{date}')"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_weapon_exists(cls, serial_no: str):
        check = f"SELECT EXISTS(SELECT 1 FROM oruzje WHERE serijski_broj='{serial_no}')"
        return DBManipulator.fetch_row(check)[0][0]

    @classmethod
    def check_air_cylinder_exists(cls, serial_no: str):
        check = f"SELECT EXISTS(SELECT 1 FROM cilindar_za_zrak WHERE serijski_broj='{serial_no}')"
        return DBManipulator.fetch_row(check)[0][0]


class DBAdder:
    @classmethod
    def add_weapon_shooter(cls, weapon_id: int, shooter_id: int):
        query = f"""
        INSERT INTO oruzja_strijelci (id_strijelac, id_oruzje) VALUES (
            {shooter_id}, {weapon_id});
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def add_weapon_service(cls, weapon_id: int, note: str, date: str):
        query = f"""INSERT INTO oruzja_servis (oruzje_id, datum, napomena) VALUES(
                    {weapon_id}, '{date}', '{note}')"""
        return DBManipulator.execute_query(query)

    @classmethod
    def add_air_cylinder(cls, serial_no: str):
        if not DBChecker.check_air_cylinder_exists(serial_no):
            query = f"""
            INSERT INTO cilindar_za_zrak (serijski_broj) VALUES ('{serial_no}');
            """
            return DBManipulator.execute_query(query)
        return -1

    @classmethod
    def add_weapon(cls, serial_no: str, manufacturer: str, model: str):
        query = f"""
        INSERT INTO oruzje (serijski_broj, proizvodjac, model) VALUES
        ('{serial_no}', '{manufacturer}', '{model}')
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def add_shooter_to_competition(cls, competition_id: int, shooter_id: int, rifle: int):
        query = f"""
        INSERT INTO strijelci_na_natjecanju (id_natjecanja, id_strijelac, kategorija) VALUES
        ({competition_id}, {shooter_id}, {rifle})
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def add_club(cls, title: str, location: str):
        query = f"""
        INSERT INTO klub (naziv, mjesto) VALUES ('{title}', '{location}');
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def add_competition_values(self, values: sqlTypes.CompetitionInfo) -> int:
        empty = "''"
        insert = f"""
        INSERT INTO natjecanja(
            naziv, -- 0
            mjesto, -- 1
            adresa, -- 2
            datum, -- 3
            program, -- 4
            kategorija, -- 5
            napomena, -- 6
            hss_id
        )
        VALUES(
            '{values["Naziv"]}',
            '{values["Mjesto"]}',
            '{values["Adresa"]}',
            '{values["Datum"]}',
            '{values["Program"]}',
            {values["Kategorija"]},
            '{values["Napomena"]}',
            {values['hss_id'] if values['hss_id'] else empty}
        );
        """
        competition_id = 0
        if DBManipulator.execute_query(insert):
            competition_id = int(DBGetter.get_table_last_row_id("natjecanja"))
        return competition_id

    @classmethod
    def add_hss_natjecanje(cls, competition_id: int, place: str, utc_start: int, utc_end: int, name: str, note: str = ""):
        insert = f"""INSERT INTO hss_natjecanja (id, naziv, utc_start, utc_end, mjesto, napomena) VALUES (
                    {competition_id}, '{name}', {utc_start}, {utc_end}, '{place}', '{note}');"""
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_shooter_registration(cls, shooter_id: int, date_from: str, date_to: str, path: str, get_id: bool = False):
        insert = f"""INSERT INTO registracije (id_strijelac, datum_od, datum_do, path) VALUES (
                    {shooter_id}, '{date_from}', '{date_to}', '{path}');"""
        success = DBManipulator.execute_query(insert)
        if get_id:
            return DBGetter.get_table_last_row_id("registracije")
        return success

    @classmethod
    def add_doctors_pdf(cls, shooter_id: int, path: str, date_from: str, date_to: str, get_id: bool = False):
        insert = f"INSERT INTO pdf_lijecnicki (id_strijelac, datum_od, datum_do, path) VALUES (" \
                 f"{shooter_id}, '{date_from}', '{date_to}', '{path}');"
        success = DBManipulator.execute_query(insert)
        if get_id:
            return DBGetter.get_table_last_row_id("pdf_lijecnicki")
        return success

    @classmethod
    def add_other_reminder(cls, title: str, text: str, date: str, read: bool = False, category: int = 0):
        insert = f"INSERT INTO obavijesti (naslov, tekst, datum, procitana, kategorija) VALUES " \
                 f"('{title}', '{text}', '{date}', {int(read)}, {category})"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_program(cls, name: str, description: str):
        if DBChecker.check_program_name_exists(name):
            return -1
        insert = f"INSERT INTO programi (naziv, opis) VALUES ('{name}', '{description}')"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_target(cls, name: str, description: str):
        if DBChecker.check_target_name_exists(name):
            return -1
        insert = f"INSERT INTO mete (naziv, opis) VALUES ('{name}', '{description}')"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_discipline(cls, name: str, description: str):
        if DBChecker.check_discipline_name_exists(name):
            return -1
        insert = f"INSERT INTO discipline (naziv, opis) VALUES ('{name}', '{description}')"
        return DBManipulator.execute_query(insert)

    @classmethod   # triggers should exist to create profiles in other tables for each new shooter
    def add_shooter(cls, name: str, lastname: str, date_of_birth: str, sex: str):
        if DBChecker.check_shooter_name_exists(name, lastname):
            return -1
        insert = f"INSERT INTO strijelci (ime, prezime, datRod, spol) VALUES (" \
                 f"'{name}', '{lastname}', '{date_of_birth}', '{sex}')"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_competition(cls, title: str, place: str, address: str, date: str, program: str, note: str, category: int):
        if DBChecker.check_competition_title_date_exists(title, date):
            return -1
        insert = f"INSERT INTO natjecanja (naziv, mjesto, adresa, datum, program, kategorija, napomena) VALUES (" \
                 f"'{title}', '{place}', '{address}', '{date}', '{program}', '{category}', '{note}')"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_shooter_note(cls, shooter_id: int, text: str, date: str):
        if not (DBChecker.check_shooter_id_exists(shooter_id) or DBChecker.check_ex_shooter_id_exists(shooter_id)):
            return -1
        insert = f"INSERT INTO strijelci_napomene (id_strijelac, napomena, datum) VALUES (" \
                 f"{shooter_id}, '{text}', '{date}')"
        return DBManipulator.execute_query(insert)

    @classmethod
    def add_result(cls, result: sqlTypes.ResultInput):
        empty = "''"
        insert = f"""
        INSERT INTO dnevnik (
            strijelac_id, -- 0
            datum, -- 1
            disciplina, -- 2
            program, -- 3
            meta, -- 4
            natjecanje, -- 5
            p, -- 6
            r10, -- 7
            r20, -- 8
            r30, -- 9
            r40, -- 10
            r50, -- 11
            r60, -- 12
            rezultat, -- 13
            ineri, -- 14
            napomena -- 15
        ) VALUES (
            {result['idStrijelac']}, -- 0
            '{result['Datum']}',  -- 1
            {result['Disciplina']},  -- 2
            {result['Program']},  -- 3
            {result['Meta']}, -- 4
            {result['idNatjecanja']}, -- 5
            {result['P'] if isinstance(result['P'], (int, float)) else empty}, -- 6
            {result['R10'] if isinstance(result['R10'], (int, float)) else empty}, -- 7
            {result['R20'] if isinstance(result['R20'], (int, float)) else empty}, -- 8
            {result['R30'] if isinstance(result['R30'], (int, float)) else empty}, -- 9
            {result['R40'] if isinstance(result['R40'], (int, float)) else empty}, -- 10
            {result['R50'] if isinstance(result['R50'], (int, float)) else empty}, -- 11
            {result['R60'] if isinstance(result['R60'], (int, float)) else empty}, -- 12
            {result['Rezultat']}, -- 13
            {result['Ineri'] if isinstance(result['Ineri'], (int, float)) else empty}, -- 14
            '{result['Napomena']}' -- 15
        )
        """
        return DBManipulator.execute_query(insert)


class DBGetter:
    @classmethod
    def get_shooter_weapons(cls, shooter_id: int) -> List[sqlTypes.WeaponDetails]:
        query = f"""
        SELECT
            id, -- 0
            serijski_broj, -- 1 
            vrsta, -- 2
            tip, -- 3
            proizvodjac, -- 4
            model, -- 5
            duljina, -- 6
            visina, -- 7
            sirina, -- 8
            duljina_cijevi, -- 9
            kalibar, -- 10
            materijal, -- 11
            masa_okidanja_od, -- 12
            masa_okidanja_do, -- 13
            drska_ruka, -- 14
            drska_velicina, -- 15
            napomena, -- 16
            id_strijelac -- 17
        FROM oruzje
        WHERE id_strijelac={shooter_id}
        """

        weapons = []

        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return weapons

        for d in data:
            weapons.append(
                {
                    "id": d[0],
                    "serial_no": d[1],
                    "kind": d[2],
                    "type": d[3],
                    "manufacturer": d[4],
                    "model": d[5],
                    "length": d[6],
                    "height": d[7],
                    "width": d[8],
                    "barrel_length": d[9],
                    "caliber": d[10],
                    "material": d[11],
                    "trigger_mass_from": d[12],
                    "trigger_mass_to": d[13],
                    "handle_hand": d[14],
                    "handle_size": d[15],
                    "note": d[16],
                    "shooter_id": d[17]
                }
            )
        return weapons

    @classmethod
    def get_service_details(cls, service_id: int) -> sqlTypes.WeaponService:
        query = f"""
                SELECT
                    id, -- 0 
                    napomena, -- 1
                    datum, -- 2
                    oruzje_id -- 3
                FROM oruzja_servis
                WHERE
                    id={service_id}
                """
        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return {}

        return {
                    "weapon_id": data[0][3],
                    "note": data[0][1],
                    "date": data[0][2],
                    "id": data[0][0]
                }

    @classmethod
    def get_available_air_cylinders(cls) -> List[sqlTypes.AirCylinder]:
        """Returns air cylinders not added to weapons"""
        query = f"""
                SELECT 
                    id, -- 0
                    serijski_broj, -- 1
                    proizvodjac, -- 2
                    duljina, -- 3
                    kapacitet, -- 4
                    masa, -- 5
                    maksimalni_pritisak, -- 6
                    promjer, -- 7
                    vrijedi_do -- 8
                FROM cilindar_za_zrak
                WHERE id_oruzje<=0 OR id_oruzje IS NULL
                """
        air_cylinders = []

        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return air_cylinders

        for d in data:
            air_cylinders.append(
                {
                    "id": d[0],
                    "serial_no": d[1],
                    "manufacturer": d[2],
                    "length": d[3],
                    "capacity": d[4],
                    "mass": d[5],
                    "max_pressure": d[6],
                    "diameter": d[7],
                    "date_expire": d[8]
                }
            )
        return air_cylinders

    @classmethod
    def get_air_cylinders(cls) -> List[sqlTypes.AirCylinder]:
        query = f"""
        SELECT 
            id, -- 0
            serijski_broj, -- 1
            proizvodjac, -- 2
            duljina, -- 3
            kapacitet, -- 4
            masa, -- 5
            maksimalni_pritisak, -- 6
            promjer, -- 7
            vrijedi_do, -- 8
            id_oruzje -- 9
        FROM cilindar_za_zrak
        """
        air_cylinders = []

        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return air_cylinders

        for d in data:
            air_cylinders.append(
                {
                    "id": d[0],
                    "serial_no": d[1],
                    "manufacturer": d[2],
                    "length": d[3],
                    "capacity": d[4],
                    "mass": d[5],
                    "max_pressure": d[6],
                    "diameter": d[7],
                    "date_expire": d[8],
                    "weapon_id": d[9]
                }
            )
        return air_cylinders

    @classmethod
    def get_weapon_air_cylinders(cls, weapon_id: int) -> List[int]:
        """Returns air cylinders id"""
        query = f"""
        SELECT
            id -- 0
        FROM cilindar_za_zrak
        WHERE id_oruzje={weapon_id}
        """

        weapon_air_cylinders = []

        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return weapon_air_cylinders

        for d in data:
            weapon_air_cylinders.append(d[0])

        return weapon_air_cylinders

    @classmethod
    def get_air_cylinder_details(cls, cylinder_id: int = 0, serial_no: str = "") -> sqlTypes.AirCylinder:
        query = f"""
        SELECT 
            id, -- 0
            serijski_broj, -- 1
            proizvodjac, -- 2
            duljina, -- 3
            kapacitet, -- 4
            masa, -- 5
            maksimalni_pritisak, -- 6
            promjer, -- 7
            vrijedi_do, -- 8
            id_oruzje -- 9
        FROM cilindar_za_zrak
        """
        if serial_no:
            query += f" WHERE serijski_broj='{serial_no}'"
        elif cylinder_id:
            query += f" WHERE id={cylinder_id}"
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return {}

        return {
            "id": data[0][0],
            "serial_no": data[0][1],
            "manufacturer": data[0][2],
            "length": data[0][3],
            "capacity": data[0][4],
            "mass": data[0][5],
            "max_pressure": data[0][6],
            "diameter": data[0][7],
            "date_expire": data[0][8],
            "weapon_id": data[0][9]
        }

    @classmethod
    def get_weapon_shooter(cls, weapon_id: int) -> int:
        query = f"""
        SELECT 
            id_strijelac
        FROM oruzje
        WHERE id={weapon_id}
        """

        data = DBManipulator.fetch_row(query)

        if data[0]:
            return data[0][0]

        return 0

    @classmethod
    def get_weapon_services(cls, weapon_id: int) -> List[sqlTypes.WeaponService]:
        query = f"""
        SELECT
            id, -- 0 
            napomena, -- 1
            datum -- 2
        FROM oruzja_servis
        WHERE
            oruzje_id={weapon_id}
        """
        data = DBManipulator.fetch_row(query)
        services = []
        if not data[0]:
            return services

        for d in data:
            services.append(
                {
                    "weapon_id": weapon_id,
                    "note": d[1],
                    "date": d[2],
                    "id": d[0]
                }
            )
        return services

    @classmethod
    def get_weapon_details(cls, weapon_id: int = 0, serial_no: str = "") -> sqlTypes.WeaponDetails:
        weapon = {}
        query = f"""
        SELECT
            id, -- 0
            serijski_broj, -- 1 
            vrsta, -- 2
            tip, -- 3
            proizvodjac, -- 4
            model, -- 5
            duljina, -- 6
            visina, -- 7
            sirina, -- 8
            duljina_cijevi, -- 9
            kalibar, -- 10
            materijal, -- 11
            masa_okidanja_od, -- 12
            masa_okidanja_do, -- 13
            drska_ruka, -- 14
            drska_velicina, -- 15
            napomena, -- 16
            id_strijelac -- 17
        FROM oruzje
        """
        if weapon_id:
            query += f" WHERE id={weapon_id}"
        elif serial_no:
            query += f" WHERE serijski_broj='{serial_no}'"
        else:
            return weapon
        data = DBManipulator.fetch_row(query)

        if not data[0]:
            return weapon

        weapon: sqlTypes.WeaponDetails = {
            "id": data[0][0],
            "serial_no": data[0][1],
            "kind": data[0][2],
            "type": data[0][3],
            "manufacturer": data[0][4],
            "model": data[0][5],
            "length": data[0][6],
            "height": data[0][7],
            "width": data[0][8],
            "barrel_length": data[0][9],
            "caliber": data[0][10],
            "material": data[0][11],
            "trigger_mass_from": data[0][12],
            "trigger_mass_to": data[0][13],
            "handle_hand": data[0][14],
            "handle_size": data[0][15],
            "note": data[0][16],
            "shooter_id": data[0][17]
        }
        return weapon

    @classmethod
    def get_weapon_types(cls):
        query = f"""
        SELECT tip FROM oruzje
        """
        values = []
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return values
        for d in data:
            try:
                values.append(d[0])
            except IndexError:
                pass
        return values

    @classmethod
    def get_weapon_kinds(cls):
        query = f"""
        SELECT vrsta FROM oruzje
        """
        values = []
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return values
        for d in data:
            try:
                values.append(d[0])
            except IndexError:
                pass
        return values

    @classmethod
    def get_weapon_type_kind_cartesian_product(cls):
        weapons = {}
        weapon_types = DBGetter.get_weapon_types()
        weapon_kinds = DBGetter.get_weapon_kinds()
        for weapon_type in weapon_types:
            for weapon_kind in weapon_kinds:
                query = f"""
                SELECT id -- 0
                FROM oruzje 
                WHERE tip='{weapon_type}'
                    AND vrsta='{weapon_kind}'
                """
                data = DBManipulator.fetch_row(query)
                weapons[f"{weapon_kind} - {weapon_type}"] = []
                try:
                    weapons[f"{weapon_kind} - {weapon_type}"] = [d[0] for d in data]
                except IndexError:
                    pass
        #cartesian_product = [f"{w_kind} {w_type}" for w_kind in weapon_kinds for w_type in weapon_types]
        return weapons

    @classmethod
    def get_competition_details(self, competition_id: int) -> sqlTypes.CompetitionInfo:
        query = f"""
        SELECT 
            naziv, -- 0
            program, -- 1
            mjesto, -- 2
            adresa, -- 3
            datum, -- 4
            napomena, -- 5
            kategorija, -- 6
        FROM natjecanja 
        WHERE id_natjecanja={competition_id}
        """
        data = DBManipulator.fetch_row(query)
        competition_info = {}
        if not data[0]:
            return competition_info
        d = data[0]
        try:
            competition_info = {
                "Naziv": d[0],
                "Mjesto": d[2],
                "Adresa": d[3],
                "Datum": d[4],
                "Program": d[1],
                "Kategorija": d[6],
                "Napomena": d[5],
                "id": competition_id,
            }
        except Exception:
            pass
        return competition_info

    @classmethod
    def get_club_name(cls):
        query = """
        SELECT
            naziv
        FROM
            klub
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return False
        return data[0][0]

    @classmethod
    def get_club_location(cls):
        query = """
        SELECT
            mjesto
        FROM
            klub
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return False
        return data[0][0]

    @classmethod
    def get_shooter_notes(cls, shooter_id: int) -> List[sqlTypes.Napomena]:
        query = f"""
        SELECT 
            napomena, -- 0
            datum, -- 1
            id_napomena -- 2
            FROM napomene 
        WHERE id_strijelac={shooter_id} 
        ORDER BY datum
        """
        data = DBManipulator.fetch_row(query)
        if not data:
            return []
        dictionaries = []
        try:
            for d in data:
                dictionary: sqlTypes.Napomena = {
                    "Tekst": d[0],
                    "Datum": d[1],
                    "id": d[2],
                    "id_strijelac": shooter_id
                }
                dictionaries.append(dictionary)
        except Exception:
            pass
        return dictionaries

    @classmethod
    def get_shooter_contact_info(cls, shooter_id: int) -> sqlTypes.ShooterContactInfo:
        query = f"""
        SELECT 
            telefon_kuca, -- 0
            telefon_posao, -- 1
            mobitel_1, -- 2
            mobitel_2, -- 3
            email -- 4
        FROM strijelci_hss   
        WHERE id_strijelac={shooter_id}
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return {}
        d = data[0]
        try:
            dictionary: sqlTypes.ShooterContactInfo = {
                "id": shooter_id,
                "TelefonKuca": d[0],
                "TelefonPosao": d[1],
                "Mobitel1": d[2],
                "Mobitel2": d[3],
                "Email": d[4]
            }
        except Exception:
            dictionary = {}
        return dictionary

    @classmethod
    def get_shooter_general_info(cls, shooter_id: int) -> sqlTypes.ShooterGeneralInfo:
        query = f"""
        SELECT 
            strucna_sprema, -- 0
            zaposlenje, -- 1
            hobi, -- 2
            banka, -- 3
            ziro  -- 4
        FROM strijelci_hss 
        WHERE id_strijelac={shooter_id}
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return {}
        d = data[0]
        try:
            dictionary: sqlTypes.ShooterGeneralInfo = {
                "id": shooter_id,
                "StrucnaSprema": d[0],
                "Zaposlenje": d[1],
                "Hobi": d[2],
                "Banka": d[3],
                "Ziro": d[4]
            }
        except Exception:
            dictionary = {}
        return dictionary

    @classmethod
    def get_shooter_PIN_info(cls, shooter_id: int) -> sqlTypes.ShooterPINInfo:
        query = f"""
        SELECT 
            oi, -- 0
            oi_datum, -- 1
            oi_mjesto, -- 2
            oi_trajna, -- 3
            putovnica, -- 4
            putovnica_datum, -- 5
            putovnica_postoji, -- 6
            putovnica_mjesto, -- 7
            drzavljanstvo -- 8
        FROM strijelci_hss 
        WHERE id_strijelac={shooter_id}
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return {}
        d = data[0]
        try:
            dictionary: sqlTypes.ShooterPINInfo = {
                "id": shooter_id,
                "OI": d[0],
                "OIDatum": d[1],
                "OIMjesto": d[2],
                "OITrajna": d[3],
                "Putovnica": d[4],
                "PutovnicaDatum": d[5],
                "PutovnicaPostoji": d[6],
                "PutovnicaMjesto": d[7],
                "Drzavljanstvo": d[8]
            }
        except Exception:
            dictionary = {}
        return dictionary

    @classmethod
    def get_shooter_required_info(cls, shooter_id: int) -> sqlTypes.ShooterRequiredInfo:
        query = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.spol, -- 2
            strijelci_hss.oib, -- 3
            strijelci.datRod, -- 4
            strijelci_hss.mjesto_rod, -- 5
            strijelci_hss.adresa, -- 6
            strijelci_hss.mjesto_stan, -- 7 
            strijelci_hss.hss -- 8
        FROM strijelci_hss 
        LEFT JOIN strijelci ON strijelci.id_strijelac=strijelci_hss.id_strijelac 
        WHERE strijelci_hss.id_strijelac={shooter_id} 
        """
        data = DBManipulator.fetch_row(query)
        if not data[0]:
            return {}
        d = data[0]
        try:
            dictionary: sqlTypes.ShooterRequiredInfo = {
                "id": shooter_id,
                "Ime": d[0],
                "Prezime": d[1],
                "Spol": d[2],
                "Oib": d[3],
                "Datum": d[4],
                "MjestoRodjenja": d[5],
                "Adresa": d[6],
                "MjestoStanovanja": d[7],
                "HSS": d[8]
            }
        except IndexError:
            dictionary = {}
        return dictionary

    @classmethod
    def get_min_date_in_results(cls) -> str:
        """Returns date in %Y-%m-%d format"""
        select_min_date = "SELECT MIN(datum) FROM dnevnik"
        data = DBManipulator.fetch_row(select_min_date)
        if not data[0]:
            return "1900-01-01"
        return data[0][0]

    @classmethod
    def get_max_date_in_results(cls) -> str:
        """Returns date in %Y-%m-%d format"""
        select_max_date = "SELECT MAX(datum) FROM dnevnik"
        data = DBManipulator.fetch_row(select_max_date)
        if not data[0]:
            return "1900-01-01"
        return data[0][0]

    @classmethod
    def get_competition_hss_id(cls, competition_id: int):
        select = f"""SELECT hss_id FROM natjecanja WHERE id_natjecanja={competition_id}"""
        value = DBManipulator.fetch_row(select)[0]
        if value:
            return value[0]
        return 0

    @classmethod
    def get_hss_ids_of_competitions(cls):
        select = "SELECT hss_id FROM natjecanja WHERE hss_id > 0"
        ids = DBManipulator.fetch_row(select)
        if not ids[0]:
            return []
        return [id_[0] for id_ in ids]

    @classmethod
    def get_hss_natjecanja(cls):
        select = """
        SELECT
            id, -- 0
            naziv, -- 1
            utc_start, -- 2
            utc_end, -- 3
            mjesto, -- 4
            napomena -- 5
        FROM hss_natjecanja
        ORDER BY id
        """
        data = DBManipulator.fetch_row(select)
        competitions = []
        try:
            for d in data:
                competition = {
                    "hss_id": d[0],
                    "Naziv": d[1],
                    "utc_start": d[2],
                    "utc_end": d[3],
                    "Mjesto": d[4],
                    "Napomena": d[5]
                }
                competitions.append(competition)
        except Exception:
            pass
        finally:
            return competitions

    @classmethod
    def get_bilten(cls, competition_id: int):
        select = f"""
            SELECT bilten_path FROM natjecanja WHERE id_natjecanja={competition_id}
            """
        data = DBManipulator.fetch_row(select)[0]
        if data:
            return data[0]
        return None

    @classmethod
    def get_startne_liste(cls, competition_id: int):
        select = f"""
            SELECT startne_liste_path FROM natjecanja WHERE id_natjecanja={competition_id}
            """
        data = DBManipulator.fetch_row(select)[0]
        if data:
            return data[0]
        return None

    @classmethod
    def get_pozivno_pismo(cls, competition_id: int):
        select = f"""
            SELECT pozivno_pismo_path FROM natjecanja WHERE id_natjecanja={competition_id}
            """
        data = DBManipulator.fetch_row(select)[0]
        if data:
            return data[0]
        return None

    @classmethod
    def get_target_id_from_name(self, target_name: str) -> int:
        query = f"SELECT id_meta FROM mete WHERE naziv='{target_name}'"
        return DBManipulator.fetch_row(query)[0][0]

    @classmethod
    def get_shooter_basic_info(cls, shooter_id: int) -> sqlTypes.ShooterBasicInfo:
        query = f"""
        SELECT 
            ime, -- 0
            prezime, -- 1
            datRod, -- 2
            spol -- 3
        FROM strijelci 
        WHERE id_strijelac={shooter_id}
    	"""
        values = DBManipulator.fetch_row(query)[0]
        try:
            dictionary: sqlTypes.ShooterBasicInfo = {
                "id": shooter_id,
                "Ime": values[0],
                "Prezime": values[1],
                "Datum": values[2],
                "Spol": values[3]
            }
        except Exception:
            dictionary = {}
        return dictionary

    @classmethod
    def get_shooter_registrations(cls, shooter_id: int):
        select = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.id_strijelac, -- 2
            registracije.datum_od, -- 3
            registracije.datum_do, -- 4
            registracije.path, -- 5
            registracije.id -- 6
        FROM registracije
        LEFT JOIN strijelci ON strijelci.id_strijelac=registracije.id_strijelac
        WHERE registracije.id_strijelac={shooter_id}
        ORDER BY registracije.datum_do
        """
        rows = DBManipulator.fetch_row(select)
        registrations = []
        try:
            for row in rows:
                registration = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "id": row[2],
                    "Vrijedi od": row[3],
                    "Vrijedi do": row[4],
                    "Path": row[5],
                    "pdf_id": row[6]
                }
                registrations.append(registration)
        except Exception:
            pass
        finally:
            return registrations

    @classmethod
    def get_shooter_doctors_pdf(cls, shooter_id: int):
        select = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.id_strijelac, -- 2
            pdf_lijecnicki.datum_od, -- 3
            pdf_lijecnicki.datum_do, -- 4
            pdf_lijecnicki.path, -- 5
            pdf_lijecnicki.id -- 6
        FROM pdf_lijecnicki
        LEFT JOIN strijelci ON strijelci.id_strijelac=pdf_lijecnicki.id_strijelac
        WHERE pdf_lijecnicki.id_strijelac={shooter_id}
        ORDER BY pdf_lijecnicki.datum_do
        """
        rows = DBManipulator.fetch_row(select)
        doctors = []
        try:
            for row in rows:
                doctor = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "id": row[2],
                    "Vrijedi od": row[3],
                    "Vrijedi do": row[4],
                    "Path": row[5],
                    "pdf_id": row[6]
                }
                doctors.append(doctor)
        except Exception:
            pass
        finally:
            return doctors

    @classmethod
    def get_notification_shooter_doctor(cls, shooter_id: int):
        select = f"""
        SELECT 
            lijecnicki 
        FROM strijelci_obavijesti
        WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.fetch_row(select)[0][0]

    @classmethod
    def get_notification_shooter_NPIN(cls, shooter_id: int):
        select = f"""
        SELECT
            osobna
        FROM strijelci_obavijesti
        WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.fetch_row(select)[0][0]

    @classmethod
    def get_notification_shooter_passport(cls, shooter_id: int):
        select = f"""
        SELECT
            putovnica
        FROM strijelci_obavijesti
        WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.fetch_row(select)[0][0]

    @classmethod
    def get_active_other_reminders(cls, category: int = 0) -> List[sqlTypes.OtherReminder]:
        select = """
        SELECT 
            id_obavijesti, --0
            naslov, -- 1
            tekst, -- 2
            datum, -- 3
            procitana, -- 4
            kategorija -- 5
        """
        if not category:
            select += f"""
                FROM obavijesti
                WHERE procitana=0
                AND kategorija={category}
            """
        else:
            select += """
            FROM obavijesti
            WHERE procitana=0
            """
        rows = DBManipulator.fetch_row(select)
        reminders = []
        try:
            for row in rows:
                reminder: sqlTypes.OtherReminder = {
                    "id": row[0],
                    "Naslov": row[1],
                    "Tekst": row[2],
                    "Datum": row[3],
                    "Procitana": row[4]
                }
                reminders.append(reminder)
        except Exception:
            pass
        finally:
            return reminders

    @classmethod
    def get_other_reminders(cls) -> List[sqlTypes.OtherReminder]:
        select = """
        SELECT 
            id_obavijesti, --0
            naslov, -- 1
            tekst, -- 2
            datum, -- 3
            procitana -- 4
        FROM obavijesti
        """
        rows = DBManipulator.fetch_row(select)
        reminders = []
        try:
            for row in rows:
                reminder: sqlTypes.OtherReminder = {
                    "id": row[0],
                    "Naslov": row[1],
                    "Tekst": row[2],
                    "Datum": row[3],
                    "Procitana": row[4]
                }
                reminders.append(reminder)
        except Exception:
            pass
        finally:
            return reminders

    @classmethod
    def get_result_note_text(cls, result_id: int):
        select = f"SELECT napomena FROM dnevnik WHERE id={result_id}"
        return DBManipulator.fetch_row(select)[0][0]

    @classmethod
    def get_shooters_with_expired_NPIN(cls, current_date: str = "") -> List[sqlTypes.ShooterWithNPINExpireDate]:
        """If current_date is not provided, system time will be used"""
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.datRod, -- 2
            strijelci.spol, -- 3
            strijelci.id_strijelac,  -- 4
            strijelci_hss.oi_datum -- 5
        FROM strijelci
        LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac
        LEFT JOIN strijelci_hss ON strijelci_hss.id_strijelac=strijelci.id_strijelac
        WHERE strijelci_obavijesti.osobna = 1
                AND strijelci_hss.oi_datum<date('{current_date}')
                AND strijelci_hss.oi_trajna = 0  
                AND strijelci_hss.registracija = 1
        ORDER BY strijelci_hss.oi_datum
        """
        shooters = []
        rows = DBManipulator.fetch_row(select)
        try:
            for row in rows:
                shooter: sqlTypes.ShooterWithNPINExpireDate = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "id": row[4],
                    "DatumIstekaOI": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_shooter_with_NPIN_about_to_expire(cls, days_till_expire: int,
                                              current_date: str = "") -> List[sqlTypes.ShooterWithNPINExpireDate]:
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
        SELECT
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.spol, -- 2
            strijelci.datRod, -- 3
            strijelci.id_strijelac, -- 4
            strijelci_hss.oi_datum -- 5
        FROM strijelci
        LEFT JOIN strijelci_hss ON strijelci_hss.id_strijelac=strijelci.id_strijelac
        LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac 
        WHERE strijelci_obavijesti.osobna = 1 
                AND strijelci_hss.oi_datum<date('{current_date}', '{days_till_expire} day')
                AND strijelci_hss.oi_datum>=date('{current_date}')
                AND strijelci_hss.oi_trajna = 0 
                AND strijelci_hss.registracija = 1
        ORDER BY strijelci_hss.lijecnicki
        """
        shooters = []
        rows = DBManipulator.fetch_row(select)
        try:
            for row in rows:
                shooter: sqlTypes.ShooterWithNPINExpireDate = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Spol": row[2],
                    "Datum": row[3],
                    "id": row[4],
                    "DatumIstekaOI": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_registered_shooters(cls, current_date: str = ""):
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
        SELECT
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.spol, -- 2
            strijelci.datRod, -- 3
            strijelci.id_strijelac -- 4
        FROM strijelci
        LEFT JOIN registracije on strijelci.id_strijelac=registracije.id_strijelac
        WHERE registracije.datum_do>date('{current_date}')
        GROUP BY strijelci.id_strijelac
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterBasicInfo = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Spol": row[2],
                    "Datum": row[3],
                    "id": row[4]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_registered_shooters_with_no_doctors(cls, current_date: str = "") :
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
        SELECT
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.spol, -- 2
            strijelci.datRod, -- 3
            strijelci.id_strijelac -- 4
        FROM strijelci
        LEFT JOIN strijelci_hss ON strijelci_hss.id_strijelac=strijelci.id_strijelac
        LEFT JOIN registracije on strijelci.id_strijelac=registracije.id_strijelac
        WHERE strijelci.id_strijelac NOT IN (SELECT pdf_lijecnicki.id_strijelac FROM pdf_lijecnicki)
            AND registracije.datum_do>date('{current_date}')
        GROUP BY strijelci.id_strijelac
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterWithDoctorExpireDate = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Spol": row[2],
                    "Datum": row[3],
                    "id": row[4],
                    "DatumIstekaLijecnickog": "1000-00-00"
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_registered_shooters_with_expired_doctors(cls, current_date: str = "") -> List[sqlTypes.ShooterWithDoctorExpireDate]:
        """returns shooters with expired doctor's who are registered
            does not return shooters with no doctor's set"""
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.spol, -- 2
            strijelci.datRod, -- 3
            strijelci.id_strijelac, -- 4
            MAX(date(pdf_lijecnicki.datum_do)), -- 5
            MAX(date(registracije.datum_do)) -- 6
        FROM strijelci
        LEFT JOIN registracije ON strijelci.id_strijelac=registracije.id_strijelac
        LEFT JOIN pdf_lijecnicki ON pdf_lijecnicki.id_strijelac=strijelci.id_strijelac
        LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac
        WHERE strijelci_obavijesti.lijecnicki = 1
        GROUP BY strijelci.id_strijelac
        HAVING MAX(date(pdf_lijecnicki.datum_do))<date('{current_date}') 
            AND MAX(date(registracije.datum_do))>=date('{current_date}')
        ORDER BY pdf_lijecnicki.datum_do
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterWithDoctorExpireDate = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Spol": row[2],
                    "Datum": row[3],
                    "id": row[4],
                    "DatumIstekaLijecnickog": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        return shooters

    @classmethod
    def get_registered_shooters_with_doctors_about_to_expire(cls, days_till_expire: int,
                                                  current_date: str = "") -> List[sqlTypes.ShooterWithDoctorExpireDate]:
        if not current_date:
            current_date = str(datetime.datetime.now().date())
        select = f"""
                SELECT 
                    strijelci.ime, -- 0
                    strijelci.prezime, -- 1
                    strijelci.spol, -- 2
                    strijelci.datRod, -- 3
                    strijelci.id_strijelac, -- 4
                    MAX(registracije.datum_do), -- 5
                    MAX(pdf_lijecnicki.datum_do) -- 6
                FROM strijelci
                LEFT JOIN registracije ON registracije.id_strijelac=strijelci.id_strijelac
                LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac
                LEFT JOIN pdf_lijecnicki ON pdf_lijecnicki.id_strijelac=strijelci.id_strijelac
                WHERE strijelci_obavijesti.lijecnicki=1
                GROUP BY strijelci.id_strijelac
                HAVING 
                    MAX(pdf_lijecnicki.datum_do)<date('{current_date}', '{days_till_expire} day') 
                    AND MAX(pdf_lijecnicki.datum_do)>=date('{current_date}')
                    AND MAX(registracije.datum_do)>=date('{current_date}')
                ORDER BY pdf_lijecnicki.datum_do
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterWithDoctorExpireDate = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Spol": row[2],
                    "Datum": row[3],
                    "id": row[4],
                    "DatumIstekaLijecnickog": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_notification_shooter_birthday(cls, shooter_id: int):
        select = f"""
        SELECT
            rodjendan
        FROM strijelci_obavijesti
        WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.fetch_row(select)[0][0]

    @classmethod
    def get_shooters_birthdays(cls) -> List[sqlTypes.ShooterBasicInfo]:
        select = f"""
        SELECT 
            strijelci.id_strijelac, -- 0
            strijelci.ime, -- 1
            strijelci.prezime, -- 2
            strijelci.spol,  -- 3
            strijelci.datRod  -- 4
        FROM strijelci 
        LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac
        WHERE 
            strijelci_obavijesti.rodjendan=1
            AND
            julianday('{str(ApplicationProperties.CURRENT_DATE)}')
                -
            julianday('{ApplicationProperties.CURRENT_DATE.year}' || '-' || substr(datRod, 6, 2) || '-' || substr(datRod, 9, 2))
                < 1
            AND
            julianday('{str(ApplicationProperties.CURRENT_DATE)}')
                -
            julianday('{ApplicationProperties.CURRENT_DATE.year}' || '-' || substr(datRod, 6, 2) || '-' || substr(datRod, 9, 2))
                > -30
        """
        shooters = []
        data = DBManipulator.fetch_row(select)
        if not data[0]:
            return shooters
        for d in data:
            shooters.append(
                {
                    "id": d[0],
                    "Ime": d[1],
                    "Prezime": d[2],
                    "Spol": d[3],
                    "Datum": d[4]
                }
            )
        return shooters

    @classmethod
    def get_all_shooters_notifications(cls) -> List[sqlTypes.ShooterNotificationsSettings]:
        select = f"""
        SELECT 
            strijelci.id_strijelac, -- 0
            strijelci.ime, -- 1
            strijelci.prezime, -- 2
            strijelci.spol, -- 3
            strijelci.datRod, -- 4
            strijelci_obavijesti.lijecnicki, -- 5
            strijelci_obavijesti.osobna, -- 6
            strijelci_obavijesti.putovnica, -- 7
            strijelci_obavijesti.rodjendan -- 8
        FROM strijelci
        LEFT JOIN strijelci_obavijesti ON strijelci_obavijesti.id_strijelac=strijelci.id_strijelac
        """
        notifications = []
        data = DBManipulator.fetch_row(select)
        if not data[0]:
            return notifications
        for d in data:
            try:
                notifications.append(
                    {
                        "id": d[0],
                        "Ime": d[1],
                        "Prezime": d[2],
                        "Spol": d[3],
                        "Datum": d[4],
                        "Lijecnicki": d[5],
                        "Osobna": d[6],
                        "Putovnica": d[7],
                        "Rodjendan": d[8]
                    }
                )
            except IndexError:
                pass

        return notifications

    @classmethod
    def get_retired_shooters(cls) -> List[sqlTypes.RetiredShooter]:
        select = """
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.datRod, -- 2
            strijelci.spol, -- 3
            strijelci_bivsi.datUmirovljenja, -- 4
            strijelci.id_strijelac -- 5
        FROM strijelci
        JOIN strijelci_bivsi ON strijelci.id_strijelac=strijelci_bivsi.id_strijelac
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.RetiredShooter = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "DatumUmirovljenja": row[4],
                    "id": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_active_shooters(cls) -> List[sqlTypes.ShooterBasicInfo]:
        select = """
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.datRod, -- 2
            strijelci.spol, -- 3
            strijelci.id_strijelac -- 4
        FROM strijelci 
        LEFT JOIN strijelci_pozicije ON strijelci_pozicije.id_strijelac=strijelci.id_strijelac
        WHERE strijelci_pozicije.pozicija > 0
        ORDER BY strijelci_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterBasicInfo = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "id": row[4]
                }
                shooters.append(shooter)
        except Exception:
            pass
        return shooters

    @classmethod
    def get_active_shooters_with_position(cls) -> List[sqlTypes.ShootersBasicInfoWithPosition]:
        select = """
            SELECT 
                strijelci.ime, -- 0
                strijelci.prezime, -- 1
                strijelci.datRod, -- 2
                strijelci.spol, -- 3
                strijelci.id_strijelac, -- 4
                strijelci_pozicije.pozicija -- 5
            FROM strijelci 
            LEFT JOIN strijelci_pozicije ON strijelci_pozicije.id_strijelac=strijelci.id_strijelac
            WHERE strijelci_pozicije.pozicija > 0
            ORDER BY strijelci_pozicije.pozicija
            """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShootersBasicInfoWithPosition = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "id": row[4],
                    "Pozicija": row[5]
                }
                shooters.append(shooter)
        except Exception:
            pass
        return shooters

    # TODO: replace get_active / get_inactive with a single function, use variable to insert into string '>' or '='
    @classmethod
    def get_inactive_shooters(cls) -> List[sqlTypes.ShooterBasicInfo]:
        select = """
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.datRod, -- 2
            strijelci.spol, -- 3
            strijelci.id_strijelac -- 4
        FROM strijelci 
        LEFT JOIN strijelci_pozicije ON strijelci_pozicije.id_strijelac=strijelci.id_strijelac
        WHERE strijelci_pozicije.pozicija = 0
        ORDER BY strijelci_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterBasicInfo = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "id": row[4]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_inactive_competitions(cls) -> List[sqlTypes.CompetitionInfo]:
        select = """
                SELECT 
                    natjecanja.naziv, -- 0
                    natjecanja.datum, -- 1
                    natjecanja.mjesto, -- 2
                    natjecanja.adresa, -- 3
                    natjecanja.kategorija, -- 4
                    natjecanja.program, -- 5
                    natjecanja.napomena, -- 6
                    natjecanja.id_natjecanja, -- 7
                    natjecanja.hss_id -- 8
                FROM natjecanja 
                LEFT JOIN natjecanja_pozicije ON natjecanja_pozicije.id_natjecanja=natjecanja.id_natjecanja
                WHERE natjecanja_pozicije.pozicija=0
                """
        rows = DBManipulator.fetch_row(select)
        competitions = []
        try:
            for row in rows:
                competition: sqlTypes.CompetitionInfo = {
                    "Naziv": row[0],
                    "Datum": row[1],
                    "Mjesto": row[2],
                    "Adresa": row[3],
                    "Kategorija": row[4],
                    "Program": row[5],
                    "Napomena": row[6],
                    "id": row[7],
                    "hss_id": row[8]
                }
                competitions.append(competition)
        except Exception:
            pass
        return competitions

    @classmethod
    def get_competitions_in_results(cls) -> List[sqlTypes.CompetitionInfo]:
        select = """
        SELECT 
            natjecanja.naziv, -- 0
            natjecanja.datum, -- 1
            natjecanja.mjesto, -- 2
            natjecanja.adresa, -- 3
            natjecanja.kategorija, -- 4
            natjecanja.program, -- 5
            natjecanja.napomena, -- 6
            natjecanja.hss_id, -- 7
            dnevnik.natjecanje -- 8
        FROM dnevnik
        LEFT JOIN natjecanja ON natjecanja.id_natjecanja=dnevnik.natjecanje            
        """
        competitions = []
        data = DBManipulator.fetch_row(select)
        try:
            for d in data:
                competition: sqlTypes.CompetitionInfo = {
                    "Naziv": d[0],
                    "Datum": d[1],
                    "Mjesto": d[2],
                    "Adresa": d[3],
                    "Kategorija": d[4],
                    "Program": d[5],
                    "Napomena": d[6],
                    "id": d[8],
                    "hss_id": d[7],
                }
                competitions.append(competition)
        except Exception:
            pass
        finally:
            return competitions

    @classmethod
    def get_active_competitions(cls) -> List[sqlTypes.CompetitionWithPosition]:
        select = """
        SELECT 
            natjecanja.naziv, -- 0
            natjecanja.datum, -- 1
            natjecanja.mjesto, -- 2
            natjecanja.adresa, -- 3
            natjecanja.kategorija, -- 4
            natjecanja.program, -- 5
            natjecanja.napomena, -- 6
            natjecanja.id_natjecanja, -- 7
            natjecanja_pozicije.pozicija, -- 8
            natjecanja.hss_id -- 9
        FROM natjecanja 
        LEFT JOIN natjecanja_pozicije ON natjecanja_pozicije.id_natjecanja=natjecanja.id_natjecanja
        WHERE natjecanja_pozicije.pozicija > 0
        ORDER BY natjecanja_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        competitions = []
        try:
            for row in rows:
                competition: sqlTypes.CompetitionWithPosition = {
                    "Naziv": row[0],
                    "Datum": row[1],
                    "Mjesto": row[2],
                    "Adresa": row[3],
                    "Kategorija": row[4],
                    "Program": row[5],
                    "Napomena": row[6],
                    "id": row[7],
                    "Pozicija": row[8],
                    "hss_id": row[9]
                }
                competitions.append(competition)
        except Exception:
            pass
        finally:
            return competitions

    @classmethod
    def get_shooters_at_competition(cls, competition_id: int, weapon_category: int) -> List[sqlTypes.ShooterBasicInfo]:
        """weapon_category: 1 for rifle, 0 for pistol"""
        select = f"""
        SELECT 
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            strijelci.datRod, -- 2
            strijelci.spol, -- 3
            strijelci_na_natjecanju.id_strijelac  -- 4
        FROM strijelci_na_natjecanju 
        LEFT JOIN strijelci ON strijelci.id_strijelac=strijelci_na_natjecanju.id_strijelac 
        WHERE id_natjecanja={competition_id} AND kategorija={weapon_category}
        """
        rows = DBManipulator.fetch_row(select)
        shooters = []
        try:
            for row in rows:
                shooter: sqlTypes.ShooterBasicInfo = {
                    "Ime": row[0],
                    "Prezime": row[1],
                    "Datum": row[2],
                    "Spol": row[3],
                    "id": row[4]
                }
                shooters.append(shooter)
        except Exception:
            pass
        finally:
            return shooters

    @classmethod
    def get_active_disciplines_with_positions(cls) -> List[sqlTypes.DisciplineWithPosition]:
        select = """
                SELECT
                    discipline.naziv, -- 0
                    discipline.opis, -- 1
                    discipline.id_disciplina, -- 2
                    discipline_pozicije.pozicija -- 3
                FROM discipline
                LEFT JOIN discipline_pozicije ON discipline.id_disciplina=discipline_pozicije.id_disciplina
                WHERE discipline_pozicije.pozicija > 0
                ORDER BY discipline_pozicije.pozicija 
                """
        rows = DBManipulator.fetch_row(select)
        disciplines = []
        try:
            for row in rows:
                discipline: sqlTypes.DisciplineWithPosition = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2],
                    "Pozicija": row[3]
                }
                disciplines.append(discipline)
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_disciplines_in_results(cls) -> List[sqlTypes.Discipline]:
        select = """
        SELECT 
            dnevnik.disciplina, -- 0
            discipline.naziv, -- 1
            discipline.opis -- 2
        FROM dnevnik 
        LEFT JOIN discipline ON dnevnik.disciplina=discipline.id_disciplina
        """
        rows = DBManipulator.fetch_row(select)
        disciplines = []

        try:
            for row in rows:
                discipline: sqlTypes.Discipline = {
                    "id": row[0],
                    "Naziv": row[1],
                    "Opis": row[2]
                }
                disciplines.append(discipline)
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_disciplines(cls) -> List[sqlTypes.Discipline]:
        select = """
        SELECT  
            naziv, -- 0 
            opis,  -- 1
            id_disciplina  -- 2 
        FROM discipline
        """
        rows = DBManipulator.fetch_row(select)
        disciplines = []
        try:
            for row in rows:
                discipline: sqlTypes.Discipline = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                disciplines.append(discipline)
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_targets_in_results(cls) -> List[sqlTypes.Target]:
        select = """
            SELECT 
                dnevnik.meta, -- 0
                mete.naziv, -- 1
                mete.opis -- 2
            FROM dnevnik 
            LEFT JOIN mete ON dnevnik.meta=mete.id_meta
            """
        rows = DBManipulator.fetch_row(select)
        targets = []
        try:
            for row in rows:
                target: sqlTypes.Discipline = {
                    "id": row[0],
                    "Naziv": row[1],
                    "Opis": row[2]
                }
                targets.append(target)
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_targets(cls) -> List[sqlTypes.Target]:
        select = """
        SELECT  
            naziv, -- 0 
            opis, -- 1
            id_meta --2
        FROM mete
        """
        rows = DBManipulator.fetch_row(select)
        targets = []
        try:
            for row in rows:
                target: sqlTypes.Target = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                targets.append(target)
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_programs_in_results(cls) -> List[sqlTypes.Program]:
        select = """
            SELECT 
                dnevnik.program, -- 0
                programi.naziv, -- 1
                programi.opis -- 2
            FROM dnevnik 
            LEFT JOIN programi ON dnevnik.program=programi.id_program
            """
        rows = DBManipulator.fetch_row(select)
        programs = []
        try:
            for row in rows:
                program: sqlTypes.Discipline = {
                    "id": row[0],
                    "Naziv": row[1],
                    "Opis": row[2]
                }
                programs.append(program)
        except Exception:
            pass
        finally:
            return programs

    @classmethod
    def get_program_details(cls, program) -> sqlTypes.Program:
        select = f"""
        SELECT 
            naziv, -- 0
            opis, -- 1
            id_program -- 2
        FROM programi
        WHERE id_program={program}
        """
        data = DBManipulator.fetch_row(select)

        if not data[0]:
            return {}

        return {
            "Naziv": data[0][0],
            "Opis": data[0][1],
            "id": data[0][2]
        }

    @classmethod
    def get_discipline_details(cls, discipline) -> sqlTypes.Discipline:
        select = f"""
        SELECT 
            naziv, -- 0
            opis, -- 1
            id_disciplina -- 2
        FROM discipline
        WHERE id_disciplina={discipline}
        """

        data = DBManipulator.fetch_row(select)

        if not data[0]:
            return {}

        return {
            "Naziv": data[0][0],
            "Opis": data[0][1],
            "id": data[0][2]
        }

    @classmethod
    def get_target_details(cls, target_id: int) -> sqlTypes.Target:
        select = f"""
        SELECT 
            naziv, -- 0
            opis -- 1
        FROM mete
        WHERE id_meta={target_id}
        """

        data = DBManipulator.fetch_row(select)

        if not data[0]:
            return {}

        return {
            "Naziv": data[0][0],
            "Opis": data[0][1],
            "id": target_id
        }

    @classmethod
    def get_programs(cls) -> List[sqlTypes.Target]:
        select = """
        SELECT 
            naziv, -- 0
            opis, -- 1
            id_program --2
        FROM programi
        """
        rows = DBManipulator.fetch_row(select)
        programs = []

        try:
            for row in rows:
                program: sqlTypes.Program = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                programs.append(program)
        except Exception:
            pass
        finally:
            return programs

    @classmethod
    def get_inactive_programs(cls) -> List[sqlTypes.Program]:
        select = """
            SELECT 
                programi.naziv, -- 0
                programi.opis, -- 1
                programi.id_program -- 2
            FROM programi
            LEFT JOIN programi_pozicije ON programi_pozicije.id_program=programi.id_program
            WHERE programi_pozicije.pozicija = 0
            ORDER BY programi_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        programs = []
        try:
            for row in rows:
                program: sqlTypes.Program = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                programs.append(program)
        except Exception:
            pass
        finally:
            return programs

    @classmethod
    def get_active_programs_with_positions(cls) -> List[sqlTypes.ProgramWithPositon]:
        select = """
            SELECT 
                programi.naziv, -- 0
                programi.opis, -- 1
                programi.id_program, -- 2
                programi_pozicije.pozicija -- 3
            FROM programi
            LEFT JOIN programi_pozicije ON programi_pozicije.id_program=programi.id_program
            WHERE programi_pozicije.pozicija > 0
            ORDER BY programi_pozicije.pozicija
            """
        rows = DBManipulator.fetch_row(select)
        programs = []
        try:
            for row in rows:
                program: sqlTypes.ProgramWithPositon = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2],
                    "Pozicija": row[3]
                }
                programs.append(program)
        except Exception:
            pass
        finally:
            return programs

    @classmethod
    def get_active_programs(cls):
        select = """
        SELECT 
            programi.naziv, -- 0
            programi.opis, -- 1
            programi.id_program -- 2
        FROM programi
        LEFT JOIN programi_pozicije ON programi_pozicije.id_program=programi.id_program
        WHERE programi_pozicije.pozicija > 0
        ORDER BY programi_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        programs = []
        try:
            for row in rows:
                program: sqlTypes.Program = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                programs.append(program)
        except Exception:
            pass
        finally:
            return programs

    # TODO: Note: ordered dictionary from 3.7
    @classmethod
    def get_active_disciplines(cls) -> List[sqlTypes.Discipline]:
        select = """
        SELECT
            discipline.naziv, -- 0
            discipline.opis, -- 1
            discipline.id_disciplina -- 2
        FROM discipline
        LEFT JOIN discipline_pozicije ON discipline.id_disciplina=discipline_pozicije.id_disciplina
        WHERE discipline_pozicije.pozicija > 0
        ORDER BY discipline_pozicije.pozicija 
        """
        rows = DBManipulator.fetch_row(select)
        disciplines = []

        try:
            for row in rows:
                discipline: sqlTypes.Discipline = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                disciplines.append(discipline)
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_inactive_disciplines(cls) -> List[sqlTypes.Discipline]:
        select = """
           SELECT
               discipline.naziv, -- 0
               discipline.opis, -- 1
               discipline.id_disciplina -- 2
           FROM discipline
           LEFT JOIN discipline_pozicije ON discipline.id_disciplina=discipline_pozicije.id_disciplina
           WHERE discipline_pozicije.pozicija = 0
           ORDER BY discipline_pozicije.pozicija 
           """
        rows = DBManipulator.fetch_row(select)
        disciplines = []

        try:
            for row in rows:
                discipline: sqlTypes.Discipline = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                disciplines.append(discipline)
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_active_targets_with_positions(cls) -> List[sqlTypes.TargetWithPositon]:
        select = """
            SELECT 
                mete.naziv, -- 0 
                mete.opis, -- 1
                mete.id_meta, -- 2
                mete_pozicije.pozicija -- 3
            FROM mete
            LEFT JOIN mete_pozicije ON mete.id_meta=mete_pozicije.id_meta
            WHERE mete_pozicije.pozicija > 0
            ORDER BY mete_pozicije.pozicija
            """
        rows = DBManipulator.fetch_row(select)
        targets = []

        try:
            for row in rows:
                target: sqlTypes.TargetWithPositon = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2],
                    "Pozicija": row[3]
                }
                targets.append(target)
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_active_targets(cls) -> List[sqlTypes.Target]:
        select = """
        SELECT 
            mete.naziv, -- 0 
            mete.opis, -- 1
            mete.id_meta -- 2
        FROM mete
        LEFT JOIN mete_pozicije ON mete.id_meta=mete_pozicije.id_meta
        WHERE mete_pozicije.pozicija > 0
        ORDER BY mete_pozicije.pozicija
        """
        rows = DBManipulator.fetch_row(select)
        targets = []
        try:
            for row in rows:
                target: sqlTypes.Target = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                targets.append(target)
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_inactive_targets(cls) -> List[sqlTypes.Target]:
        select = """
            SELECT 
                mete.naziv, -- 0 
                mete.opis, -- 1
                mete.id_meta -- 2
            FROM mete
            LEFT JOIN mete_pozicije ON mete.id_meta=mete_pozicije.id_meta
            WHERE mete_pozicije.pozicija = 0
            ORDER BY mete_pozicije.pozicija
            """
        rows = DBManipulator.fetch_row(select)
        targets = []
        try:
            for row in rows:
                target: sqlTypes.Target = {
                    "Naziv": row[0],
                    "Opis": row[1],
                    "id": row[2]
                }
                targets.append(target)
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_table_last_row_id(cls, table: str):
        select_last_rowid = "SELECT seq FROM sqlite_sequence WHERE name='{}'".format(table)
        last_rowid = DBManipulator.fetch_row(select_last_rowid)
        return last_rowid[0][0]

    @classmethod
    def get_last_result_id(cls):
        return cls.get_table_last_row_id("dnevnik")

    @classmethod
    def get_shooter_best_result(cls,
                                shooter_id: int,
                                program_ids: List = None,
                                discipline_ids: List = None,
                                competition_ids: List = None,
                                target_ids: List = None,
                                date_from="1970-01-01",
                                date_to="2100-01-01"
                                ) -> sqlTypes.Result:

        query = f"""
        SELECT
            strijelci.ime, -- 0
            strijelci.prezime, -- 1
            discipline.naziv, -- 2
            programi.naziv, -- 3
            mete.naziv, -- 4
            dnevnik.p, -- 5
            dnevnik.r10, -- 6
            dnevnik.r20, -- 7
            dnevnik.r30, -- 8
            dnevnik.r40, -- 9
            dnevnik.r50, -- 10
            dnevnik.r60, -- 11
            dnevnik.ineri, -- 12
            dnevnik.datum, -- 13
            dnevnik.rezultat, -- 14
            natjecanja.naziv, -- 15
            dnevnik.id, -- 16
            dnevnik.napomena, -- 17
            natjecanja.datum -- 18
        FROM dnevnik
            JOIN mete ON dnevnik.meta=mete.id_meta
            JOIN programi ON dnevnik.program=programi.id_program
            JOIN discipline ON dnevnik.disciplina=discipline.id_disciplina
            JOIN natjecanja ON dnevnik.natjecanje=natjecanja.id_natjecanja
            LEFT JOIN strijelci ON dnevnik.strijelac_id=strijelci.id_strijelac
        WHERE dnevnik.datum<='{date_to}'
            AND dnevnik.datum>='{date_from}'
            AND strijelci.id_strijelac={shooter_id}
        """
        if program_ids:
            query += " AND (dnevnik.program='%s')" % "' OR dnevnik.program='".join(
                str(program_id) for program_id in program_ids)
        if competition_ids:
            query += " AND (dnevnik.natjecanje=%s)" % " OR dnevnik.natjecanje=".join(
                str(competition_id) for competition_id in competition_ids)
        if discipline_ids:
            query += " AND (dnevnik.disciplina='%s')" % "' OR dnevnik.disciplina='".join(
                str(discipline_id) for discipline_id in discipline_ids)
        if target_ids:
            query += " AND (dnevnik.meta='%s')" % "' OR dnevnik.meta='".join(str(target_id) for target_id in target_ids)

        query += " ORDER BY dnevnik.datum "

        db_values = DBManipulator.fetch_row(query)

        if not db_values:
            return {}

        if not db_values[0]:
            return {}

        value = db_values[0]

        return {
            "Ime": value[0],
            "Prezime": value[1],
            "Strijelac": value[0] + " " + value[1],
            "Disciplina": value[2],
            "Program": value[3],
            "Meta": value[4],
            "P": value[5],
            "R10": value[6],
            "R20": value[7],
            "R30": value[8],
            "R40": value[9],
            "R50": value[10],
            "R60": value[11],
            "Ineri": value[12],
            "Datum": value[13],
            "Rezultat": value[14],
            "Natjecanje": f"({Tools.SQL_date_format_to_croatian(value[18])}) {value[15]}",
            "id": value[16],
            "Napomena": value[17]
        }

    @classmethod
    def get_distinct_shooter_programs(cls, shooter_id: int) -> List[sqlTypes.Program]:
        select = f"""
        SELECT 
            DISTINCT dnevnik.program, -- 0,
            programi.naziv,  -- 1
            programi.opis -- 2
        FROM dnevnik
        JOIN programi ON programi.id_program=dnevnik.program
        WHERE strijelac_id={shooter_id}
        """

        data = DBManipulator.fetch_row(select)

        programs = []

        try:
            for d in data:
                programs.append(
                    {
                        "Naziv": d[1],
                        "Opis": d[2],
                        "id": d[0]
                    }
                )
        except Exception:
            pass
        finally:
            return programs

    @classmethod
    def get_distinct_shooter_disciplines(cls, shooter_id: int) -> List[sqlTypes.Discipline]:
        select = f"""
            SELECT 
                DISTINCT dnevnik.disciplina, -- 0,
                discipline.naziv,  -- 1
                discipline.opis -- 2
            FROM dnevnik
            JOIN discipline ON discipline.id_disciplina=dnevnik.disciplina
            WHERE strijelac_id={shooter_id}
            """
        data = DBManipulator.fetch_row(select)

        disciplines = []

        try:
            for d in data:
                disciplines.append(
                    {
                        "Naziv": d[1],
                        "Opis": d[2],
                        "id": d[0]
                    }
                )
        except Exception:
            pass
        finally:
            return disciplines

    @classmethod
    def get_distinct_shooter_targets(cls, shooter_id: int) -> List[sqlTypes.Target]:
        select = f"""
            SELECT 
                DISTINCT dnevnik.meta, -- 0,
                mete.naziv,  -- 1
                mete.opis -- 2
            FROM dnevnik
            JOIN mete ON mete.id_meta=dnevnik.meta
            WHERE strijelac_id={shooter_id}
            """
        data = DBManipulator.fetch_row(select)

        targets = []

        try:
            for d in data:
                targets.append(
                    {
                        "Naziv": d[1],
                        "Opis": d[2],
                        "id": d[0]
                    }
                )
        except Exception:
            pass
        finally:
            return targets

    @classmethod
    def get_results(cls,
                    date_from="1970-01-01",
                    date_to="2100-01-01",
                    shooter_ids: List = None,
                    programs: List = None,
                    competition_ids: List = None,
                    targets: List = None,
                    disciplines: List = None
                    ):
        """Returns list of dictionaries, ordered by date"""
        if shooter_ids is None:
            shooter_ids = []
        dictionaries_list = []
        # do not break into multiple queries, single database query from file is faster
        query = ("SELECT "
                 "strijelci.ime, "  # 0
                 "strijelci.prezime, "  # 1
                 "discipline.naziv, "  # 2
                 "programi.naziv, "  # 3
                 "mete.naziv, "  # 4
                 "dnevnik.p, "  # 5
                 "dnevnik.r10, "  # 6
                 "dnevnik.r20, "  # 7
                 "dnevnik.r30, "  # 8
                 "dnevnik.r40, "  # 9
                 "dnevnik.r50, "  # 10
                 "dnevnik.r60, "  # 11
                 "dnevnik.ineri, "  # 12
                 "dnevnik.datum, "  # 13
                 "dnevnik.rezultat, "  # 14
                 "natjecanja.naziv, "  # 15
                 "dnevnik.id, "  # 16
                 "dnevnik.napomena, "  # 17
                 "natjecanja.datum " # 18
                 "FROM dnevnik "
                 "JOIN mete ON dnevnik.meta=mete.id_meta "
                 "JOIN programi ON dnevnik.program=programi.id_program "
                 "JOIN discipline ON dnevnik.disciplina=discipline.id_disciplina "
                 "JOIN natjecanja ON dnevnik.natjecanje=natjecanja.id_natjecanja "
                 "LEFT JOIN strijelci ON dnevnik.strijelac_id=strijelci.id_strijelac "
                 f"WHERE dnevnik.datum<='{date_to}' "
                 f"AND dnevnik.datum>='{date_from}' "
                 )
        if shooter_ids:
            query += " AND (dnevnik.strijelac_id=%s)" % " OR dnevnik.strijelac_id=".join(
                str(item) for item in shooter_ids)
        if programs:
            query += " AND (dnevnik.program='%s')" % "' OR dnevnik.program='".join(str(item) for item in programs)
        if competition_ids:
            query += " AND (dnevnik.natjecanje=%s)" % " OR dnevnik.natjecanje=".join(
                str(item) for item in competition_ids)
        if targets:
            query += " AND (dnevnik.meta='%s')" % "' OR dnevnik.meta='".join(str(item) for item in targets)
        if disciplines:
            query += " AND (dnevnik.disciplina='%s')" % "' OR dnevnik.disciplina='".join(
                str(item) for item in disciplines)
        query += " ORDER BY dnevnik.datum "
        db_values = DBManipulator.fetch_row(query)
        try:
            for value in db_values:
                dictionary_values: sqlTypes.Result = {
                    "Ime": value[0],
                    "Prezime": value[1],
                    "Strijelac": value[0] + " " + value[1],
                    "Disciplina": value[2],
                    "Program": value[3],
                    "Meta": value[4],
                    "P": value[5],
                    "R10": value[6],
                    "R20": value[7],
                    "R30": value[8],
                    "R40": value[9],
                    "R50": value[10],
                    "R60": value[11],
                    "Ineri": value[12],
                    "Datum": value[13],
                    "Rezultat": value[14],
                    "Natjecanje": f"({Tools.SQL_date_format_to_croatian(value[18])}) {value[15]}",
                    "id": value[16],
                    "Napomena": value[17]
                }
                dictionaries_list.append(dictionary_values)
        except Exception:
            pass
        finally:
            return dictionaries_list

    @classmethod
    def get_competitions_in_time(
            cls,
            date_from: str = "1000-01-01",
            date_to: str = "2100-01-01"
    ) -> List[sqlTypes.CompetitionInfo]:
        dictionaries = []
        query = f"""
        SELECT 
            naziv, -- 0
            mjesto, -- 1
            adresa, -- 2
            datum, -- 3
            program, -- 4
            kategorija, -- 5 
            napomena, -- 6
            id_natjecanja, -- 7
            hss_id -- 8
        FROM natjecanja
        WHERE datum <= '{date_to}' AND datum >= '{date_from}'
        ORDER BY datum
        """
        data = DBManipulator.fetch_row(query)
        try:
            for d in data:
                dictionaries.append(
                    {
                        "Naziv": d[0],
                        "Mjesto": d[1],
                        "Adresa": d[2],
                        "Datum": d[3],
                        "Program": d[4],
                        "Kategorija": d[5],
                        "Napomena": d[6],
                        "id": d[7],
                        "hss_id": d[8]
                    }
                )
        except Exception:
            pass
        return dictionaries

    @classmethod
    def get_competitions(cls, state: str):
        """state possible values: 'all', 'active', 'inactive'"""
        if not isinstance(state, str):
            raise TypeError("Wrong state type: possible values: 'all', 'active', 'inactive'")
        if state == "active":
            return DBGetter.get_active_competitions()
        elif state == "inactive":
            return DBGetter.get_inactive_competitions()
        elif state == "all":
            return DBGetter.get_active_competitions() + DBGetter.get_inactive_competitions()
        else:
            raise ValueError("Unknown state - possible values: 'all', 'active', 'inactive'")


class DBUpdate:
    @classmethod
    def update_air_cylinder_weapon(cls, air_cylinder_id: int, weapon_id: int):
        query = f"""
        UPDATE cilindar_za_zrak 
        SET id_oruzje={weapon_id}
        WHERE id={air_cylinder_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def update_weapon_shooter(cls, weapon_id: int, shooter_id: int):
        query = f"""
        UPDATE oruzje
        SET 
            id_strijelac={shooter_id}
        WHERE
            id={weapon_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def update_weapon_service(cls, weapon_id: int, service_id: int, note: str, date: str):
        query = f"""
        UPDATE oruzja_servis
        SET 
            oruzje_id={weapon_id},
            napomena='{note}',
            datum='{date}'
        WHERE 
            id={service_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def update_air_cylinder(cls, details: sqlTypes.AirCylinder, serial_no: str = "", cylinder_id: int = 0):
        query = f"""
        UPDATE cilindar_za_zrak
        SET
            serijski_broj='{details['serial_no']}',
            proizvodjac='{details['manufacturer']}',
            duljina='{details['length']}',
            kapacitet='{details['capacity']}',
            masa='{details['mass']}',
            maksimalni_pritisak='{details['max_pressure']}',
            promjer='{details['diameter']}',
            vrijedi_do='{details['date_expire']}'
        """
        if cylinder_id:
            query += f" WHERE id={cylinder_id}"
        elif serial_no:
            query += f" WHERE serijski_broj='{details['serial_no']}'"
        else:
            return False
        return DBManipulator.execute_query(query)

    @classmethod
    def update_weapon(cls, details: sqlTypes.WeaponDetails, weapon_id: int = 0, serial_no: str = ""):
        empty = "''"
        query = f"""
        UPDATE oruzje 
        SET 
            vrsta='{details['kind']}',
            tip='{details['type']}',
            proizvodjac='{details['manufacturer']}',
            model='{details['model']}',
            duljina='{details['length']}',
            visina='{details['height']}',
            sirina='{details['width']}',
            duljina_cijevi='{details['barrel_length']}',
            kalibar='{details['caliber']}',
            materijal='{details['material']}',
            masa_okidanja_od='{details['trigger_mass_from']}',
            masa_okidanja_do='{details['trigger_mass_to']}',
            drska_ruka='{details['handle_hand']}',
            drska_velicina='{details['handle_size']}',
            napomena='{details['note']}'
        """
        if weapon_id:
            query += f",serijski_broj='{details['serial_no']}' WHERE id={weapon_id}"
        elif serial_no:
            query += f" WHERE serijski_broj='{serial_no}'"
        return DBManipulator.execute_query(query)

    @classmethod
    def update_shooter_required_info(cls, shooter_id: int, values: sqlTypes.ShooterRequiredInfo) -> bool:
        query1 = f"""
        UPDATE strijelci_hss 
        SET
            oib='{values['Oib']}',
            mjesto_rod='{values['MjestoRodjenja']}',
            adresa='{values['Adresa']}',
            mjesto_stan='{values['MjestoStanovanja']}',
            hss='{values['HSS']}'
        WHERE id_strijelac={shooter_id}
        """

        if not DBManipulator.execute_query(query1):
            return False

        query2 = f"""
        UPDATE strijelci 
            SET
              ime='{values['Ime']}',
              prezime='{values['Prezime']}',
              spol='{values['Spol']}',
              datRod='{values['Datum']}'
            WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.execute_query(query2)

    @classmethod
    def update_shooter_PIN_info(cls, values: sqlTypes.ShooterPINInfo, shooter_id: int):
        query = f"""
        UPDATE strijelci_hss 
        SET 
            oi='{values['OI']}', 
            oi_datum='{values['OIDatum']}', 
            oi_mjesto='{values['OIMjesto']}', 
            oi_trajna={values['OITrajna']}, 
            putovnica='{values['Putovnica']}', 
            putovnica_datum='{values['PutovnicaDatum']}', 
            putovnica_postoji={values['PutovnicaPostoji']}, 
            putovnica_mjesto='{values['PutovnicaMjesto']}', 
            drzavljanstvo='{values['Drzavljanstvo']}' 
        WHERE id_strijelac={shooter_id} 
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def update_shooter_general_info(cls, values: sqlTypes.ShooterGeneralInfo, shooter_id: int):
        query = f"""
        UPDATE strijelci_hss 
        SET 
            strucna_sprema='{values['StrucnaSprema']}', 
            zaposlenje='{values['Zaposlenje']}', 
            hobi='{values['Hobi']}', 
            banka='{values['Banka']}', 
            ziro='{values['Ziro']}' 
            WHERE id_strijelac={shooter_id}
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def update_shooter_contact_info(cls, values: sqlTypes.ShooterContactInfo, shooter_id: int):
        query = f"""
        UPDATE strijelci_hss 
        SET 
            telefon_kuca='{values['TelefonKuca']}', 
            telefon_posao='{values['TelefonPosao']}', 
            mobitel_1='{values['Mobitel1']}', 
            mobitel_2='{values['Mobitel2']}', 
            email='{values['Email']}' 
            WHERE id_strijelac={shooter_id} 
        """
        return DBManipulator.execute_query(query)

    @classmethod
    def set_competition_hss_id(cls, competition_id: int, hss_id: int):
        update = f"""UPDATE natjecanja SET hss_id={hss_id} WHERE id_natjecanja={competition_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_competition_position(cls, competition_id: int, value: int):
        update = f"""
        UPDATE natjecanja_pozicije SET pozicija={value} WHERE id_natjecanja={competition_id}
        """
        return DBManipulator.execute_query(update)

    @classmethod
    def update_competition_bilten(cls, competition_id: int, path: str):
        update = f"""UPDATE natjecanja SET bilten_path='{path}' WHERE id_natjecanja={competition_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_competition_startne_liste(cls, competition_id: int, path: str):
        update = f"""UPDATE natjecanja SET startne_liste_path='{path}' WHERE id_natjecanja={competition_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_competition_pozivno_pismo(cls, competition_id: int, path: str):
        update = f"""UPDATE natjecanja SET pozivno_pismo_path='{path}' WHERE id_natjecanja={competition_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def other_reminder_read(cls, other_reminder_id: int):
        update = f"""UPDATE obavijesti SET procitana=1 WHERE id_obavijesti={other_reminder_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_shooter_registration(cls, pdf_id: str, shooter_id: int, date_from: str, date_to: str, path: str):
        update = f"""
            UPDATE registracije 
            SET 
                datum_od='{date_from}', 
                datum_do='{date_to}', 
                path='{path}', 
                id_strijelac={shooter_id} 
            WHERE id={pdf_id}
        """
        return DBManipulator.execute_query(update)

    @classmethod
    def update_shooter_doctors_pdf(cls, pdf_id: str, shooter_id: int, date_from: str, date_to: str, path: str):
        update = f"""
            UPDATE pdf_lijecnicki 
            SET 
                datum_od='{date_from}', 
                datum_do='{date_to}', 
                path='{path}', 
                id_strijelac={shooter_id} 
            WHERE id={pdf_id}
            """
        return DBManipulator.execute_query(update)

    @classmethod
    def update_notification_shooter_doctor(cls, shooter_id: int, doctor: bool):
        update = f"""UPDATE strijelci_obavijesti SET lijecnicki={1 if doctor else 0} WHERE id_strijelac={shooter_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_notification_shooter_NPIN(cls, shooter_id: int, NPIN: bool):
        update = f"""UPDATE strijelci_obavijesti SET osobna={1 if NPIN else 0} WHERE id_strijelac={shooter_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_notification_shooter_passport(cls, shooter_id: int, passport: bool):
        update = f"""UPDATE strijelci_obavijesti SET putovnica={1 if passport else 0} WHERE id_strijelac={shooter_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_shooter_notifications(cls, shooter_id: int, doctor: bool, NPIN: bool, passport: bool, birthday: bool):
        update = f"""UPDATE strijelci_obavijesti SET osobna={1 if NPIN else 0}, lijecnicki={1 if doctor else 0}, 
                    putovnica={1 if passport else 0}, rodjendan={1 if birthday else 0} WHERE id_strijelac={shooter_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_notification_shooter_birthday(cls, shooter_id: int, birthday: bool):
        update = f"""UPDATE strijelci_obavijesti SET rodjendan={1 if birthday else 0} WHERE id_strijelac={shooter_id}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def update_result(cls, result: sqlTypes.ResultInput, result_id: int):
        empty = "''"  # else '' instead of else empty below does not work, Python completely ignores it as a string
        update = f"""UPDATE dnevnik
                        SET 
                            strijelac_id={result['idStrijelac']}, -- 0 
                            datum='{result['Datum']}', -- 1
                            disciplina={result['Disciplina']}, -- 2
                            program={result['Program']}, -- 3
                            meta={result['Meta']}, -- 4
                            natjecanje={result['idNatjecanja']}, -- 5
                            p={result['P']}, -- 6
                            r10={result['R10'] if isinstance(result['R10'], (int, float)) else empty}, -- 7
                            r20={result['R20'] if isinstance(result['R20'], (int, float)) else empty}, -- 8
                            r30={result['R30'] if isinstance(result['R30'], (int, float)) else empty}, -- 9
                            r40={result['R40'] if isinstance(result['R40'], (int, float)) else empty}, -- 10
                            r50={result['R50'] if isinstance(result['R50'], (int, float)) else empty}, -- 11
                            r60={result['R60'] if isinstance(result['R60'], (int, float)) else empty}, -- 12
                            rezultat={result['Rezultat']}, -- 13
                            ineri={result['Ineri'] if isinstance(result['Ineri'], (int, float)) else empty}, -- 14
                            napomena='{result['Napomena']}' -- 15
                        WHERE id={result_id} -- 16
        """
        return DBManipulator.execute_query(update)

    @classmethod
    def update_shooter_position(cls, shooter_id: int, position: int):
        if not DBChecker.check_shooter_id_exists(shooter_id):
            return -1
        update = f"UPDATE strijelci_pozicije SET pozicija={position} WHERE id_strijelac={shooter_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_strijelci(cls, shooter_id: int, name: str, lastname: str,
                         date_of_birth: str, sex: str):
        """Returns 1 if query is successful, 0 if not, -1 if shooter_id does not exist"""
        if not DBChecker.check_shooter_id_exists(shooter_id):
            return -1
        update = f"UPDATE strijelci SET ime='{name}', prezime='{lastname}', datRod='{date_of_birth}', spol='{sex}' " \
                 f"WHERE id_strijelac={shooter_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_strijelci_dict(self, values: sqlTypes.ShooterBasicInfo):
        if not DBChecker.check_shooter_id_exists(values['id']):
            return -1
        update = f"UPDATE strijelci SET ime='{values['Ime']}', prezime='{values['Prezime']}', " \
                 f"datRod='{values['Datum']}', spol='{values['Spol']}' WHERE id_strijelac={values['id']}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_mete(cls, target_id: int, name: str, description: str):
        """Returns 1 if query is successful, 0 if not, -1 if target_id does not exist"""
        if not DBChecker.check_target_id_exists(target_id):
            return -1
        update = f"UPDATE mete SET naziv='{name}', opis='{description}' WHERE id_meta={target_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_target_position(cls, target_id: int, position: int):
        if not DBChecker.check_target_id_exists(target_id):
            return -1
        update = f"UPDATE mete_pozicije SET pozicija={position} WHERE id_meta={target_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_mete_dict(cls, values: sqlTypes.Target):
        if not DBChecker.check_target_id_exists(values['id']):
            return -1
        update = f"UPDATE mete SET naziv='{values['Naziv']}', opis='{values['Opis']}', WHERE id_meta={values['id']}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_discipline(cls, discipline_id: int, name: str, description: str):
        """Returns 1 if query is successful, 0 if not, -1 if discipline_id does not exist"""
        if not DBChecker.check_discipline_id_exists(discipline_id):
            return -1
        update = f"UPDATE discipline SET naziv='{name}', opis='{description}' WHERE id_disciplina={discipline_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_discipline_dict(cls, values: sqlTypes.Discipline):
        if not DBChecker.check_discipline_id_exists(values['id']):
            return -1
        update = f"UPDATE discipline SET naziv='{values['Naziv']}', opis='{values['Opis']}' " \
                 f"WHERE id_disciplina={values['id']}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_discipline_position(cls, discipline_id: int, position: int):
        if not DBChecker.check_discipline_id_exists(discipline_id):
            return -1
        update = f"UPDATE discipline_pozicije SET pozicija={position} WHERE id_disciplina={discipline_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_programi(cls, program_id: int, name: str, description: str):
        """Returns 1 if query is successful, 0 if not, -1 if program_id does not exist"""
        if not DBChecker.check_program_id_exists(program_id):
            return -1
        update = f"UPDATE programi SET naziv='{name}', opis='{description}' WHERE id_program={program_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_programi_dict(cls, values: sqlTypes.Program):
        if not DBChecker.check_program_id_exists(values['id']):
            return -1
        update = f"UPDATE programi SET naziv='{values['Naziv']}', opis='{values['Opis']}' " \
                 f"WHERE id_program={values['id']}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_program_position(cls, program_id: int, position: int):
        if not DBChecker.check_program_id_exists(program_id):
            return -1
        update = f"UPDATE programi_pozicije SET pozicija={position} WHERE id_program={program_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_natjecanja(cls, competition_id: int, title: str, place: str, address: str, date: str, program: str,
                          note: str, category: int):
        if not DBChecker.check_competition_id_exists(competition_id):
            return -1
        update = f"UPDATE natjecanja SET naziv='{title}', mjesto='{place}', adresa='{address}', datum='{date}', " \
                 f"program='{program}', kategorija={category}, napomena='{note}' WHERE id_natjecanja={competition_id}"
        return DBManipulator.execute_query(update)

    @classmethod
    def update_natjecanja_dict(cls, values: sqlTypes.CompetitionInfo):
        if not DBChecker.check_competition_id_exists(values['id']):
            return -1
        update = f"""UPDATE natjecanja 
                        SET naziv='{values['Naziv']}', 
                            mjesto='{values['Mjesto']}',
                            adresa='{values['Adresa']}', 
                            datum='{values['Datum']}', 
                            program='{values['Program']}',
                            kategorija={values['Kategorija']}, 
                            napomena='{values['Napomena']}',
                            hss_id={values['hss_id']}
                        WHERE id_natjecanja={values['id']}"""
        return DBManipulator.execute_query(update)

    @classmethod
    def set_club_title_and_location(cls, title: str, location: str):
        query = f"""
        UPDATE klub SET naziv='{title}', mjesto='{location}' WHERE rowid=1
        """
        return DBManipulator.execute_query(query)


class DBTables:
    @classmethod
    def create_table_oruzja_servis(cls):
        query = """
        CREATE TABLE IF NOT EXISTS oruzja_servis(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oruzje_id INTEGER,
            datum TEXT,
            napomena TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_kreator_natjecanja(cls):
        query = """
        CREATE TABLE IF NOT EXISTS kreator_natjecanja(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT,
            mjesto TEXT,
            datum TEXT,
            path TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_klub(cls):
        query = """
        CREATE TABLE IF NOT EXISTS klub(
            naziv TEXT,
            mjesto TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_hss_natjecanja(cls):
        query = """
        CREATE TABLE IF NOT EXISTS hss_natjecanja(
            id INTEGER UNIQUE,
            naziv TEXT,
            utc_start INT,
            utc_end INT,
            Mjesto TEXT,
            napomena TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_strijelci_bivsi(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_bivsi(
            id_strijelac INTEGER,
            datUmirovljenja TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_registracije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS registracije(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_strijelac INT,
            datum_od TEXT,
            datum_do TEXT,
            path TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_pdf_lijecnicki(cls):
        query = """
        CREATE TABLE IF NOT EXISTS pdf_lijecnicki(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_strijelac INT,
            datum_od TEXT,
            datum_do TEXT,
            path TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_obavijesti(cls):
        query = """
        CREATE TABLE IF NOT EXISTS obavijesti
        (
            id_obavijesti INTEGER PRIMARY KEY AUTOINCREMENT,
            naslov TEXT,
            tekst TEXT,
            datum TEXT,
            procitana INT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_strijelci(cls):
        query = """
            CREATE TABLE IF NOT EXISTS strijelci
            (
                id_strijelac INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT,
                prezime TEXT,
                spol TEXT,
                datRod TEXT
            );
            """
        DBManipulator.execute_query(query)

    # TODO: datBrisanja u datUmirovljenja
    @classmethod
    def create_table_dnenvik(cls):
        query = """
        CREATE TABLE IF NOT EXISTS dnevnik
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strijelac_id INTEGER,
            datum TEXT,
            disciplina TEXT,
            program TEXT,
            meta TEXT,
            natjecanje INTEGER,
            p INTEGER,
            r10 REAL,
            r20 REAL,
            r30 REAL,
            r40 REAL,
            r50 REAL,
            r60 REAL,
            rezultat REAL,
            ineri INTEGER,
            napomena TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_strijelci_hss(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_hss
        (
            id_strijelac INTEGER,
            oib TEXT,
            mjesto_rod TEXT,
            adresa TEXT,
            mjesto_stan TEXT,
            hss TEXT,
            oi TEXT,
            oi_trajna INTEGER,
            oi_datum TEXT,
            oi_mjesto TEXT,
            putovnica TEXT,
            putovnica_datum TEXT,
            putovnica_postoji INTEGER,
            putovnica_mjesto TEXT,
            drzavljanstvo TEXT,
            strucna_sprema TEXT,
            zaposlenje TEXT, 
            hobi TEXT,
            banka TEXT,
            ziro TEXT,
            telefon_kuca TEXT,
            telefon_posao TEXT,
            mobitel_1 TEXT,
            mobitel_2 TEXT,
            email TEXT,
            registracija INTEGER,
            obavijesti INTEGER,
            lijecnicki TEXT
        )
        """
        DBManipulator.execute_query(query)

    @classmethod  # TODO: natjecanja_pozicije koristiti umjesto 'ukljuceno' iz tablice natjecanja
    def create_table_natjecanja(cls):
        query = """CREATE TABLE IF NOT EXISTS natjecanja
        (
            id_natjecanja INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT,
            mjesto TEXT,
            adresa TEXT,
            datum TEXT,
            program TEXT,
            kategorija INT, 
            napomena TEXT
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_strijelci_pozicije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_pozicije
        (
            id_strijelac INTEGER PRIMARY KEY,
            pozicija INTEGER 
        ) WITHOUT ROWID;
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_natjecanja_pozicije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS natjecanja_pozicije
        (
            id_natjecanja INTEGER UNIQUE,
            pozicija INTEGER
        ) WITHOUT ROWID;
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_mete_pozicije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS mete_pozicije
        (
            id_meta INTEGER PRIMARY KEY,
            pozicija INTEGER
        ) WITHOUT ROWID;
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_programi_pozicije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS programi_pozicije
        (
            id_program INTEGER PRIMARY KEY,
            pozicija INTEGER
        ) WITHOUT ROWID;
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_discipline_pozicije(cls):
        query = """
        CREATE TABLE IF NOT EXISTS discipline_pozicije
        (
            id_disciplina INTEGER PRIMARY KEY,
            pozicija INTEGER
        ) WITHOUT ROWID;
        """
        DBManipulator.execute_query(query)

    # TODO: convert all table references from 'napomene' to 'strijelci_napomene'
    @classmethod
    def create_table_strijelci_napomene(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_napomene
        (
            id_napomena INTEGER PRIMARY KEY AUTOINCREMENT,
            id_strijelac INTEGER,
            napomena TEXT,
            datum TEXT
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_mete(cls):
        query = """
        CREATE TABLE IF NOT EXISTS mete(
            id_meta INTEGER PRIMARY KEY AUTOINCREMENT,
            opis TEXT,
            naziv TEXT UNIQUE
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_programi(cls):
        query = """
        CREATE TABLE IF NOT EXISTS programi(
            id_program INTEGER PRIMARY KEY AUTOINCREMENT,
            opis TEXT,
            naziv TEXT UNIQUE
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_discipline(cls):
        query = """
        CREATE TABLE IF NOT EXISTS discipline(
            id_disciplina INTEGER PRIMARY KEY AUTOINCREMENT,
            opis TEXT,
            naziv TEXT UNIQUE
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_strijelci_obavijesti(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_obavijesti(
            id_strijelac INT UNIQUE,
            osobna INT,
            lijecnicki INT,
            putovnica INT,
            rodjendad INT
        );
        """
        DBManipulator.execute_query(query)

    # TODO: table name change from natjecanja_strijelci to strijelci_na_natjecanju
    @classmethod
    def create_table_strijelci_na_natjecanju(cls):
        query = """
        CREATE TABLE IF NOT EXISTS strijelci_na_natjecanju(
            id_strijelac INT, 
            id_natjecanja INT,
            kategorija INT
        )
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_obavijesti_strijelci(cls):
        query = """
        CREATE TABLE obavijesti_strijelci(
            id_obavijesti INTEGER PRIMARY KEY AUTOINCREMENT,
            id_strijelac INT,
            tekst TEXT,
            datum TEXT,
            procitana INT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_obavijesti_oruzje(cls):
        query = """
        CREATE TABLE obavijesti_oruzje(
            id_obavijesti INTEGER PRIMARY KEY AUTOINCREMENT,
            id_oruzje INT,
            tekst TEXT,
            datum TEXT,
            procitana INT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_oruzje(cls):
        query = """
        CREATE TABLE oruzje(
            vrsta TEXT,
            tip TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serijski_broj TEXT UNIQUE,
            proizvodjac TEXT,
            model TEXT,
            duljina INTEGER,
            visina INTEGER,
            sirina INTEGER,
            duljina_cijevi INTEGER,
            kalibar REAL,
            materijal TEXT,
            masa_okidanja_od INTEGER,
            masa_okidanja_do INTEGER,
            drska_ruka TEXT,
            drska_velicina TEXT,
            napomena TEXT,
            id_strijelac INTEGER
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_drska(cls):
        query = """
        CREATE TABLE drska(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_oruzja INTERGER
            za TEXT,
            velicina TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_cilindar_za_zrak(cls):
        query = """
        CREATE TABLE cilindar_za_zrak(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serijski_broj TEXT UNIQUE,
            proizvodjac TEXT,
            duljina INTEGER,
            kapacitet INTEGER,
            masa INTEGER,
            maksimalni_pritisak INTEGER,
            promjer INTEGER,
            id_oruzje INTEGER,
            vrijedi_do TEXT
        );
        """
        DBManipulator.execute_query(query)

    @classmethod
    def create_table_oruzja_strijelci(cls):
        query = """
        CREATE TABLE IF NOT EXISTS oruzja_strijelci(
            id_strijelac INT,
            id_oruzje INT,
            UNIQUE(id_strijelac, id_oruzje)
        );
        """
        DBManipulator.execute_query(query)


class DBSetter:
    @classmethod
    def prepare_db(cls):
        """Creates all the tables and triggers if they do not exist in the database yet"""
        # create tables
        DBTables.create_table_strijelci()
        DBTables.create_table_strijelci_pozicije()
        DBTables.create_table_strijelci_hss()
        DBTables.create_table_strijelci_obavijesti()
        DBTables.create_table_strijelci_napomene()
        DBTables.create_table_strijelci_bivsi()
        DBTriggers.create_trigger_hss_info_nakon_novog_strijelca()
        # triggers
        DBTriggers.create_trigger_novi_profil_strijelci_obavijesti_nakon_novog_strijelca()
        DBTriggers.create_trigger_novi_profil_strijelci_pozicije_nakon_novog_strijelca()

        # create tables
        DBTables.create_table_discipline()
        DBTables.create_table_discipline_pozicije()
        # triggers
        DBTriggers.create_trigger_novi_profil_discipline_pozicije_nakon_nove_discipline()

        # create tables
        DBTables.create_table_mete()
        DBTables.create_table_mete_pozicije()
        # triggers
        DBTriggers.create_trigger_novi_profil_mete_pozicije_nakon_nove_mete()

        # create tables
        DBTables.create_table_programi()
        DBTables.create_table_programi_pozicije()
        # triggers
        DBTriggers.create_trigger_novi_profil_programi_pozicije_nakon_novog_programa()

        # create table
        DBTables.create_table_natjecanja()
        DBTables.create_table_hss_natjecanja()
        DBTables.create_table_strijelci_na_natjecanju()
        DBTables.create_table_natjecanja_pozicije()

        # triggers
        DBTriggers.create_trigger_novi_profil_natjecanja_pozicije_nakon_novog_natjecanja()

        # create table
        DBTables.create_table_obavijesti()

        # create table pdf_lijecnicki
        DBTables.create_table_pdf_lijecnicki()

        # create table registracije
        DBTables.create_table_registracije()

        DBTables.create_table_klub()

        DBTables.create_table_oruzje()
        DBTables.create_table_cilindar_za_zrak()

        DBTables.create_table_oruzja_servis()
        DBTables.create_table_oruzja_strijelci()

        if not DBGetter.get_club_name():
            DBAdder.add_club("Nepoznato", "Nepoznato")


class DBManipulator:
    connection = None

    @classmethod
    def get_connection(cls):
        if cls.connection is None:
            cls.connection = DBConnector.create_connection()

        return cls.connection

    @classmethod
    def execute_query(cls, query: str, values: list = None):
        """Returns True if query is successful, False if not"""
        db = cls.get_connection()
        cursor = db.cursor()
        try:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            db.commit()
            return True
        except Exception as e:
            return False

    @classmethod
    def fetch_row(cls, query) -> List[tuple]:
        data = []
        try:
            db = cls.get_connection()
            cursor = db.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                data.append(row)
        except Exception as e:
            logging.log(logging.ERROR, e)
            logging.log(logging.ERROR, query)
            data = [()]
        if not data:
            data = [()]
        return data
