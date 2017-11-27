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

import os
import sys
from PyQt5 import QtGui, uic ,  QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import  QFileDialog
from NewProject import NewProject
from QGisMap import QGisMap
import resources

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'VideoGis_dockwidget_base.ui'), resource_suffix='')


class VideoGisDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(VideoGisDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.pushButton_2.setEnabled(False)
        self.lineEdit_2.setEnabled(False)
        self.pushButton_8.clicked.connect(self.close)
        self.pushButton_7.clicked.connect(self.NewProj)
        self.pushButton_5.clicked.connect(self.LoadProj)
        self.pushButton_2.clicked.connect(self.Start)

        self.QGisMapWindow = None
        self.NewProjectWindow = None
        self.groupBox.hide()
        
    def closeEvent(self, event):
        if self.QGisMapWindow != None:
            self.QGisMapWindow.close()
        if self.NewProjectWindow != None:
            self.NewProjectWindow.close()
        self.closingPlugin.emit()
        event.accept()

    def NewProj(self):
        self.projectfile = None
        self.pushButton_2.setEnabled(False)
        self.lineEdit_2.clear()
        projectfile, _ = QFileDialog.getSaveFileName(caption = 'Save project file', filter = "VUT Project (*.vut)")
        if projectfile:
            self.NewProjectWindow = NewProject(projectfile,self)
            #self.NewProjectWindow.setWindowModality(2)
            self.NewProjectWindow.show()
        
        
        
    def LoadProjFromNew(self,VutPrj):
        self.NewProjectWindow = None
        self.lineEdit_2.setText(VutPrj)  
        self.projectfile = VutPrj
        self.pushButton_2.setEnabled(True)
        
    
    def LoadProj(self):
        
        
        self.pushButton_2.setEnabled(False)
        self.lineEdit_2.clear()
        self.projectfile, _ = QFileDialog.getOpenFileName(caption = "Select project file",filter = "VUT Project  (*.vut)")
        if self.projectfile != '':
            with open(self.projectfile,'r') as File:
                for line in File:
                    if line[0:23] == 'Video start at msecond:':
                        self.lineEdit_2.setText(self.projectfile)
                        self.pushButton_2.setEnabled(True)
                        break
                
    
    def Start(self):
        
        
        self.QGisMapWindow = QGisMap(self.projectfile,self)
        #self.QGisMapWindow.setWindowModality(2)
        self.QGisMapWindow.show()
