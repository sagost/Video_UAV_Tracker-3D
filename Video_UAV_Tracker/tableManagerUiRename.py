# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Rename(object):
    def setupUi(self, Rename):
        Rename.setObjectName("Rename")
        Rename.resize(397, 126)
        self.gridlayout = QtWidgets.QGridLayout(Rename)
        self.gridlayout.setObjectName("gridlayout")
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")
        self.label = QtWidgets.QLabel(Rename)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.vboxlayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(Rename)
        self.lineEdit.setMouseTracking(False)
        self.lineEdit.setInputMask("")
        self.lineEdit.setMaxLength(10)
        self.lineEdit.setFrame(True)
        self.lineEdit.setObjectName("lineEdit")
        self.vboxlayout.addWidget(self.lineEdit)
        self.gridlayout.addLayout(self.vboxlayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Rename)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(Rename)
        self.buttonBox.accepted.connect(Rename.accept)
        self.buttonBox.rejected.connect(Rename.reject)
        QtCore.QMetaObject.connectSlotsByName(Rename)

    def retranslateUi(self, Rename):
        _translate = QtCore.QCoreApplication.translate
        Rename.setWindowTitle(_translate("Rename", "Rename field"))
        self.label.setText(_translate("Rename", "Enter new field name:"))

