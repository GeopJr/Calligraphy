# font_view_page.py
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
from gi.repository import Adw, Gtk, Graphene

from . import update_button_sensitivity
from .fonts_list import FONTS_LIST


@Gtk.Template(resource_path="/dev/geopjr/Calligraphy/gtk/font-view-page.ui")
class FontViewPage(Adw.NavigationPage):
    __gtype_name__ = "FontViewPage"

    main_stack = Gtk.Template.Child()
    copy_btn = Gtk.Template.Child()
    output_label = Gtk.Template.Child()

    def __init__(self, font_name, parent_window, **kwargs):
        super().__init__(**kwargs)

        self.font = FONTS_LIST[font_name]
        self.set_title(font_name)
        self.parent_window = parent_window

        copy_callback = lambda *args: parent_window.show_copied_toast(font_name)
        self.copy_btn.connect("clicked", copy_callback)

    def update_text(self, text):
        output = pyfiglet.figlet_format(text, font=self.font)
        output_exists = output != ""
        self.main_stack.set_visible_child_name(
            "text-view" if output_exists else "no-text"
        )
        self.output_label.set_label(output)

        update_button_sensitivity.update(self.copy_btn, output_exists)

    @Gtk.Template.Callback()
    def screenshot(self, *args):
        dialog = Gtk.FileDialog()
        dialog.set_modal(True)
        dialog.set_initial_name(f"{self.font}.png")
        dialog.save(self.parent_window, None, self.__do_screenshot)

    def __do_screenshot(self, source, res):
        try:
            filename = res.get_source_object().save_finish(res).get_path()
            paintable = Gtk.WidgetPaintable(widget=self.output_label)
            width = self.output_label.get_width()
            height = self.output_label.get_height()
            snapshot = Gtk.Snapshot()
            paintable.snapshot(snapshot, width, height)
            node = snapshot.to_node()
            if node is None:
                print(f"Could not get node snapshot, width: {width}, height: {height}")
                return
            renderer = self.output_label.get_native().get_renderer()

            rect = Graphene.rect_alloc()
            rect.origin = Graphene.Point.zero()
            size = Graphene.Size.alloc()
            size.width = float(width)
            size.height = float(height)
            rect.size = size
            texture = renderer.render_texture(node, rect)
            texture.save_to_png(filename)
        except Exception as e:
            print(e)
