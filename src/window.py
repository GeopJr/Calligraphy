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

import pyfiglet
from gi.repository import Adw, Gdk, Gio, Gtk

from .fonts_list import FONTS_LIST
from .save_file import SaveFile


@Gtk.Template(resource_path="/io/gitlab/gregorni/Calligraphy/gtk/window.ui")
class CalligraphyWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CalligraphyWindow"

    window_box = Gtk.Template.Child()
    output_text_view = Gtk.Template.Child()
    input_text_view = Gtk.Template.Child()
    to_clipboard_btn = Gtk.Template.Child()
    to_file_btn = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    toolbar = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings = Gio.Settings(schema_id="io.gitlab.gregorni.Calligraphy")
        settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

        self.input_buffer = self.input_text_view.get_buffer()
        self.input_buffer.connect("changed", self.__on_input_changed)

        self.output_buffer = self.output_text_view.get_buffer()

        self.to_clipboard_btn.connect("clicked", self.copy_output_to_clipboard)
        self.to_file_btn.connect("clicked", lambda *_: SaveFile().save(self))

        self.select_font_dropdown = self.__create_fonts_dropdown()

        settings.bind(
            "selected-font",
            self.select_font_dropdown,
            "selected",
            Gio.SettingsBindFlags.DEFAULT,
        )
        self.select_font_dropdown.connect("notify::selected", self.__on_input_changed)
        self.toolbar.prepend(self.select_font_dropdown)

        self.scrolled_distance = 0

    def do_size_allocate(self, width, height, baseline):
        self.window_box.props.orientation = (
            Gtk.Orientation.VERTICAL if width < 800 else Gtk.Orientation.HORIZONTAL
        )

        Adw.ApplicationWindow.do_size_allocate(self, width, height, baseline)

    def __text_as_figlet(self):
        return str(
            pyfiglet.figlet_format(
                self.input_buffer.get_text(
                    self.input_buffer.get_start_iter(),
                    self.input_buffer.get_end_iter(),
                    False,
                ),
                FONTS_LIST[self.select_font_dropdown.get_selected_item().get_string()],
            )
        )

    def __on_input_changed(self, *args):
        self.output_buffer.set_text(self.__text_as_figlet())
        self.to_clipboard_btn.set_sensitive(self.__text_as_figlet() != "")
        self.to_file_btn.set_sensitive(self.__text_as_figlet() != "")

    def copy_output_to_clipboard(self, *args):
        if self.__text_as_figlet() != "":
            Gdk.Display.get_default().get_clipboard().set(self.__text_as_figlet())
            self.toast_overlay.add_toast(Adw.Toast(title=_("Copied to clipboard")))

    def __on_scrolled(self, scroll, dx, dy):
        self.scrolled_distance += dy / (
            2
            if scroll.get_current_event_device().get_source() == Gdk.InputSource.MOUSE
            else 50
        )

        if abs(self.scrolled_distance) >= 1:
            self.change_font(min(1, max(-1, self.scrolled_distance)) <= -1)
            self.scrolled_distance = 0

    def change_font(self, back=False):
        dropdown = self.select_font_dropdown
        dropdown.set_selected(
            max(
                min(
                    dropdown.get_selected() - 1
                    if back
                    else dropdown.get_selected() + 1,
                    len(dropdown.get_model()) - 1,
                ),
                0,
            )
        )

    def __create_fonts_dropdown(self):
        string_list_items = "\n".ljust(11).join(
            [f"<item>{font}</item>" for font in FONTS_LIST]
        )

        builder = Gtk.Builder.new_from_string(
            f"""
            <interface>
              <object class="GtkDropDown" id="fonts_dropdown">
                <property name="width-request">150</property>
                <property name="tooltip-text">{_('Scroll to change font')}</property>

                <property name="model">
                  <object class="GtkStringList" id="string_list">
                    <items>
                      {string_list_items}
                    </items>
                  </object>
                </property>

                <property name="enable-search">true</property>
                <property name="expression">
                  <lookup type="GtkStringObject" name="string"/>
                </property>

                <child>
                  <object class="GtkEventControllerScroll" id="scroller">
                    <property name="flags">vertical</property>
                  </object>
                </child>
              </object>
            </interface>
            """,
            -1,
        )
        builder.get_object("scroller").connect("scroll", self.__on_scrolled)

        return builder.get_object("fonts_dropdown")
