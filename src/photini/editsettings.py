#  Photini - a simple photo metadata editor.
#  http://github.com/jim-easterbrook/Photini
#  Copyright (C) 2012-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

try:
    import keyring
except ImportError:
    keyring = None
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class EditSettings(QtGui.QDialog):
    def __init__(self, parent, config_store):
        QtGui.QDialog.__init__(self, parent)
        self.config_store = config_store
        self.setWindowTitle(self.tr('Photini: settings'))
        self.setLayout(QtGui.QGridLayout())
        self.layout().setRowStretch(0, 1)
        self.layout().setColumnStretch(0, 1)
        # main dialog area
        scroll_area = QtGui.QScrollArea()
        self.layout().addWidget(scroll_area, 0, 0, 1, 2)
        panel = QtGui.QWidget()
        panel.setLayout(QtGui.QFormLayout())
##        panel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        # done button
        done_button = QtGui.QPushButton(self.tr('Done'))
        done_button.clicked.connect(self.accept)
        self.layout().addWidget(done_button, 1, 1)
        # copyright holder name
        self.copyright_name = QtGui.QLineEdit()
        self.copyright_name.setText(
            self.config_store.get('user', 'copyright_name', ''))
        self.copyright_name.editingFinished.connect(self.new_copyright_name)
        self.copyright_name.setMinimumWidth(200)
        panel.layout().addRow(self.tr('Copyright holder'), self.copyright_name)
        # creator name
        self.creator_name = QtGui.QLineEdit()
        self.creator_name.setText(
            self.config_store.get('user', 'creator_name', ''))
        self.creator_name.editingFinished.connect(self.new_creator_name)
        panel.layout().addRow(self.tr('Creator'), self.creator_name)
        # reset flickr
        self.reset_flickr = QtGui.QPushButton(self.tr('OK'))
        self.reset_flickr.setEnabled(
            keyring and keyring.get_password('photini', 'flickr') is not None)
        self.reset_flickr.clicked.connect(self.do_reset_flickr)
        panel.layout().addRow(self.tr('Reset Flickr'), self.reset_flickr)
        # reset picasa
        self.reset_picasa = QtGui.QPushButton(self.tr('OK'))
        self.reset_picasa.setEnabled(
            keyring and keyring.get_password('photini', 'picasa') is not None)
        self.reset_picasa.clicked.connect(self.do_reset_picasa)
        panel.layout().addRow(self.tr('Reset Picasa'), self.reset_picasa)
        # sidecar files
        if_mode = eval(self.config_store.get('files', 'image', 'True'))
        sc_mode = self.config_store.get('files', 'sidecar', 'auto')
        if not if_mode:
            sc_mode = 'always'
        self.sc_always = QtGui.QRadioButton(self.tr('Always create'))
        self.sc_always.setChecked(sc_mode == 'always')
        self.sc_always.clicked.connect(self.new_sc)
        panel.layout().addRow(self.tr('Sidecar files'), self.sc_always)
        self.sc_auto = QtGui.QRadioButton(self.tr('Create if necessary'))
        self.sc_auto.setChecked(sc_mode == 'auto')
        self.sc_auto.setEnabled(if_mode)
        self.sc_auto.clicked.connect(self.new_sc)
        panel.layout().addRow('', self.sc_auto)
        self.sc_delete = QtGui.QRadioButton(self.tr('Delete when possible'))
        self.sc_delete.setChecked(sc_mode == 'delete')
        self.sc_delete.setEnabled(if_mode)
        self.sc_delete.clicked.connect(self.new_sc)
        panel.layout().addRow('', self.sc_delete)
        # image file locking
        self.write_if = QtGui.QCheckBox(self.tr('(when possible)'))
        self.write_if.setChecked(if_mode)
        self.write_if.clicked.connect(self.new_write_if)
        panel.layout().addRow(self.tr('Write to image'), self.write_if)
        # add panel to scroll area after its size is known
        scroll_area.setWidget(panel)

    def new_copyright_name(self):
        value = self.copyright_name.text()
        self.config_store.set('user', 'copyright_name', value)

    def new_creator_name(self):
        value = self.creator_name.text()
        self.config_store.set('user', 'creator_name', value)

    def do_reset_flickr(self):
        if keyring.get_password('photini', 'flickr'):
            keyring.delete_password('photini', 'flickr')
        self.reset_flickr.setDisabled(True)

    def do_reset_picasa(self):
        if keyring.get_password('photini', 'picasa'):
            keyring.delete_password('photini', 'picasa')
        self.reset_picasa.setDisabled(True)

    def new_sc(self):
        if self.sc_always.isChecked():
            sc_mode = 'always'
        elif self.sc_auto.isChecked():
            sc_mode = 'auto'
        else:
            sc_mode = 'delete'
        self.config_store.set('files', 'sidecar', sc_mode)

    def new_write_if(self):
        if_mode = self.write_if.isChecked()
        self.config_store.set('files', 'image', str(if_mode))
        self.sc_auto.setEnabled(if_mode)
        self.sc_delete.setEnabled(if_mode)
        if not if_mode:
            self.sc_always.setChecked(True)
            self.new_sc()
