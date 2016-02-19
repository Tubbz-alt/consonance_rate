#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright (C) 2015-2016 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of consonance_rate

#    consonance_rate is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    consonance_rate is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with consonance_rate.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals

import signal, sys
import qrc_resources
from pyqtver import*
if pyqtversion == 4:
    from PyQt4 import QtCore
    from PyQt4.QtGui import QApplication, QDialog, QDialogButtonBox, QFileDialog, QPushButton, QScrollArea, QVBoxLayout
    QFileDialog.getOpenFileName = QFileDialog.getOpenFileNameAndFilter
    QFileDialog.getOpenFileNames = QFileDialog.getOpenFileNamesAndFilter
    QFileDialog.getSaveFileName = QFileDialog.getSaveFileNameAndFilter
elif pyqtversion == -4:
    from PySide import QtCore
    from PySide.QtGui import QApplication, QDialog, QDialogButtonBox, QFileDialog, QPushButton, QScrollArea, QVBoxLayout
elif pyqtversion == 5:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFileDialog, QPushButton, QScrollArea, QVBoxLayout

from mw import*

#allows to close the app with CTRL-C from the console
signal.signal(signal.SIGINT, signal.SIG_DFL)

def main(argv):
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/app_icon"))
    x = mainWin(parent=None)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv[1:])
