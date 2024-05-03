# font_preview_card.py
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

import threading
from gi.repository import Gtk, GLib
from pyfiglet import Figlet

from . import update_button_sensitivity
from .fonts_list import FONTS_LIST


@Gtk.Template(resource_path="/dev/geopjr/Calligraphy/gtk/font-preview-card.ui")
class FontPreviewCard(Gtk.Box):
    __gtype_name__ = "FontPreviewCard"

    font_name_label = Gtk.Template.Child()
    copy_btn = Gtk.Template.Child()
    output_text_view = Gtk.Template.Child()
    display_stack = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.content_changed_signal_id = -1
        self.first_needed_chars = 10
        self.figlet = None

    def bind(self, parent_window, font_name: str) -> None:
        font_name_str = font_name.get_string()
        self.figlet = FONTS_LIST[font_name_str]
        self.font_name_label.set_label(font_name_str)

        copy_callback = lambda *args: parent_window.show_copied_toast(font_name_str)
        self.copy_btn.connect("clicked", copy_callback)

    def on_content_changed(self, inst, text: str) -> None:
        self.update_text(text)

    def update_text(self, text: str) -> None:
        output_buffer = self.output_text_view.get_buffer()
        if text == "":
            output_buffer.set_text(text)
            return

        full_text = text.replace("\n", " ")
        only_needed_letters = full_text[: self.first_needed_chars]
        output = self.figlet.renderText(only_needed_letters)
        output_buffer.set_text(output)
        self.__update_sensitivity(output != "")

    def __update_sensitivity(self, sensitive: bool) -> None:
        update_button_sensitivity.update(self.copy_btn, sensitive)
        self.display_stack.set_visible_child_name("text" if sensitive else "no-text")
