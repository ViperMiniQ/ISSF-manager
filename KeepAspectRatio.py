from typing import Any

_subscribers = []

x = 800
y = 600
startup = "fullscreen"  # can be either full_screen or window


def subscribe(object: Any):
    _subscribers.append(object)


def call_subscribers(subscriber=None):
    print("__calling all subsribers__")
    if subscriber is not None:
        for o in _subscribers:
            if o.__class__.__name__ == subscriber:
                try:
                    o.keep_aspect_ratio()
                    break
                except:
                    pass
        return
    for o in _subscribers:
        try:
            o.keep_aspect_ratio()
        except:
            pass


"""
font modes can either be 'dynamic' or 'static':
    dynamic: 'font_size_division_from_main' needs to be set
    static: module keeps font settings throughout any window size changes, 'font_size_division_from_main' is ignored
"""