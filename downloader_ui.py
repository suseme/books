# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'res\downloader.ui'
#
# Created: Mon Mar 14 15:16:26 2016
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(576, 175)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_id = QtGui.QLineEdit(Dialog)
        self.lineEdit_id.setObjectName(_fromUtf8("lineEdit_id"))
        self.horizontalLayout.addWidget(self.lineEdit_id)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit_name = QtGui.QLineEdit(Dialog)
        self.lineEdit_name.setObjectName(_fromUtf8("lineEdit_name"))
        self.horizontalLayout.addWidget(self.lineEdit_name)
        self.pushButton_start = QtGui.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/img/Download_73.119383825417px_1183408_easyicon.net.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_start.setIcon(icon)
        self.pushButton_start.setCheckable(True)
        self.pushButton_start.setObjectName(_fromUtf8("pushButton_start"))
        self.horizontalLayout.addWidget(self.pushButton_start)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.textEdit = QtGui.QTextEdit(Dialog)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.pushButton_start, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), Dialog.do_start)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("when_message(QString)")), self.textEdit.append)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("when_id(QString)")), self.lineEdit_id.setText)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("when_name(QString)")), self.lineEdit_name.setText)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("when_progress(int)")), self.progressBar.setValue)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("finished(int)")), Dialog.do_stop)
        QtCore.QObject.connect(Dialog, QtCore.SIGNAL(_fromUtf8("when_title(QString)")), Dialog.setWindowTitle)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "ID", None))
        self.label_2.setText(_translate("Dialog", "Name", None))
        self.pushButton_start.setText(_translate("Dialog", "Start", None))

import res_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

