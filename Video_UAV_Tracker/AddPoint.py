# -*- coding: utf-8 -*-
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

from qgis.gui import QgsMapTool
from PyQt5.QtGui import QCursor,QPixmap
from PyQt5.QtCore import Qt

class AddPointTool(QgsMapTool):
    
    def __init__(self, canvas, layer,Parent):
        QgsMapTool.__init__(self,canvas)
        self.Parent = Parent
        self.canvas=canvas
        self.layer = layer
        self.geom = None
        self.rb = None
        self.x0 = None
        self.y0 = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                  
 
    def canvasPressEvent(self,event):
        layer = self.layer
        x = event.pos().x()
        y = event.pos().y()
        point = self.toLayerCoordinates(layer,event.pos())        
        pointMap = self.toMapCoordinates(layer, point)
        self.x0 = pointMap.x()
        self.y0 = pointMap.y()        
        self.Parent.AddPoint(point.x(),point.y(),-1000)
            
    def canvasMoveEvent(self,event):
        pass            
        
    def canvasReleaseEvent(self,event):
        pass
        
    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True
