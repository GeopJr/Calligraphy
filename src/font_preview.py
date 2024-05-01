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

from gi.repository import Gtk, Gsk, Graphene, Gdk
import math

class FontPreview(Gtk.Widget):
    __gtype_name__ = "FontPreview"

    FADE_WIDTH = 168.0 # Adjust when gridview gets merged

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_view = Gtk.TextView.new()
        self.text_view.set_margin_top(12)
        self.text_view.set_margin_bottom(12)
        self.text_view.set_margin_start(18)
        self.text_view.set_margin_end(18)
        self.text_view.width_request = 210
        self.text_view.set_editable(False)
        self.text_view.set_monospace(True)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_hexpand(True)
        self.text_view.set_vexpand(True)
        self.text_view.set_valign(Gtk.Align.CENTER)
        self.text_view.set_focusable(False)
        self.text_view.set_can_focus(False)
        self.text_view.set_parent(self)
        self.text_view.add_css_class("font-size-7")
        self.set_vexpand(True)

    def do_measure(self, orientation, for_size):
        min, nat, min_b, nat_b = self.text_view.measure(orientation, for_size)
        if (orientation == Gtk.Orientation.HORIZONTAL and min > 0):
            min = 0
        return min, nat, min_b, nat_b

    def do_size_allocate(self, width, height, baseline):
        self.text_view.allocate(width, height, baseline, None)

    def do_snapshot(self, snapshot):
        width = self.get_width()
        if width <= 0:
            return

        child_snapshot = Gtk.Snapshot.new()
        self.snapshot_child(self.text_view, child_snapshot)
        node = child_snapshot.to_node()

        if node == None:
            return

        bounds = Gsk.RenderNode.get_bounds(node)
        bounds.origin.x = 0
        bounds.origin.y = math.floor(bounds.origin.y)
        bounds.size.width = width
        bounds.size.height = math.ceil(bounds.size.height) + 1

        snapshot.push_mask(Gsk.MaskMode.INVERTED_ALPHA)

        color1 = Gdk.RGBA()
        color1.red = 0
        color1.green = 0
        color1.blue = 0
        color1.alpha = 1

        color2 = Gdk.RGBA()
        color2.red = 0
        color2.green = 0
        color2.blue = 0
        color2.alpha = 0

        colorstop1 = Gsk.ColorStop()
        colorstop1.offset, colorstop1.color = 0, color1

        colorstop2 = Gsk.ColorStop()
        colorstop2.offset, colorstop2.color = 1, color2

        if (not self.__is_rtl()):
            new_fade = width - self.FADE_WIDTH
            snapshot.append_linear_gradient(
                Graphene.Rect().init(
                    new_fade, bounds.origin.y, self.FADE_WIDTH, bounds.size.height
                ),
                Graphene.Point().init(width, 0),
                Graphene.Point().init(new_fade, 0),
                (colorstop1, colorstop2),
            )
        else:
            snapshot.append_linear_gradient(
                Graphene.Rect().init(
                    0, bounds.origin.y, self.FADE_WIDTH, bounds.size.height
                ),
                Graphene.Point().init(0, 0),
                Graphene.Point().init(self.FADE_WIDTH, 0),
                (colorstop1, colorstop2),
            )

        snapshot.pop()

        snapshot.push_clip(bounds)
        snapshot.append_node(node)
        snapshot.pop()
        snapshot.pop()

        node.unref()

    def __is_rtl(self):
        return Gtk.Widget.get_default_direction() == Gtk.TextDirection.RTL

    def get_buffer(self):
        return self.text_view.get_buffer()
