# font_view.py
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

import pyfiglet
from gi.repository import Adw, Gtk

from .fonts_list import FONTS_LIST


@Gtk.Template(resource_path="/io/gitlab/gregorni/Calligraphy/gtk/font-view-page.ui")
class FontViewPage(Adw.NavigationPage):
    __gtype_name__ = "FontViewPage"

    main_stack = Gtk.Template.Child()
    copy_btn = Gtk.Template.Child()
    output_label = Gtk.Template.Child()

    def __init__(self, font_name, parent_window, **kwargs):
        super().__init__(**kwargs)

        self.font = FONTS_LIST[font_name]
        self.set_title(font_name)

        copy_callback = lambda *_: parent_window.show_copied_toast(font_name)
        self.copy_btn.connect("clicked", copy_callback)

    def update_text(self, text):
        empty_text = text == ""
        self.main_stack.set_visible_child_name("no-text" if empty_text else "text-view")
        self.output_label.set_label(pyfiglet.figlet_format(text, font=self.font))
        self.copy_btn.set_sensitive(not empty_text)
