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

    def update_text(self, text):
        first_line = text.splitlines()[0]
        output = self.figlet.renderText(first_line)
        self.output_buffer.set_text(output)

        output_exists = output != ""
        update_button_sensitivity.update(self.copy_btn, output_exists)

        self.display_stack.set_visible_child_name(
            "text" if output_exists else "no-text"
        )
