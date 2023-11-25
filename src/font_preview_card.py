# font_preview.py
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


from gi.repository import Gtk
from pyfiglet import Figlet
import math

from . import update_button_sensitivity
from .fonts_list import FONTS_LIST


@Gtk.Template(resource_path="/io/gitlab/gregorni/Calligraphy/gtk/font-preview-card.ui")
class FontPreviewCard(Gtk.Box):
    __gtype_name__ = "FontPreviewCard"

    font_name_label = Gtk.Template.Child()
    copy_btn = Gtk.Template.Child()
    output_text_view = Gtk.Template.Child()
    show_details_btn = Gtk.Template.Child()
    display_stack = Gtk.Template.Child()
    details_arrow = Gtk.Template.Child()

    def __init__(self, parent_window, font_name, **kwargs):
        super().__init__(**kwargs)

        # Needed for search from window.py
        self.font_name = font_name
        self.font = FONTS_LIST[font_name]

        self.font_name_label.set_label(f"<b>{font_name}</b>")

        self.output_buffer = self.output_text_view.get_buffer()

        copy_callback = lambda *_: parent_window.show_copied_toast(font_name)
        self.copy_btn.connect("clicked", copy_callback)

        details_callback = lambda *_: parent_window.go_to_details_page(font_name)
        self.show_details_btn.connect("clicked", details_callback)

        infinity = float("inf")
        self.figlet = Figlet(font=self.font, width=infinity)

        thinnest_output_char = self.figlet.renderText(".")
        if thinnest_output_char == "":
            thinnest_output_char = self.figlet.renderText("i")
        thinnest_non_whitespace = thinnest_output_char.strip().splitlines()[0].strip()
        width_thinnest_char = len(thinnest_non_whitespace)

        card_width_in_chars = 70
        self.first_needed_chars = int(card_width_in_chars / width_thinnest_char)

    def update_text(self, text):
        first_line = text.splitlines()[0]
        only_needed_letters = first_line[:self.first_needed_chars]
        output = self.figlet.renderText(only_needed_letters)
        self.output_buffer.set_text(output)

        output_exists = output != ""
        self.__update_sensitivity(output_exists)

    def __update_sensitivity(self, sensitive):
        update_button_sensitivity.update(self.copy_btn, sensitive)

        self.display_stack.set_visible_child_name("text" if sensitive else "no-text")

        self.show_details_btn.set_sensitive(sensitive)
        self.details_arrow.set_css_classes(
            ["details-arrow" if sensitive else "dim-label"]
        )
