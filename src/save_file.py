# save_file.py
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

from gi.repository import Adw, Gio, GLib, Gtk


class SaveFile:
    def save(self, parent):
        self.parent = parent

        def __on_response(_dialog, response):
            """Run if the user selects a file."""
            if response == Gtk.ResponseType.ACCEPT:
                self.on_save_file(_dialog.get_file())

        dialog = Gtk.FileChooserNative.new(
            title=_("Select a location"),
            parent=self.parent,
            action=Gtk.FileChooserAction.SAVE,
        )

        dialog.set_modal(True)
        dialog.connect("response", __on_response)
        dialog.set_current_name("output.txt")
        dialog.show()

    def on_save_file(self, file):
        print(f"Output file: {file.get_path()}")
        text = self.parent.output_buffer.get_text(
            self.parent.output_buffer.get_start_iter(),
            self.parent.output_buffer.get_end_iter(),
            False,
        )
        if not text:
            return
        bytes = GLib.Bytes.new(text.encode("utf-8"))
        file.replace_contents_bytes_async(
            bytes,
            None,
            False,
            Gio.FileCreateFlags.NONE,
            None,
            self.__save_file_complete,
        )

    def __save_file_complete(self, file, result):
        info = file.query_info("standard::display-name", Gio.FileQueryInfoFlags.NONE)
        display_name = (
            info.get_attribute_string("standard::display-name")
            if info
            else file.get_basename()
        )

        toast = Adw.Toast(
            # Translators: Do not translate "{display_name}"
            title=_('Unable to save "{display_name}"').format(display_name=display_name)
        )
        if not file.replace_contents_finish(result):
            print(f"Unable to save {display_name}")
        else:
            toast.set_title(
                # Translators: Do not translate "{display_name}"
                _('"{display_name}" saved').format(display_name=display_name)
            )
            toast.set_button_label(_("Open"))
            toast.props.action_name = "app.open-output"
            toast.props.action_target = GLib.Variant("s", file.get_path())

        self.parent.toast_overlay.add_toast(toast)
