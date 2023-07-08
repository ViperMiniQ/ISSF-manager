import JSONManager
import ApplicationProperties


_subscribers = []


colors = None


def subscribe(_object):
    _subscribers.append(_object)


def call_subscribers(subscriber=None):
    if subscriber:
        try:
            subscriber.load_colors()
        except AttributeError:
            pass
        finally:
            return

    if subscriber is not None:
        for o in _subscribers:
            if o.__class__.__name__ == subscriber:
                try:
                    o.load_colors()
                except AttributeError:
                    continue
        return

    for o in _subscribers:
        try:
            o.load_colors()
        except AttributeError:
            pass
        finally:
            return


def load_colors():
    global colors
    colors = JSONManager.load_json(ApplicationProperties.COLORS_PATH)


def save_colors():
    JSONManager.save_json(ApplicationProperties.COLORS_PATH, colors)


# TODO: set default if not able to load .json