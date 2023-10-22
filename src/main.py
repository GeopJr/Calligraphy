# main.py
#
# Copyright 2023 Calligraphy Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

from .save_file import SaveFile
from .window import CalligraphyWindow


class CalligraphyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.gitlab.gregorni.Calligraphy",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.__create_action(
            "quit", lambda *_: self.quit(), ["<primary>q", "<primary>w"]
        )
        self.__create_action("about", self.__on_about_action)
        self.__create_action(
            "next-font",
            lambda *_: self.get_active_window().change_font(),
            ["<primary>plus"],
        )
        self.__create_action(
            "previous-font",
            lambda *_: self.get_active_window().change_font(back=True),
            ["<primary>minus"],
        )
        self.__create_action(
            "copy-output",
            # TODO: lambda is only there to prevent Python from checking if self.get_active_window() exists
            lambda *_: self.get_active_window().copy_output_to_clipboard(),
            ["<primary><shift>c"],
        )
        self.__create_action(
            "save-output",
            lambda *_: SaveFile().save(self.get_active_window()),
            ["<primary><shift>s", "<primary>s"],
        )
        self.__create_action(
            "open-output", self.__open_output, param=GLib.VariantType("s")
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.get_active_window()
        if win is None:
            win = CalligraphyWindow(application=self)
        win.present()

    def __open_output(self, app, data):
        try:
            file = open(data.unpack(), "r")
            Gio.DBusProxy.new_sync(
                Gio.bus_get_sync(Gio.BusType.SESSION, None),
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.OpenURI",
                None,
            ).call_with_unix_fd_list_sync(
                "OpenFile",
                GLib.Variant("(sha{sv})", ("", 0, {"ask": GLib.Variant("b", True)})),
                Gio.DBusCallFlags.NONE,
                -1,
                Gio.UnixFDList.new_from_array([file.fileno()]),
                None,
            )
        except Exception as e:
            print(f"Error saving file: {e}")

    def __on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutWindow.new_from_appdata(
            "/io/gitlab/gregorni/Calligraphy/appdata.xml"
        )
        about.set_transient_for(self.get_active_window())
        about.set_artists(["kramo https://kramo.hu"])
        about.set_developer_name(_("Calligraphy Contributors"))
        # These are Python lists: Add your string to the list (separated by a comma)
        # See the translator comment below for possible formats
        about.set_developers(["gregorni https://gitlab.gnome.org/gregorni"])
        about.set_copyright(_("Copyright © 2023 Calligraphy Contributors"))
        # Translators: Translate this string as your translator credits.
        # Name only:    gregorni
        # Name + URL:   gregorni https://gitlab.gnome.org/gregorni/
        # Name + Email: gregorni <gregorniehl@web.de>
        # Do not remove existing names.
        # Names are separated with newlines.
        about.set_translator_credits(_("translator-credits"))

        about.add_legal_section(
            title="pyfiglet",
            copyright="Copyright © 2018 Christopher Jones, Stefano Rivera, Peter Waller",
            license_type=Gtk.License.MIT_X11,
        )

        about.present()

    def __create_action(self, name, callback, shortcuts=None, param=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, param)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    return CalligraphyApplication().run(sys.argv)
