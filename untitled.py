# -*- coding: utf-8 -*-
"""
/***************************************************************************
 aDialog
                                 A QGIS plugin
 a
                             -------------------
        begin                : 2017-07-24
        git sha              : $Format:%H$
        copyright            : (C) 2017 by a
        email                : a
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QFileInfo

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'untitled.ui'))


class Untitled(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Untitled, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.find.clicked.connect(self.handler)

    def getFilePaths(self):
        return self.path.text(), 'cvs'

    def handler(self, title):
        layerPath = QFileDialog.getOpenFileName(self, u'Abrir CSV', '.', 'CSV (*.CSV)')
        layerInfo = QFileInfo(layerPath)
        self.path.setText(layerPath)
