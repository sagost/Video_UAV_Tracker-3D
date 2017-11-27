# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Clone(object):
    def setupUi(self, Clone):
        Clone.setObjectName("Clone")
        Clone.resize(375, 210)
        self.gridlayout = QtWidgets.QGridLayout(Clone)
        self.gridlayout.setObjectName("gridlayout")
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.vboxlayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(Clone)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.vboxlayout.addWidget(self.label)
        self.lineDsn = QtWidgets.QLineEdit(Clone)
        self.lineDsn.setMouseTracking(False)
        self.lineDsn.setInputMask("")
        self.lineDsn.setMaxLength(10)
        self.lineDsn.setFrame(True)
        self.lineDsn.setObjectName("lineDsn")
        self.vboxlayout.addWidget(self.lineDsn)
        self.label_3 = QtWidgets.QLabel(Clone)
        self.label_3.setObjectName("label_3")
        self.vboxlayout.addWidget(self.label_3)
        self.comboDsn = QtWidgets.QComboBox(Clone)
        self.comboDsn.setObjectName("comboDsn")
        self.vboxlayout.addWidget(self.comboDsn)
        self.gridlayout.addLayout(self.vboxlayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Clone)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.gridlayout.addItem(spacerItem1, 1, 0, 1, 1)

        self.retranslateUi(Clone)
        self.buttonBox.accepted.connect(Clone.accept)
        self.buttonBox.rejected.connect(Clone.reject)
        QtCore.QMetaObject.connectSlotsByName(Clone)
        Clone.setTabOrder(self.lineDsn, self.comboDsn)
        Clone.setTabOrder(self.comboDsn, self.buttonBox)

    def retranslateUi(self, Clone):
        _translate = QtCore.QCoreApplication.translate
        Clone.setWindowTitle(_translate("Clone", "Clone field"))
        self.label.setText(_translate("Clone", "A name for the new field:"))
        self.label_3.setText(_translate("Clone", "Insert at position:"))

