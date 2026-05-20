#!/usr/bin/env python3
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk, Gio, Adw, GtkSource
from window import ReviveNotesWindow

class ReviveNotesApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.github.revivenotes",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.set_accels_for_action("win.new-tab", ["<Ctrl>t"])
        self.set_accels_for_action("win.close-tab", ["<Ctrl>w"])
        self.set_accels_for_action("win.search", ["<Ctrl>f"])
        self.set_accels_for_action("win.save-file", ["<Ctrl>s"])
        self.set_accels_for_action("win.save-as-file", ["<Ctrl><Shift>s"])
        self.set_accels_for_action("win.open-file", ["<Ctrl>o"])
        self.set_accels_for_action("win.next-tab", ["<Ctrl>Tab"])
        self.set_accels_for_action("win.prev-tab", ["<Ctrl><Shift>Tab"])
        self.set_accels_for_action("win.replace", ["<Ctrl>h"])
        self.set_accels_for_action("win.zoom-in", ["<Ctrl>plus", "<Ctrl>equal"])
        self.set_accels_for_action("win.zoom-out", ["<Ctrl>minus"])
        self.set_accels_for_action("win.zoom-reset", ["<Ctrl>0"])
        self.set_accels_for_action("win.toggle-wrap", ["<Alt>z"])

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = ReviveNotesWindow(application=self)
        win.present()

    def do_open(self, files, n_files, hint):
        self.do_activate()
        win = self.props.active_window
        for file in files:
            win.open_file(file.get_path())

if __name__ == '__main__':
    app = ReviveNotesApp()
    app.run(sys.argv)
