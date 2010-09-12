#!/usr/bin/python
# Copyright (C) 2010  onox <denkpadje@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import os
import re
from threading import Lock
from urllib import unquote

import pygtk
pygtk.require("2.0")
import gtk

from awn.extras import _, awnlib, __version__
from desktopagnostic import fdo, vfs

import gio
import glib

applet_name = _("Common Folder Launcher")
applet_description = _("Applet to launch common folders and bookmarks")

# Applet's themed icon, also shown in the GTK About dialog
applet_logo = "folder"

# Describes the pattern used to try to decode URLs
url_pattern = re.compile("^[a-z]+://(?:[^@]+@)?([^/]+)/(.*)$")

user_path = os.path.expanduser("~/")
bookmarks_file = os.path.expanduser("~/.gtk-bookmarks")


class CommonFolderApplet:

    """Applet to launch common folders and bookmarks.

    """

    def __init__(self, applet):
        self.applet = applet

        self.__rebuild_lock = Lock()

        self.icon_theme = gtk.icon_theme_get_default()

        # Monitor bookmarks file for changes
        self.__bookmarks_monitor = gio.File(bookmarks_file).monitor_file()  # keep a reference to avoid getting it garbage collected
        def bookmarks_changed_cb(monitor, file, other_file, event):
            if event == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
                with self.__rebuild_lock:
                    self.add_folders_and_bookmarks()
        self.__bookmarks_monitor.connect("changed", bookmarks_changed_cb)

        with self.__rebuild_lock:
            self.add_folders_and_bookmarks()

    def add_folders_and_bookmarks(self):
        self.applet.icons.destroy_all()

        self.add_folder_icon(_("Home Folder"), "user-home", "file://%s" % user_path)
        self.add_folder_icon(_("Desktop"), "user-desktop", "file://%s" % os.path.join(user_path, "Desktop"))

        if os.path.isfile(bookmarks_file):
            with open(bookmarks_file) as f:
                for url_name in (i.rstrip().split(" ", 1) for i in f):
                    if len(url_name) == 1:
                        match = url_pattern.match(url_name[0])
                        if match is not None:
                            url_name.append("/%s on %s" % (match.group(2), match.group(1)))
                        else:
                            basename = glib.filename_display_basename(url_name[0])
                            url_name.append(unquote(str(basename)))
                    uri, name = (url_name[0], url_name[1])

                    if uri.startswith("file://"):
                        if not vfs.File.for_uri(uri).exists():
                            continue
                        file = gio.File(uri)
                        info = file.query_info(gio.FILE_ATTRIBUTE_STANDARD_ICON, gio.FILE_QUERY_INFO_NONE)
                        icon = self.get_icon_name(info.get_attribute_object(gio.FILE_ATTRIBUTE_STANDARD_ICON))
                    else:
                        icon = "folder-remote"

                    self.add_folder_icon(name, icon, uri)

    def add_folder_icon(self, label, icon_name, uri):
        icon = self.applet.icons.add(icon_name, label)
        icon.connect("clicked", self.icon_clicked_cb, uri)

    def icon_clicked_cb(self, widget, uri):
        file = vfs.File.for_uri(uri)

        if file is not None and (not uri.startswith("file://") or file.exists()):
            try:
                file.launch()
            except glib.GError, e:
                print "Error when opening: %s" % e
        else:
            print "File at URI not found (%s)" % uri

    def get_icon_name(self, icon):
        if gio.pygio_version >= (2, 17, 0) and isinstance(icon, gio.EmblemedIcon):
            icon = icon.get_icon()

        if isinstance(icon, gio.ThemedIcon):
            return filter(self.icon_theme.has_icon, icon.get_names())[0]
        elif isinstance(icon, gio.FileIcon):
            return icon.get_file().get_path()


if __name__ == "__main__":
    awnlib.init_start(CommonFolderApplet, {"name": applet_name,
        "short": "common-folder",
        "version": __version__,
        "description": applet_description,
        "theme": applet_logo,
        "author": "onox",
        "copyright-year": 2010,
        "authors": ["onox <denkpadje@gmail.com>"]},
        ["multiple-icons"])
