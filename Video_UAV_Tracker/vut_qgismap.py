# -*- coding: utf-8 -*-
'''
Video Uav Tracker 3D  v 2.1

Replay a video in sync with a gps track displayed on the map.


     -------------------
copyright    : (C) 2017 by Salvatore Agosta
email          : sagost@katamail.com


This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.


INSTRUCTION:

ATTENTION: 3D IS NOT TESTED ON WINDOWS PLATFORM
- Pixel value query need a .npz archive containing one array data for every frame, it must be named as 'VideoFile.npz' and be in the same folder of 'VideoFile.mp4'
- for 3d options install numpy,panda3d and pypng python3 modules
- Download all files from https://github.com/sagost/Video_UAV_Tracker-3D/Video_UAV_Tracker/FFMPEG and copy them in your Video_Uav_Tracker/FFMPEG folder

Syncing:
- Create new project
- Select video and .gpx track (1 trkpt per second)
- Identify first couple Frame/GpsTime and select it.
- Push Synchronize
- Push Start

Replay:
- Move on map
- Create associated DB shapefile
- Add POI with associated video frame saved
- Extract frames with associated coordinates for rapid photogrammetry use
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QKeySequence

import resources

class Scroller(QtWidgets.QScrollArea):
    def __init__(self):
        QtWidgets.QScrollArea.__init__(self)
        self._oldPos = None
    def wheelEvent(self,ev):
        if ev.type() == QtCore.QEvent.Wheel:
            ev.ignore()
#     def mouseMoveEvent(self, event):
#
#         if event.buttons() != Qt.LeftButton:
#             self._oldpos = event.pos()
#
#         if event.buttons() & Qt.LeftButton:
#             if self._oldpos is not None:
#              delta = event.pos() - self._oldpos
#              print('delta: ', delta.x, delta.y)
#              self.setVerticalScrollBar()
#              self.setHorizontalScrollBar()
             
             

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(706, 493)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/VideoGis/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setKerning(True)
        self.pushButton_3.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/VgisIcon/Hand-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setAutoExclusive(False)
        self.pushButton_3.setAutoDefault(False)
        self.pushButton_3.setDefault(False)
        self.pushButton_3.setFlat(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.toolButton_6 = QtWidgets.QToolButton(Form)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/plugins/VideoGis/iconNewTabEditorConsole.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_6.setIcon(icon2)
        self.toolButton_6.setObjectName("toolButton_6")
        self.horizontalLayout.addWidget(self.toolButton_6)
        self.toolButton_7 = QtWidgets.QToolButton(Form)
        self.toolButton_7.setEnabled(False)
        self.toolButton_7.setCheckable(True)
        self.toolButton_7.setObjectName("toolButton_7")
        self.horizontalLayout.addWidget(self.toolButton_7)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setEnabled(False)
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setEnabled(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.spinBox = QtWidgets.QSpinBox(Form)
        self.spinBox.setEnabled(False)
        self.spinBox.setMinimum(1)
        self.spinBox.setSingleStep(10)
        self.spinBox.setProperty("value", 25)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.spinBox)
        spacerItem = QtWidgets.QSpacerItem(23, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.toolButton_4 = QtWidgets.QToolButton(Form)
        self.toolButton_4.setObjectName("toolButton_4")
        self.horizontalLayout.addWidget(self.toolButton_4)
        self.toolButton_5 = QtWidgets.QToolButton(Form)
        self.toolButton_5.setObjectName("toolButton_5")
        self.horizontalLayout.addWidget(self.toolButton_5)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.dockWidget_2 = QtWidgets.QDockWidget(Form)
        self.dockWidget_2.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidgetContents_7 = QtWidgets.QWidget()
        self.dockWidgetContents_7.setObjectName("dockWidgetContents_7")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.dockWidgetContents_7)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.video_frame = QVideoWidget(Form)
        p = self.video_frame.palette()
        p.setColor(QtGui.QPalette.Window, QtCore.Qt.black)
        self.video_frame.setPalette(p)
        self.video_frame.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_frame.sizePolicy().hasHeightForWidth())
        self.video_frame.setSizePolicy(sizePolicy)
        self.video_frame.setMinimumSize(QtCore.QSize(200, 200))
        self.video_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.video_frame.setObjectName("video_frame")
        
        self.scroll = Scroller()
        self.scroll.setMinimumSize(QtCore.QSize(200, 200))
        self.scroll.setSizePolicy(sizePolicy)
        self.scroll.setObjectName("scroll_frame")
        self.scroll.setWidget(self.video_frame)
        self.scroll.setAlignment(QtCore.Qt.AlignCenter)
        
        self.video_frame.resize(self.scroll.size())
    
        self.verticalLayout.addWidget(self.scroll)
        
        # self.verticalLayout.addWidget(self.video_frame)
        
        self.horizontalSlider = QtWidgets.QSlider(self.dockWidgetContents_7)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalLayout.addWidget(self.horizontalSlider)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(98, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        
        #<<<
        self.toolButton_previous1min = QtWidgets.QToolButton(self.dockWidgetContents_7)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowLeft.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButton_previous1min.setIcon(icon3)
        self.toolButton_previous1min.setObjectName("toolButton_previous1min")
        self.horizontalLayout_3.addWidget(self.toolButton_previous1min)
        
        #<<
        self.toolButton_11 = QtWidgets.QToolButton(self.dockWidgetContents_7)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowLeft.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButton_11.setIcon(icon3)
        self.toolButton_11.setObjectName("toolButton_11")
        self.horizontalLayout_3.addWidget(self.toolButton_11)
        
        #<
        self.SkipBacktoolButton_8 = QtWidgets.QToolButton(self.dockWidgetContents_7)
        self.SkipBacktoolButton_8.setStyleSheet("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasPrev.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.SkipBacktoolButton_8.setIcon(icon4)
        self.SkipBacktoolButton_8.setObjectName("SkipBacktoolButton_8")
        self.horizontalLayout_3.addWidget(self.SkipBacktoolButton_8)
        
        # start/pause
        self.playButton = QtWidgets.QToolButton(self.dockWidgetContents_7)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_3.addWidget(self.playButton)
        
        #mute
        self.muteButton = QtWidgets.QToolButton(self.dockWidgetContents_7)
        self.muteButton.setText("")
        self.muteButton.setObjectName("muteButton")
        self.horizontalLayout_3.addWidget(self.muteButton)
        
        #replay
        self.replayPosition_label = QtWidgets.QLabel(self.dockWidgetContents_7)
        self.replayPosition_label.setObjectName("replayPosition_label")
        self.horizontalLayout_3.addWidget(self.replayPosition_label)
        
        #>
        self.SkipFortoolButton_9 = QtWidgets.QToolButton(self.dockWidgetContents_7)
        self.SkipFortoolButton_9.setStyleSheet("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasNext.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.SkipFortoolButton_9.setIcon(icon5)
        self.SkipFortoolButton_9.setObjectName("SkipFortoolButton_9")
        self.horizontalLayout_3.addWidget(self.SkipFortoolButton_9)

        
        #>>
        self.toolButton_12 = QtWidgets.QToolButton(self.dockWidgetContents_7)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowRight.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButton_12.setIcon(icon6)
        self.toolButton_12.setObjectName("toolButton_12")
        self.horizontalLayout_3.addWidget(self.toolButton_12)
        
        #>>>
        self.toolButton_next1min = QtWidgets.QToolButton(self.dockWidgetContents_7)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowRight.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButton_next1min.setIcon(icon6)
        self.toolButton_next1min.setObjectName("toolButton_next1min")
        self.horizontalLayout_3.addWidget(self.toolButton_next1min)
        
        spacerItem2 = QtWidgets.QSpacerItem(98, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.lcdNumber = QtWidgets.QLCDNumber(self.dockWidgetContents_7)
        self.lcdNumber.setObjectName("lcdNumber")
        self.horizontalLayout_3.addWidget(self.lcdNumber)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.dockWidget_2.setWidget(self.dockWidgetContents_7)
        self.verticalLayout_3.addWidget(self.dockWidget_2)
        self.dockWidget_4 = QtWidgets.QDockWidget(Form)
        self.dockWidget_4.setMaximumSize(QtCore.QSize(524287, 121))
        self.dockWidget_4.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_4.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.dockWidget_4.setObjectName("dockWidget_4")
        self.dockWidgetContents_6 = QtWidgets.QWidget()
        self.dockWidgetContents_6.setObjectName("dockWidgetContents_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.dockWidgetContents_6)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButtonCutA_6 = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButtonCutA_6.setEnabled(True)
        self.pushButtonCutA_6.setObjectName("pushButtonCutA_6")
        self.horizontalLayout_2.addWidget(self.pushButtonCutA_6)
        self.pushButtonCutB_6 = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButtonCutB_6.setObjectName("pushButtonCutB_6")
        self.horizontalLayout_2.addWidget(self.pushButtonCutB_6)
        self.label_7 = QtWidgets.QLabel(self.dockWidgetContents_6)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.dockWidgetContents_6)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_2)
        self.comboBox_6 = QtWidgets.QComboBox(self.dockWidgetContents_6)
        self.comboBox_6.setObjectName("comboBox_6")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox_6)
        self.pushButton_5 = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.pushButtonCut_2 = QtWidgets.QPushButton(self.dockWidgetContents_6)
        self.pushButtonCut_2.setObjectName("pushButtonCut_2")
        self.horizontalLayout_2.addWidget(self.pushButtonCut_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.progressBar = QtWidgets.QProgressBar(self.dockWidgetContents_6)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)
        self.dockWidget_4.setWidget(self.dockWidgetContents_6)
        self.verticalLayout_3.addWidget(self.dockWidget_4)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Video UAV Tracker - Player"))
        self.pushButton_3.setToolTip(_translate("Form", "<html><head/><body><p>Move along Video directly clicking on gps track</p></body></html>"))
        self.pushButton_3.setText(_translate("Form", "MapTool   "))
        self.label_2.setText(_translate("Form", "Overlap %"))
        self.toolButton_6.setToolTip(_translate("Form", "<html><head/><body><p>Add point</p></body></html>"))
        self.toolButton_6.setText(_translate("Form", "o"))
        self.toolButton_4.setToolTip(_translate("Form", "<html><head/><body><p>Enable extract frames toolbox</p><p><br/></p></body></html>"))
        self.toolButton_4.setText(_translate("Form", "Extract frames"))
        self.toolButton_5.setText(_translate("Form", "Close"))
        
        self.toolButton_previous1min.setText(_translate("Form", "<<<"))
        self.toolButton_11.setText(_translate("Form", "<<"))
        self.SkipBacktoolButton_8.setText(_translate("Form", "<"))
        self.playButton.setText(_translate("Form", "> / ||"))
        self.replayPosition_label.setText(_translate("Form", "-:- / -:-"))
        self.SkipFortoolButton_9.setText(_translate("Form", ">"))
        self.toolButton_12.setText(_translate("Form", ">>"))
        self.toolButton_next1min.setText(_translate("Form", ">>>"))
        
        
        self.label.setText(_translate("Form", "Export Frames Tool"))
        self.pushButtonCutA_6.setToolTip(_translate("Form", "<html><head/><body><p>Export from actual Video Frame</p></body></html>"))
        self.pushButtonCutA_6.setText(_translate("Form", "From A"))
        self.pushButtonCutB_6.setToolTip(_translate("Form", "<html><head/><body><p>Export to actual Video Frame</p></body></html>"))
        self.pushButtonCutB_6.setText(_translate("Form", "To B"))
        self.label_7.setText(_translate("Form", "Pick one frame every"))
        self.comboBox_6.setItemText(0, _translate("Form", "meters"))
        self.comboBox_6.setItemText(1, _translate("Form", "seconds"))
        self.pushButton_5.setText(_translate("Form", "Cancel"))
        self.pushButtonCut_2.setText(_translate("Form", "Extract!"))
        self.toolButton_7.setText(_translate("Form", "3D"))
        self.pushButton.setText(_translate("Form", "Create Mosaic"))

