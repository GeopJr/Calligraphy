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
from gi.repository import Gtk, GLib, GObject
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
    star_revealer = Gtk.Template.Child()
    star_button = Gtk.Template.Child()

    @GObject.Signal(arg_types=(str,))
    def copied(self, *args) -> None:
        return

    @GObject.Signal(arg_types=(str,))
    def starred(self, *args) -> None:
        return

    @GObject.Signal(arg_types=(str,))
    def unstarred(self, *args) -> None:
        return

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.content_changed_signal_id = -1
        self.copy_btn_clicked_signal_id = -1
        self.starred_signal_id = -1
        self.unstarred_signal_id = -1
        self.font_name = None
        self.figlet = None
        self.is_starred = False
        self.connect("state-flags-changed", self.__on_state_flags_changed)
        self.star_button.connect("toggled", self.__on_starred_toggled)
        self.copy_btn.connect("clicked", self.__on_copied)

    def bind(self, font_name: str, starred: bool) -> None:
        self.font_name = font_name
        self.figlet = FONTS_LIST[self.font_name]
        self.font_name_label.set_label(self.font_name)
        self.is_starred = starred
        self.star_button.set_active(starred)

    def unbind(self) -> None:
        if self.copied_signal_id >= 0:
            self.disconnect(self.copied_signal_id)
        if self.unstarred_signal_id >= 0:
            self.disconnect(self.unstarred_signal_id)
        if self.starred_signal_id >= 0:
            self.disconnect(self.starred_signal_id)

    def __on_copied(self, inst) -> None:
        if self.figlet != None:
            self.emit("copied", self.font_name)

    def __on_starred_toggled(self, inst) -> None:
        is_active = self.star_button.get_active()
        state_changed = self.is_starred != is_active

        if is_active:
            self.star_button.add_css_class("enabled")
            self.star_button.set_icon_name("star-large-symbolic")
            self.star_button.set_tooltip_text(_("Unfavorite"))
            if state_changed and self.font_name != None:
                self.emit("starred", self.font_name)
        else:
            self.star_button.remove_css_class("enabled")
            self.star_button.set_icon_name("star-outline-rounded-symbolic")
            self.star_button.set_tooltip_text(_("Favorite"))
            if state_changed and self.font_name != None:
                self.emit("unstarred", self.font_name)

        self.is_starred = is_active

    def __on_state_flags_changed(self, inst, flags) -> None:
        state = self.get_state_flags()
        if (
            state
            & (
                Gtk.StateFlags.PRELIGHT
                | Gtk.StateFlags.ACTIVE
                | Gtk.StateFlags.FOCUSED
                | Gtk.StateFlags.FOCUS_VISIBLE
                | Gtk.StateFlags.FOCUS_WITHIN
            )
        ) != 0:
            self.star_revealer.set_reveal_child(True)
        else:
            self.star_revealer.set_reveal_child(False)

    def on_content_changed(self, inst, text: str) -> None:
        self.update_text(text)

    def update_text(self, text: str) -> None:
        output_buffer = self.output_text_view.get_buffer()
        if text == "":
            output_buffer.set_text(text)
            return

        if self.figlet.width < 1000:
            self.figlet.width = float("inf")
        output = self.figlet.renderText(text)
        output_buffer.set_text(output)
        self.__update_sensitivity(output != "")

    def __update_sensitivity(self, sensitive: bool) -> None:
        update_button_sensitivity.update(self.copy_btn, sensitive)
        self.display_stack.set_visible_child_name("text" if sensitive else "no-text")
