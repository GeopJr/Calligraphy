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

from .window import CalligraphyWindow


class CalligraphyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.gitlab.gregorni.Calligraphy",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.create_action("quit", lambda *_: self.quit(), ["<primary>q", "<primary>w"])
        self.create_action("about", self.__on_about_action)
        self.create_action("next-font", self.__on_next_font, ["<primary>plus"])
        self.create_action("previous-font", self.__on_previous_font, ["<primary>minus"])
        self.create_action("copy-output", self.__on_copy_output, ["<primary>c"])
        self.create_action("save-output", self.__on_save_output, ["<primary>s"])
        self.create_action(
            "open-output", self.__open_output, param=GLib.VariantType("s")
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CalligraphyWindow(application=self)
        win.present()

    def __on_copy_output(self, *args):
        self.props.active_window.copy_output_to_clipboard()

    def __on_save_output(self, *args):
        self.props.active_window.save_output_to_file()

    def __open_output(self, app, data):
        file_path = data.unpack()
        file = open(file_path, "r")
        fid = file.fileno()
        connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(
            connection,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.OpenURI",
            None,
        )

        try:
            proxy.call_with_unix_fd_list_sync(
                "OpenFile",
                GLib.Variant("(sha{sv})", ("", 0, {"ask": GLib.Variant("b", True)})),
                Gio.DBusCallFlags.NONE,
                -1,
                Gio.UnixFDList.new_from_array([fid]),
                None,
            )
        except Exception as e:
            print(f"Error: {e}")

    def __on_next_font(self, *args):
        self.props.active_window.change_font()

    def __on_previous_font(self, *args):
        self.props.active_window.change_font(True)

    def __on_about_action(self, *args):
        """If you contributed code to the project,
        feel free to add yourself to the devs list.
        To add yourself into the list, you can add your
        name/username, and optionally an email or URL:

        Name only:    gregorni
        Name + URL:   gregorni https://gitlab.com/gregorni/
        Name + Email: gregorni <gregorniehl@web.de>
        """
        # This is a Python list: Add your string to the list (separated by a comma)
        devs_list = ["gregorni https://gitlab.com/gregorni"]

        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name=_("Calligraphy"),
            application_icon="io.gitlab.gregorni.Calligraphy",
            developer_name=_("Calligraphy Contributors"),
            version="2.0",
            developers=devs_list,
            artists=["kramo https://kramo.hu"],
            # Translators: Translate this string as your translator credits.
            # Name only:    gregorni
            # Name + URL:   gregorni https://gitlab.com/gregorni/
            # Name + Email: gregorni <gregorniehl@web.de>
            # Do not remove existing names.
            # Names are separated with newlines.
            translator_credits=_("translator-credits"),
            copyright=_("Copyright © 2023 Calligraphy Contributors"),
            license_type=Gtk.License.GPL_3_0,
            website="https://gitlab.com/gregorni/Calligraphy",
            issue_url="https://gitlab.com/gregorni/Calligraphy/-/issues",
            support_url="https://matrix.to/#/#gregorni-apps:matrix.org",
        )

        about.add_acknowledgement_section(
            _("Code and Design Borrowed from"),
            [
                "Telegraph https://github.com/fkinoshita/Telegraph",
            ],
        )

        about.add_legal_section(
            title="pyfiglet",
            copyright="Copyright © 2018 Christopher Jones, Stefano Rivera, Peter Waller",
            license_type=Gtk.License.MIT_X11,
        )

        about.present()

    def create_action(self, name, callback, shortcuts=None, param=None):
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
    app = CalligraphyApplication()
    return app.run(sys.argv)
