# window.py
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

import re

import pyfiglet
from gi.repository import Adw, Gdk, Gio, Gtk

from . import get_text_view_text
from .font_preview_card import FontPreviewCard
from .font_view_page import FontViewPage
from .fonts_list import FONTS_LIST


@Gtk.Template(resource_path="/io/gitlab/gregorni/Calligraphy/gtk/window.ui")
class CalligraphyWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CalligraphyWindow"

    search_toggle = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    main_nav_view = Gtk.Template.Child()
    hint_label = Gtk.Template.Child()
    input_text_view = Gtk.Template.Child()
    clear_input_btn = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    welcome_stack = Gtk.Template.Child()
    preview_list_flowbox = Gtk.Template.Child()
    warning_revealer = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings = Gio.Settings(schema_id="io.gitlab.gregorni.Calligraphy")
        settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

        self.search_toggle.connect("toggled", self.__on_search_toggled)

        self.preview_list_flowbox.set_filter_func(self.__filter_func)
        self.search_entry.connect("search-changed", self.__on_search_changed)
        self.search_results_count = 0

        self.input_buffer = self.input_text_view.get_buffer()
        self.input_buffer.connect("changed", self.__on_input_changed)
        self.input_text_view.grab_focus()
        self.notable_input = False

        self.clear_input_btn.connect("clicked", self.__on_input_cleared)

        self.preview_cards_list = []

        for font_name in FONTS_LIST:
            card = FontPreviewCard(parent_window=self, font_name=font_name)
            self.preview_list_flowbox.append(card)
            self.preview_cards_list.append(card)

    def __filter_func(self, flowbox_child):
        search_term = self.search_entry.get_text()
        matches_pattern = (
            lambda pattern: re.search(search_term, pattern, re.IGNORECASE) is not None
        )
        preview_card = flowbox_child.get_child()
        child_matches = matches_pattern(preview_card.font_name) or matches_pattern(
            preview_card.font
        )
        if child_matches:
            self.search_results_count += 1
        return child_matches

    def __on_search_changed(self, *args):
        self.preview_list_flowbox.invalidate_filter()
        if self.notable_input:
            self.welcome_stack.set_visible_child_name(
                "no-results" if self.search_results_count == 0 else "fonts-list"
            )
        else:
            self.welcome_stack.set_visible_child_name("welcome")
        self.search_results_count = 0

    def __on_search_toggled(self, *args):
        open_search = self.search_toggle.get_active()
        self.search_bar.set_search_mode(open_search)
        if open_search:
            self.search_entry.grab_focus()
        else:
            self.search_entry.set_text("")

    def __on_input_changed(self, *args):
        raw_input = get_text_view_text.get(self.input_buffer)
        self.hint_label.set_visible(raw_input == "")

        input_text = raw_input.strip()
        self.notable_input = input_text != ""
        self.welcome_stack.set_visible_child_name(
            "fonts-list" if self.notable_input else "welcome"
        )
        self.search_toggle.set_sensitive(self.notable_input)
        self.clear_input_btn.set_visible(raw_input)

        self.warning_revealer.set_reveal_child(
            re.search(r"[^a-zA-Z\s]", input_text) is not None
        )

        if self.notable_input:
            for card in self.preview_cards_list:
                card.update_text(input_text)
        else:
            self.search_bar.set_search_mode(False)

        current_nav_page = self.main_nav_view.get_visible_page()
        if type(current_nav_page) is FontViewPage:
            current_nav_page.update_text(input_text)

    def __on_input_cleared(self, *args):
        self.input_buffer.set_text("")
        self.input_text_view.grab_focus()

    def show_copied_toast(self, font_name):
        text_to_convert = get_text_view_text.get(self.input_buffer).strip()
        font = FONTS_LIST[font_name]
        text_to_copy = pyfiglet.figlet_format(text_to_convert, font=font).replace(
            " ", "\u00A0"
        )

        Gdk.Display.get_default().get_clipboard().set(text_to_copy)
        # Translators: Do not translate "{font_name}"
        message = _("{font_name} output copied to clipboard").format(
            font_name=font_name
        )
        self.toast_overlay.add_toast(Adw.Toast(title=message))

    def go_to_details_page(self, font_name):
        page = FontViewPage(font_name=font_name, parent_window=self)
        self.main_nav_view.push(page)
        self.__on_input_changed()

    def on_ctrl_f(self, *args):
        on_details_page = type(self.main_nav_view.get_visible_page()) == FontViewPage

        if self.notable_input and not on_details_page:
            open_search = not self.search_toggle.get_active()
            self.search_toggle.set_active(open_search)
            self.__on_search_toggled()
