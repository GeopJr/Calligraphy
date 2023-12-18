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

from gi.repository import Adw, Gio, Gtk

from .window import CalligraphyWindow


class CalligraphyApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.gitlab.gregorni.Calligraphy",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.__create_action(
            "search", lambda *args: self.get_active_window().on_ctrl_f(), ["<primary>f"]
        )
        self.__create_action(
            "focus-input",
            lambda *args: self.get_active_window().input_text_view.grab_focus(),
            ["<primary>l"],
        )
        self.__create_action(
            "quit", lambda *args: self.quit(), ["<primary>q", "<primary>w"]
        )
        self.__create_action("about", self.__on_about_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.get_active_window()
        if win == None:
            win = CalligraphyWindow(application=self)
        win.present()

    def __on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutWindow.new_from_appdata(
            "/io/gitlab/gregorni/Calligraphy/appdata.xml", "2.0"
        )
        about.set_transient_for(self.get_active_window())
        about.set_artists(["kramo https://kramo.hu"])
        about.set_designers(["Brage Fuglseth https://bragefuglseth.dev"])
        # These are Python lists: Add your string to the list (separated by a comma)
        # See the translator comment below for possible formats
        about.set_developers(["Gregor Niehl https://gitlab.gnome.org/gregorni"])
        about.set_copyright(_("Copyright © 2023 Calligraphy Contributors"))
        # Translators: Translate this string as your translator credits.
        # Name only:    Gregor Niehl
        # Name + URL:   Gregor Niehl https://gitlab.gnome.org/gregorni/
        # Name + Email: Gregor Niehl <gregorniehl@web.de>
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
