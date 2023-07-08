import sys
import os
import JSONManager
import datetime
import platform


PLATFORM = "UNKNOWN"
PLATFORM_VERSION = 0

LC_TIME = "hr_HR"

if sys.platform.startswith('linux'):
    PLATFORM = "LINUX"

elif sys.platform.startswith('win32'):
    PLATFORM = "WINDOWS"
    PLATFORM_VERSION = platform.release()
    if '7' in PLATFORM_VERSION:
        LC_TIME = "hr"
    if '10' in PLATFORM_VERSION:
        LC_TIME = "hr_HR"

VERSION: str = "2023-06-29"

LOCATION: str = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else \
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# load splash [READONLY]

_splash_config = None
try:
    _splash_config = JSONManager.load_json(LOCATION + "/Config/Splash.json")
except TypeError:
    pass

_app_properties = None
try:
    _app_properties = JSONManager.load_json(LOCATION + "/Config/ApplicationProperties.json")
except TypeError:
    pass

RESPECT_FONTS_DIVISOR = 0
try:
    RESPECT_FONTS_DIVISOR = _app_properties['respect_font_divisor']
except TypeError:
    pass

SPLASH_FILEPATH = ""
SPLASH_GEOMETRY = {}

if _splash_config:
    SPLASH_FILEPATH: str = LOCATION + _splash_config["filepath"]
    SPLASH_GEOMETRY: dict = _splash_config["geometry"]

CURRENT_DATE: datetime.date = datetime.date.today()  # today() at start, only main GUI should alter after for tests

COMPETITION_MAKER_DBGETTER = None
COMPETITION_MAKER_DBUPDATE = None
COMPETITION_MAKER_DBREMOVER = None

SHOOTER_IMAGES_DIR = LOCATION + "/Data/Images/"
WEAPON_IMAGES_DIR = LOCATION + "/Data/Oruzje/"

FONTS_PATH = LOCATION + "/Config/Fonts2.json"
COLORS_PATH = LOCATION + "/Config/Colors.json"

SHOOTER_NO_PROFILE_IMAGE_PATH = LOCATION + "/Data/no_profile.png"
