from typing_extensions import TypedDict


class CompetitionInfo(TypedDict):
    Naziv: str
    Program: str
    Mjesto: str
    Adresa: str
    Datum: str
    Napomena: str
    Kategorija: int
    id: int
    hss_id: int


# TODO: removed Ukljuceno from sqlTypes.CompetitionWithPosition
class CompetitionWithPosition(CompetitionInfo):
    Pozicija: int


class ShooterRequiredInfo(TypedDict):
    id: int
    Ime: str
    Prezime: str
    Spol: str
    Oib: str
    Datum: str
    MjestoRodjenja: str
    Adresa: str
    MjestoStanovanja: str
    HSS: str


class ShooterContactInfo(TypedDict):
    id: int
    TelefonKuca: str
    TelefonPosao: str
    Mobitel1: str
    Mobitel2: str
    Email: str


class ShooterGeneralInfo(TypedDict):
    id: int
    StrucnaSprema: str
    Zaposlenje: str
    Hobi: str
    Banka: str
    Ziro: str


class ShooterPINInfo(TypedDict):
    id: int
    OI: str
    OIMjesto: str
    OITrajna: int
    OIDatum: str
    Putovnica: str
    PutovnicaDatum: str
    PutovnicaPostoji: int
    PutovnicaMjesto: str
    Drzavljanstvo: str


class ShooterHSSInfo(TypedDict):
    id: int
    Oib: str
    MjestoRodjenja: str
    Adresa: str
    MjestoStanovanja: str
    HSS: str
    OI: str
    OITrajna: int
    OIDatum: str
    OIMjesto: str
    Putovnica: str
    PutovnicaPostoji: int
    PutovnicaMjesto: str
    PutovnicaDatum: str
    Drzavljanstvo: str
    StrucnaSprema: str
    Zaposlenje: str
    Hobi: str
    Banka: str
    Ziro: str
    TelefonKuca: str
    TelefonPosao: str
    Mobitel1: str
    Mobitel2: str
    Email: str
    Registracija: int
    Obavijesti: int
    Lijecnicki: str


class ShooterMinimal(TypedDict):
    Ime: str
    Prezime: str
    id: int


class Shooter(TypedDict):
    Strijelac: str
    id: int


class ShooterBasicInfo(TypedDict):
    Ime: str
    Prezime: str
    Datum: str
    Spol: str
    id: int


class ShooterNotificationsSettings(ShooterBasicInfo):
    Putovnica: int
    Osobna: int
    Lijecnicki: int
    Rodjendan: int

class RetiredShooter(ShooterBasicInfo):
    DatumUmirovljenja: str


class ShootersBasicInfoWithPosition(ShooterBasicInfo):
    Pozicija: int


# TODO: sqlTypes.Program got Opis: str added
class Program(TypedDict):
    Naziv: str
    Opis: str
    id: int


# TODO: removed Ukljuceno from ProgramWithPosition
class ProgramWithPositon(Program):
    Pozicija: int


# TODO: sqlTypes.Target got Opis: str added
class Target(TypedDict):
    Naziv: str
    Opis: str
    id: int


# TODO: sqltypes.TargetWithPosition got Ukljuceno removed
class TargetWithPositon(Target):
    Pozicija: int


# TODO: sqlTypes.Discipline got Opis: str added
class Discipline(TypedDict):
    Naziv: str
    Opis: str
    id: int


# TODO: sqlTypes.DisciplineWithPosition got Ukljuceno removed
class DisciplineWithPosition(Discipline):
    Pozicija: int


class Napomena(TypedDict):
    Tekst: str
    Datum: str
    id: int
    id_strijelac: int


class Result(TypedDict):
    Ime: str
    Prezime: str
    Disciplina: str
    Program: str
    Meta: str
    P: float
    R10: float
    R20: float
    R30: float
    R40: float
    R50: float
    R60: float
    Ineri: int
    Datum: str
    Rezultat: float
    Natjecanje: str
    Napomena: str
    id: int


class ResultInput(TypedDict):
    idStrijelac: int
    Datum: str
    Disciplina: int
    Program: int
    Meta: int
    idNatjecanja: int
    P: int
    R10: float
    R20: float
    R30: float
    R40: float
    R50: float
    R60: float
    Rezultat: float
    Ineri: int
    Napomena: str


class ShooterWithNPINExpireDate(ShooterBasicInfo):
    DatumIstekaOI: str


class ShooterWithDoctorExpireDate(ShooterBasicInfo):
    DatumIstekaLijecnickog: str


class OtherReminder(TypedDict):
    id: int
    Naslov: str
    Tekst: str
    Datum: str
    Procitana: int


class Weapon(TypedDict):
    id: int
    serial_no: str
    manufacturer: str
    model: str


class WeaponHandle(TypedDict):
    hand: str
    size: str


class WeaponBarrel(TypedDict):
    length: int
    caliber: float
    material: str


class WeaponTypeKind(TypedDict):
    type: str
    kind: str


class WeaponTrigger(TypedDict):
    max_mass: int
    min_mass: int


class WeaponDimensions(TypedDict):
    length: int
    width: int
    height: int


class WeaponService(TypedDict):
    id: int
    weapon_id: int
    note: str
    date: str


class WeaponDetails(Weapon):
    kind: str
    type: str
    length: int
    height: int
    width: int
    caliber: float
    material: str
    trigger_mass_from: int
    trigger_mass_to: int
    barrel_length: int
    handle_hand: str
    handle_size: str
    note: str
    shooter_id: int


class AirCylinder(TypedDict):
    id: int
    serial_no: str
    manufacturer: str
    length: int
    capacity: int
    mass: int
    max_pressure: int
    diameter: int
    date_expire: str
    weapon_id: int


class Notification(TypedDict):
    id: int
    title: str
    text: str
    date: str
    bg: str
    fg: str
    type: str
