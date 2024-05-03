from gi.repository import Gtk


def is_rtl() -> bool:
    return Gtk.Widget.get_default_direction() == Gtk.TextDirection.RTL
