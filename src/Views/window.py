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
import threading
import pyfiglet
from enum import Enum
from gi.repository import Adw, Gdk, Gio, Gtk, GObject, GLib

from . import get_text_view_text
from .font_preview import FontPreview
from .font_preview_card import FontPreviewCard
from .font_view_page import FontViewPage
from .fonts_list import FONTS_LIST, convert_to_fonts
from . import env


@Gtk.Template(resource_path="/dev/geopjr/Calligraphy/gtk/window.ui")
class CalligraphyWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CalligraphyWindow"

    class Page(Enum):
        WELCOME = 1
        FONT_LIST = 2
        NO_RESULTS = 3

    search_toggle = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    main_nav_view = Gtk.Template.Child()
    hint_label = Gtk.Template.Child()
    input_text_view = Gtk.Template.Child()
    clear_input_btn = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    welcome_stack = Gtk.Template.Child()
    preview_list_grid_view = Gtk.Template.Child()
    warning_revealer = Gtk.Template.Child()
    toolbarview = Gtk.Template.Child()
    win_title = Gtk.Template.Child()

    preview_first_needed_chars = 15
    safe_regex = re.compile(r"[^a-zA-Z\s]")
    __wrap = True
    __favs = {}

    @GObject.Property(type=bool, default=True)
    def wrap(self) -> bool:
        return self.__wrap

    @wrap.setter
    def wrap(self, value: bool) -> None:
        self.__wrap = value

    @GObject.Property(type=GObject.TYPE_STRV)
    def favs(self) -> list[str]:
        return self.__favs

    @favs.setter
    def favs(self, value: list[str]) -> None:
        self.__favs = value

    @GObject.Signal(arg_types=(str,))
    def content_changed(self, *args) -> None:
        return

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="dev.geopjr.Calligraphy")
        self.settings.delay()

        bind_flags = Gio.SettingsBindFlags.DEFAULT
        self.settings.bind("window-width", self, "default-width", bind_flags)
        self.settings.bind("window-height", self, "default-height", bind_flags)
        self.settings.bind("window-is-maximized", self, "maximized", bind_flags)
        self.settings.bind("wrap", self, "wrap", bind_flags)
        self.settings.bind("favs", self, "favs", bind_flags)

        if env.DEVEL:
            self.add_css_class("devel")

        self.current_input = ""
        self.preview_list_grid_view.remove_css_class("view")

        self.font_name_list = Gtk.StringList.new()
        self.font_filter = Gtk.StringFilter.new(
            Gtk.PropertyExpression.new(Gtk.StringObject, None, "string")
        )
        self.font_filter.set_match_mode(Gtk.StringFilterMatchMode.PREFIX)
        self.model = Gtk.FilterListModel.new(self.font_name_list, self.font_filter)
        self.no_selection_model = Gtk.NoSelection.new(self.model)

        thread = threading.Thread(target=self.__populate_fonts)
        thread.daemon = True
        thread.start()

        self.item_factory = Gtk.SignalListItemFactory()
        self.item_factory.connect("setup", self.__item_setup)
        self.item_factory.connect("bind", self.__item_bind)
        self.item_factory.connect("unbind", self.__item_unbind)

        self.preview_list_grid_view.set_factory(self.item_factory)
        self.preview_list_grid_view.set_model(self.no_selection_model)
        self.preview_list_grid_view.connect("activate", self.__item_activate)

        self.search_bar.connect_entry(self.search_entry)
        self.search_entry.connect("search-changed", self.__on_search_changed)

        self.input_text_preview = ""
        self.input_text_view.get_buffer().connect("changed", self.__on_input_changed)
        self.input_text_view.grab_focus()
        self.notable_input = False

        self.clear_input_btn.connect("clicked", self.__on_input_cleared)

        capture_gesture = Gtk.GestureClick.new()
        capture_gesture.connect("pressed", self.__capture_click)
        self.input_text_view.add_controller(capture_gesture)

    def __capture_click(self, gesture, button, x, y):
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def do_close_request(self) -> bool:
        self.settings.apply()
        return False

    def __populate_fonts(self) -> None:
        convert_to_fonts()
        GLib.idle_add(self.__update_fonts)

    def __update_fonts(self) -> None:
        fonts = self.__font_names_with_favs()
        self.font_name_list.splice(0, 0, fonts)
        self.toolbarview.set_reveal_bottom_bars(True)

    def __update_favs(self) -> None:
        fonts = self.__font_names_with_favs()
        self.font_name_list.splice(0, len(fonts), fonts)

    def __font_names_with_favs(self) -> list[str]:
        fonts = list(FONTS_LIST.keys())
        for fav in reversed(self.favs):
            fonts.insert(0, fonts.pop(fonts.index(fav)))
        return fonts

    def __item_setup(
        self, _factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ) -> None:
        list_item.set_child(FontPreviewCard())

    def __item_bind(
        self, _factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ) -> None:
        fpc = list_item.get_child()
        font_name = list_item.get_item().get_string()
        fpc.bind(font_name=font_name, starred=font_name in self.favs)
        fpc.content_changed_signal_id = self.connect(
            "content-changed", fpc.on_content_changed
        )
        fpc.copied_signal_id = fpc.connect("copied", self.__on_copied)
        fpc.unstarred_signal_id = fpc.connect("unstarred", self.__on_unstarred)
        fpc.starred_signal_id = fpc.connect("starred", self.__on_starred)
        fpc.update_text(self.current_input)

    def __item_unbind(
        self, _factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ) -> None:
        fpc = list_item.get_child()
        fpc.unbind()
        if fpc.content_changed_signal_id >= 0:
            self.disconnect(fpc.content_changed_signal_id)

    def __item_activate(self, _list, pos: int) -> None:
        font_name = self.no_selection_model.get_item(pos)
        if not font_name:
            return
        self.go_to_details_page(font_name.get_string())

    def __on_copied(self, inst, font_name: str) -> None:
        self.show_copied_toast(font_name)

    def __on_unstarred(self, inst, font_name: str) -> None:
        if font_name in self.favs:
            self.favs.remove(font_name)
            self.favs = self.favs

    def __on_starred(self, inst, font_name: str) -> None:
        if font_name in self.favs:
            return
        self.favs.append(font_name)
        self.favs = self.favs

    def __on_search_changed(self, *args) -> None:
        self.font_filter.set_search(self.search_entry.get_text())
        page = self.Page.WELCOME
        if self.notable_input:
            page_to_set = self.Page.FONT_LIST
            if self.model.get_n_items() == 0:
                page_to_set = self.Page.NO_RESULTS

            self.set_visible_page(page_to_set)

    def __on_input_changed(self, *args) -> None:
        raw_input = get_text_view_text.get(self.input_text_view.get_buffer())
        self.hint_label.set_visible(raw_input == "")

        input_text = raw_input.strip()
        self.notable_input = input_text != ""
        self.search_toggle.set_sensitive(self.notable_input)
        self.search_bar.set_sensitive(self.notable_input)
        self.clear_input_btn.set_visible(raw_input)

        contains_invalid_char = self.safe_regex.search(input_text) != None
        self.warning_revealer.set_reveal_child(contains_invalid_char)

        if self.notable_input:
            page_to_set = self.Page.FONT_LIST

            sliced_input = input_text.replace("\n", " ")[
                : self.preview_first_needed_chars
            ]
            if sliced_input != self.input_text_preview:
                self.input_text_preview = sliced_input
                self.emit(
                    "content-changed",
                    sliced_input,
                )
        else:
            page_to_set = self.Page.WELCOME
            self.search_bar.set_search_mode(False)

        self.current_input = input_text

        if not self.search_bar.get_search_mode():
            self.set_visible_page(page_to_set)

        current_nav_page = self.main_nav_view.get_visible_page()
        if type(current_nav_page) == FontViewPage:
            current_nav_page.update_text(input_text)

    def __on_input_cleared(self, *args) -> None:
        self.input_text_view.get_buffer().set_text("")
        self.input_text_view.grab_focus()

    def show_copied_toast(self, font_name: str) -> None:
        text_to_convert = get_text_view_text.get(
            self.input_text_view.get_buffer()
        ).strip()
        text_to_copy = (
            FONTS_LIST[font_name].renderText(text_to_convert).replace(" ", "\u00A0")
        )

        Gdk.Display.get_default().get_clipboard().set(text_to_copy)
        # Translators: Do not translate "{font_name}"
        message = _("{font_name} output copied to clipboard").format(
            font_name=font_name
        )
        self.toast_overlay.add_toast(Adw.Toast(title=message))

    def go_to_details_page(self, font_name: str) -> None:
        page = FontViewPage(font_name=font_name, parent_window=self)
        self.main_nav_view.push(page)
        self.__on_input_changed()

    def on_ctrl_f(self, *args) -> None:
        on_details_page = type(self.main_nav_view.get_visible_page()) == FontViewPage

        if self.notable_input and not on_details_page:
            open_search = not self.search_toggle.get_active()
            self.search_toggle.set_active(open_search)

    def set_visible_page(self, page) -> None:
        match page:
            case self.Page.FONT_LIST:
                page_name = "fonts-list"
                page_title = _("Fonts")
            case self.Page.NO_RESULTS:
                page_name = "no-results"
                page_title = _("No Results")
            case _:
                page_name = "welcome"
                page_title = _("Calligraphy")
        self.win_title.set_title(page_title)
        self.welcome_stack.set_visible_child_name(page_name)
