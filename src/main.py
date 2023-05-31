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
        self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
        self.create_action("about", self.__on_about_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CalligraphyWindow(application=self)
        win.present()

    def __on_about_action(self, *args):
        """If you contributed code or translations,
        feel free to add yourself to the appropriate list.
        To add yourself into the list, you can add your
        name/username, and optionally an email or URL:

        Name only:    gregorni
        Name + URL:   gregorni https://gitlab.com/gregorni/
        Name + Email: gregorni <gregorniehl@web.de>
        """
        # This is a Python list: Add your string to the list (separated by a comma)
        devs_list = ["gregorni https://gitlab.com/gregorni"]
        # This is a string: Add your name to the string (separated by a newline '\n')
        translators_list = "gregorni https://gitlab.com/gregorni"

        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name=_("Calligraphy"),
            application_icon="io.gitlab.gregorni.Calligraphy",
            developer_name=_("Calligraphy Contributors"),
            version="1.2.0",
            developers=devs_list,
            artists=["kramo https://kramo.hu"],
            translator_credits=translators_list,
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

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = CalligraphyApplication()
    return app.run(sys.argv)
