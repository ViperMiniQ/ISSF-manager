# Any module which is supposed to be called from this module
# needs to implement call functions for specific types they are working on

from typing import Any

_shooters_subscribers = []
_disciplines_subscribers = []
_programs_subscribers = []
_targets_subscribers = []
_competitions_subscribers = []
_reminders_subscribers = []
_date_subscribers = []
_weapons_subscribers = []
_air_cylinders_subscribers = []

_shooters = False
_disciplines = False
_programs = False
_targets = False
_competitions = False
_reminders = False
_date = False
_weapons = False
_air_cylinders = False

def subscribe_to_air_cylinders(_object: Any):
    _air_cylinders_subscribers.append(_object)


def subscribe_to_date(_object: Any):
    _date_subscribers.append(_object)


def subscribe_to_reminders(_object: Any):
    _reminders_subscribers.append(_object)


def subscribe_to_targets(_object: Any):
    _targets_subscribers.append(_object)


def subscribe_to_programs(_object: Any):
    _programs_subscribers.append(_object)


def subscribe_to_disciplines(_object: Any):
    _disciplines_subscribers.append(_object)


def subscribe_to_shooters(_object: Any):
    _shooters_subscribers.append(_object)


def subscribe_to_competitions(_object: Any):
    _competitions_subscribers.append(_object)


def subscribe_to_weapons(_object: Any):
    _weapons_subscribers.append(_object)


def _unsubscribe_from_air_cylinders(_object: Any):
    try:
        _air_cylinders_subscribers.remove(_object)
    except ValueError:
        pass


def _unsubscribe_from_weapons(_object: Any):
    try:
        _weapons_subscribers.remove(_object)
    except ValueError:
        pass


def _unsubscribe_from_date(_object: Any):
    try:
        _date_subscribers.remove(_object)
    except ValueError:
        pass


def _unsubscribe_from_reminders(_object: Any):
    try:
        _reminders_subscribers.remove(_object)
    except ValueError:
        pass


def unsubscribe_to_shooters(_object: Any):
    try:
        _shooters_subscribers.remove(_object)
    except ValueError:
        pass


def unsubscribe_to_programs(_object: Any):
    try:
        _programs_subscribers.remove(_object)
    except ValueError:
        pass


def unsubscribe_to_disciplines(_object: Any):
    try:
        _disciplines_subscribers.remove(_object)
    except ValueError:
        pass


def unsubscibe_to_targets(_object: Any):
    try:
        _targets_subscribers.remove(_object)
    except ValueError:
        pass


def unsubscribe_to_competitions(_object: Any):
    try:
        _competitions_subscribers.remove(_object)
    except ValueError:
        pass


def call_refresh_air_cylinders():
    for o in _air_cylinders_subscribers:
        try:
            o.update_air_cylinders()
        except:
            pass


def call_refresh_date():
    for o in _date_subscribers:
        try:
            o.update_date()
        except:
            pass


def call_refresh_reminders():
    for o in _reminders_subscribers:
        try:
            o.update_reminders()
        except:
            pass


def call_refresh_shooters():
    for o in _shooters_subscribers:
        try:
            o.update_shooters()
        except:
            pass


def call_refresh_programs():
    for o in _programs_subscribers:
        try:
            o.update_programs()
        except:
            pass


def call_refresh_disciplines():
    for o in _disciplines_subscribers:
        try:
            o.update_disciplines()
        except:
            pass


def call_refresh_targets():
    for o in _targets_subscribers:
        try:
            o.update_targets()
        except:
            pass


def call_refresh_competitions():
    for o in _competitions_subscribers:
        try:
            o.update_competitions()
        except:
            pass


def call_refresh_weapons():
    for o in _weapons_subscribers:
        try:
            o.update_weapons()
        except:
            pass

def set_air_cylinders(updated: bool = True):
    if isinstance(updated, bool):
        global _air_cylinders
        _air_cylinders = updated


def set_date(updated: bool = True):
    if isinstance(updated, bool):
        global _date
        _date = updated


def set_reminders(updated: bool = True):
    if isinstance(updated, bool):
        global _reminders
        _reminders = updated


def set_shooters(updated: bool = True):
    if isinstance(updated, bool):
        global _shooters
        _shooters = updated


def set_programs(updated: bool = True):
    if isinstance(updated, bool):
        global _programs
        _programs = updated


def set_disciplines(updated: bool = True):
    if isinstance(updated, bool):
        global _disciplines
        _disciplines = updated


def set_targets(updated: bool = True):
    if isinstance(updated, bool):
        global _targets
        _targets = updated


def set_competitions(updated: bool = True):
    if isinstance(updated, bool):
        global _competitions
        _competitions = updated


def set_weapons(updated: bool = True):
    if isinstance(updated, bool):
        global _weapons
        _weapons = updated


def get_air_cylinders_update():
    return _air_cylinders


def get_weapons_update():
    return _weapons


def get_date_update():
    return _date


def get_shooters_update():
    return _shooters


def get_targets_update():
    return _targets


def get_programs_update():
    return _programs


def get_disciplines_update():
    return _disciplines


def get_competitions_update():
    return _competitions
