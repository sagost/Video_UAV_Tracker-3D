# -*- coding: utf-8 -*-
'''
Video Uav Tracker  v 2.1 (3D)

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
- Create associated shapefile
- Manage 3d options (select dem and image with same extension and cartographic projection)
- Identify first couple Frame/GpsTime and select it.
- Push Synchronize
- Push Start

Replay:
- Move on map
- Create associated DB shapefile
- Add POI with associated video frame saved
- Add POI directly from video sceen if 3D is active
- Create direct georeferenced mosaic if 3D is active
- Extract frames with associated coordinates for rapid photogrammetry use
'''


import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimediaWidgets import QVideoWidget

import resources

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(736, 625)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/VideoGis/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NewProject.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(NewProject)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.video_frame_2 = QVideoWidget(NewProject)
        p = self.video_frame_2.palette()
        p.setColor(QtGui.QPalette.Window, QtCore.Qt.black)
        self.video_frame_2.setPalette(p)
        self.video_frame_2.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_frame_2.sizePolicy().hasHeightForWidth())
        self.video_frame_2.setSizePolicy(sizePolicy)
        self.video_frame_2.setStyleSheet("background-color: rgb(0, 0, 10);")
        self.video_frame_2.setObjectName("video_frame_2")
        
        # self.scroll = QtWidgets.QScrollArea()#+
        # self.scroll.setWidget(self.video_frame_2)#+
        # self.video_frame_2.setGeometry(0,0,736,625)
        # self.horizontalLayout.addWidget(self.scroll)
        
        self.horizontalLayout.addWidget(self.video_frame_2)


        

        
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 16)
        self.horizontalSlider = QtWidgets.QSlider(NewProject)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout.addWidget(self.horizontalSlider, 1, 0, 1, 16)
        self.replayPlay_pushButton = QtWidgets.QPushButton(NewProject)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.replayPlay_pushButton.sizePolicy().hasHeightForWidth())
        self.replayPlay_pushButton.setSizePolicy(sizePolicy)
        self.replayPlay_pushButton.setCheckable(False)
        self.replayPlay_pushButton.setChecked(False)
        self.replayPlay_pushButton.setObjectName("replayPlay_pushButton")
        self.gridLayout.addWidget(self.replayPlay_pushButton, 3, 1, 1, 1)
        self.replayPosition_label = QtWidgets.QLabel(NewProject)
        self.replayPosition_label.setObjectName("replayPosition_label")
        self.gridLayout.addWidget(self.replayPosition_label, 3, 4, 1, 1)
        self.muteButton = QtWidgets.QToolButton(NewProject)
        self.muteButton.setText("")
        self.muteButton.setObjectName("muteButton")
        self.gridLayout.addWidget(self.muteButton, 3, 2, 1, 1)
        self.comboBox = QtWidgets.QComboBox(NewProject)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 3, 15, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(NewProject)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 3, 13, 1, 1)
        self.toolButton_3 = QtWidgets.QToolButton(NewProject)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/plugins/VideoGis/mIconFormSelect.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_3.setIcon(icon1)
        self.toolButton_3.setObjectName("toolButton_3")
        self.gridLayout.addWidget(self.toolButton_3, 3, 11, 1, 1)
        
        # <<
        self.toolButton = QtWidgets.QToolButton(NewProject)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasPrev.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon5)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 3, 6, 1, 1)
        
        # >>
        self.toolButton_2 = QtWidgets.QToolButton(NewProject)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasNext.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_2.setIcon(icon2)
        self.toolButton_2.setObjectName("toolButton_2")
        self.gridLayout.addWidget(self.toolButton_2, 3, 9, 1, 1)
        
        # <<<
        self.toolButton_6 = QtWidgets.QToolButton(NewProject)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasNext.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_6.setIcon(icon2)
        self.toolButton_6.setObjectName("toolButton_6")
        self.gridLayout.addWidget(self.toolButton_6, 3, 5, 1, 1)
        
        # >>>
        self.toolButton_5 = QtWidgets.QToolButton(NewProject)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionAtlasNext.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_5.setIcon(icon2)
        self.toolButton_5.setObjectName("toolButton_5")
        self.gridLayout.addWidget(self.toolButton_5, 3, 10, 1, 1)
        
        # >
        self.SkipFortoolButton_8 = QtWidgets.QToolButton(NewProject)
        self.SkipFortoolButton_8.setStyleSheet("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowRight.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.SkipFortoolButton_8.setIcon(icon3)
        self.SkipFortoolButton_8.setObjectName("SkipFortoolButton_8")
        self.gridLayout.addWidget(self.SkipFortoolButton_8, 3, 8, 1, 1)
        
        self.SkipBacktoolButton_7 = QtWidgets.QToolButton(NewProject)
        self.SkipBacktoolButton_7.setStyleSheet("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/VgisIcon/mActionArrowLeft.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.SkipBacktoolButton_7.setIcon(icon4)
        self.SkipBacktoolButton_7.setObjectName("SkipBacktoolButton_7")
        self.gridLayout.addWidget(self.SkipBacktoolButton_7, 3, 7, 1, 1)
        

        self.pushButton = QtWidgets.QPushButton(NewProject)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 3, 0, 1, 1)
        self.toolButton_4 = QtWidgets.QToolButton(NewProject)
        self.toolButton_4.setObjectName("toolButton_4")
        self.gridLayout.addWidget(self.toolButton_4, 3, 12, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(NewProject)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 3, 14, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(NewProject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        _translate = QtCore.QCoreApplication.translate
        NewProject.setWindowTitle(_translate("NewProject", "Video UAV Tracker - New Project"))
        self.replayPlay_pushButton.setText(_translate("NewProject", "Play/Pause"))
        self.replayPosition_label.setText(_translate("NewProject", "-:- / -:-"))
        self.pushButton_2.setToolTip(_translate("NewProject", "<html><head/><body><p>Synchronize actual video frame with selected GPS time</p></body></html>"))
        self.comboBox.setToolTip(_translate("NewProject", "<html><head/><body><p> GPS time</p></body></html>"))
        self.pushButton_2.setText(_translate("NewProject", "Synchronize!"))
        self.toolButton_3.setToolTip(_translate("NewProject", "<html><head/><body><p>Add point shape database to project</p></body></html>"))
        #self.toolButton_3.setText(_translate("NewProject", "DB"))
       
        self.toolButton_2.setToolTip(_translate("NewProject", "<html><head/><body><p>Next second</p></body></html>"))
        self.toolButton_2.setText(_translate("NewProject", ">>"))
        
        self.toolButton_6.setToolTip(_translate("NewProject", "<html><head/><body><p>Previous 1min</p></body></html>"))
        self.toolButton_6.setText(_translate("NewProject", "<<<"))
        
        self.toolButton_5.setToolTip(_translate("NewProject", "<html><head/><body><p>Next 1min</p></body></html>"))
        self.toolButton_5.setText(_translate("NewProject", ">>>"))
        
        self.SkipFortoolButton_8.setToolTip(_translate("NewProject", "<html><head/><body><p>Next frame</p></body></html>"))
        self.SkipFortoolButton_8.setText(_translate("NewProject", ">"))
        self.SkipBacktoolButton_7.setToolTip(_translate("NewProject", "<html><head/><body><p>Previous frame</p></body></html>"))
        self.SkipBacktoolButton_7.setText(_translate("NewProject", "<"))
        self.toolButton.setToolTip(_translate("NewProject", "<html><head/><body><p>Previous second</p></body></html>"))
        self.toolButton.setText(_translate("NewProject", "<<"))
        self.pushButton.setToolTip(_translate("NewProject", "<html><head/><body><p>Select video and relative gpx</p></body></html>"))
        self.pushButton.setText(_translate("NewProject", "Select Video and GPX"))
        self.toolButton_4.setText(_translate("NewProject", "3D"))
        self.checkBox.setToolTip(_translate("NewProject","<html><head/><body><p>Activate Pixel value conversion and display (see README)</p></body></html>"))