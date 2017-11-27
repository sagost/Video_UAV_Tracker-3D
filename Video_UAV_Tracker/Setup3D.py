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


from PyQt5.QtWidgets import  QDialog
from PyQt5 import  uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Setup3D.ui'), resource_suffix='')

class Setup3D(QDialog, FORM_CLASS):
    def __init__(self,QgsProject, parent=None):
        super(Setup3D, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.SaveParameter)
        self.Proj = QgsProject

        LayerRegistryItem = self.Proj.instance().mapLayers()
        for id, layer in LayerRegistryItem.items():
            if layer.type() == 1:
                self.comboBox.addItem(layer.name(), id)
                self.comboBox_2.addItem(layer.name(), id)


    def SaveParameter(self):
        DEMName =self.comboBox.itemData(self.comboBox.currentIndex())
        ImageName = self.comboBox_2.itemData(self.comboBox_2.currentIndex())
        self.DEM = self.Proj.instance().mapLayer(DEMName).source()
        self.Image = self.Proj.instance().mapLayer(ImageName).source()
        self.HFilmSize = self.doubleSpinBox.value()
        self.VFilmSize = self.doubleSpinBox_2.value()
        self.FocalLenght = self.doubleSpinBox_3.value()
        if self.radioButton.isChecked() == True:
            self.GPXMODE = 1     # fixed offset
            self.HeadingOffset = self.doubleSpinBox_4.value()
            self.PitchOffset = self.doubleSpinBox_5.value()
            self.RollOffset = self.doubleSpinBox_6.value()
        else:
            self.GPXMODE = 2  # fromGPX



