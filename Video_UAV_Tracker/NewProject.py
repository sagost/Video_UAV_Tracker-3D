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

from qgis.core import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import  QUrl , Qt , QVariant , QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import  QFileDialog ,  QStyle, QDialog, QMessageBox ,  QTableWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer,  QMediaContent

from vut_newproject import Ui_NewProject

from tableManagerUi import Ui_Dialog
from tableManagerUiRename import Ui_Rename
from tableManagerUiClone import Ui_Clone
from tableManagerUiInsert import Ui_Insert
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import time
from geographiclib.geodesic import Geodesic
from xml.dom.minidom import parse
from Setup3D import Setup3D

class NewProject(QtWidgets.QWidget, Ui_NewProject):
    
    def __init__(self,projectfile,MainWidget):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.Main = MainWidget
        self.iface = self.Main.iface
        self.muteButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaVolume))
        self.replayPlay_pushButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
        if projectfile.split('.')[-1] =="vut":
            self.projectfile = projectfile
        else:
            self.projectfile = projectfile +'.vut'
        self.videofile = None
        self.GPXfile = None
        self.GPXList = None
        self.fps = None
        self.RealFps = None
        self.DB = None
        self.DEM = None
        self.Image = None
        self.HFilmSize = None
        self.VFilmSize = None
        self.FocalLenght = None
        self.GPXMode = 2
        self.Course = 0
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_frame_2)
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.stateChanged.connect(self.mediaStateChanged)
        self.toolButton_3.clicked.connect(self.ManageDB)
        self.pushButton_2.clicked.connect(self.Synchronize)
        self.pushButton.clicked.connect(self.SelectVideoGPX)
        self.replayPlay_pushButton.clicked.connect(self.PlayPause)
        self.muteButton.clicked.connect(self.MuteUnmute)
        self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.toolButton.clicked.connect(self.SkipBackward)
        self.toolButton_2.clicked.connect(self.SkipForward)
        self.SkipBacktoolButton_7.clicked.connect(self.BackwardFrame)
        self.SkipFortoolButton_8.clicked.connect(self.ForwardFrame)
        self.toolButton_4.clicked.connect(self.Setup3DParameterer)

        if os.name == 'nt':
            self.toolButton_4.setEnabled(False)



    def Setup3DParameterer(self):
        treDOptions = Setup3D(QgsProject)
        a = treDOptions.exec_()
        if a == 1:
            self.DEM = treDOptions.DEM
            self.Image = treDOptions.Image
            self.HFilmSize = treDOptions.HFilmSize
            self.VFilmSize = treDOptions.VFilmSize
            self.FocalLenght = treDOptions.FocalLenght
            self.GPXMode = treDOptions.GPXMODE
            if self.GPXMode == 1:
                self.HeadingOffset = treDOptions.HeadingOffset
                self.PitchOffset = treDOptions.PitchOffset
                self.RollOffset = treDOptions.RollOffset

    def closeEvent(self, *args, **kwargs):
        self.player.stop()
        
        return QtWidgets.QWidget.closeEvent(self, *args, **kwargs)  
    
    def mediaStateChanged(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.replayPlay_pushButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.replayPlay_pushButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
             
    def Synchronize(self):
        TimeItem = self.comboBox.currentIndex()
        duration = self.player.duration()
        position = self.player.position()
        VideoPartLen = round((duration-position) / 1000) 
        GpxPartition = self.GPXList[TimeItem:VideoPartLen+TimeItem]
        outputFile = open(self.projectfile ,'w')
        if self.checkBox.isChecked():
            PixelConversion = str(1)
        else:
            PixelConversion = str(0)

        if self.DB == None:
            outputFile.write('Video UAV Tracker Project v0.2 DO NOT MODIFY'+
                             '\nVideo file location = ' +self.videofile+
                             '\nVideo start at msecond: '+
                              str(self.player.position())+
                              ' #fps = '+str(self.RealFps)+' '+str(self.VideoWidth)+' '+str(self.VideoHeight)+' '+PixelConversion+
                              '\nDB = None'+
                              '\n3D = ' + str(self.DEM) + ',' + str(self.Image) + ',' + str(self.HFilmSize) + ',' + str(self.VFilmSize) + ',' + str(self.FocalLenght) +','+str(self.Course)+
                              '\n'+'Latitude # Longitude # Ele # Speed (m/s) # Course # Time  \n')
        else:
            outputFile.write('Video UAV Tracker Project v0.2 DO NOT MODIFY'+
                             '\nVideo file location = ' +self.videofile+
                             '\nVideo start at msecond: '+
                              str(self.player.position())+
                              ' #fps = '+str(self.RealFps)+' '+str(self.VideoWidth)+' '+str(self.VideoHeight)+' '+PixelConversion+
                              '\nDB = '+str(self.DB.dataProvider().dataSourceUri().split('|')[0])+
                              '\n3D = '+str(self.DEM)+','+str(self.Image)+','+str(self.HFilmSize)+','+str(self.VFilmSize)+','+str(self.FocalLenght)+','+str(self.Course)+
                              '\n'+'Latitude # Longitude # Ele # Speed (m/s) # Course # Time  \n')    
        Counter = 0
        for x in GpxPartition:
            if Counter != 0:
                ActualLatitude = x[1][0]
                ActualLongitude = x[1][1]
                PreviousLatitude = GpxPartition[Counter-1][1][0]
                PreviousLongitude = GpxPartition[Counter-1][1][1]
                GeodesicCalcolus = Geodesic.WGS84.Inverse(PreviousLatitude, PreviousLongitude, ActualLatitude, ActualLongitude)
                Speed = GeodesicCalcolus['s12'] /1
                if self.Course == 1:
                    Course = float(x[1][4])
                    Pitch = float(x[1][5])
                    Roll = float(x[1][6])
                else:
                    Course = GeodesicCalcolus['azi2']
                    if Course < 0:
                        Course += 360
                    Pitch = 0
                    Roll = 0
                if self.GPXMode == 1:      # correct value with fixed offset
                    Course = Course + self.HeadingOffset
                    if Course > 360:
                        Course = Course -360
                    elif Course < 0:
                        Course += 360
                    Pitch = Pitch + self.PitchOffset
                    if Pitch < -180:
                        Pitch = 360 - abs(Pitch)
                    elif Pitch > 180:
                        Pitch = -(360-Pitch)
                    Roll = Roll + self.RollOffset
                    if Roll < -180:
                        Roll = 360 - abs(Roll)
                    elif Roll > 180:
                        Roll = -(360-Roll)

                Ele = x[1][2]
                Time = x[1][3]
                Counter = Counter + 1
            else:
                ActualLatitude = x[1][0]
                ActualLongitude = x[1][1]
                PreviousLatitude = GpxPartition[Counter+1][1][0]
                PreviousLongitude = GpxPartition[Counter+1][1][1]
                GeodesicCalcolus = Geodesic.WGS84.Inverse(ActualLatitude, ActualLongitude, PreviousLatitude, PreviousLongitude)
                Speed = GeodesicCalcolus['s12'] * 1
                if self.Course == 1:
                    Course = float(x[1][4])
                    Pitch = float(x[1][5])
                    Roll = float(x[1][6])
                else:
                    Course = GeodesicCalcolus['azi2']
                    if Course < 0:
                        Course += 360
                    Pitch = 0
                    Roll = 0
                if self.GPXMode == 1:      # correct value with fixed offset
                    Course = Course + self.HeadingOffset
                    if Course > 360:
                        Course = Course -360
                    elif Course < 0:
                        Course += 360
                    Pitch = Pitch + self.PitchOffset
                    if Pitch < -180:
                        Pitch = 360 - abs(Pitch)
                    elif Pitch > 180:
                        Pitch = -(360-Pitch)
                    Roll = Roll + self.RollOffset
                    if Roll < -180:
                        Roll = 360 - abs(Roll)
                    elif Roll > 180:
                        Roll = -(360-Roll)

                Ele = x[1][2]
                Time = x[1][3]
                Counter = Counter + 1  
            outputFile.write(str(ActualLatitude)+' '+str(ActualLongitude)+
                             ' '+str(Ele)+' '+str(Speed)+' '+str(Course)+
                             ' '+str(Pitch)+' '+str(Roll)+' '+str(Time)+'\n')
        outputFile.close() 
        self.Main.LoadProjFromNew(self.projectfile)
        self.close()
         
    def SelectVideoGPX(self):
        if os.name == 'nt':
            ffmpeg = os.path.dirname(__file__)+'/FFMPEG/ffprobe.exe'
            versione = 'ffprobe.exe'
        else:
            ffmpeg = os.path.dirname(__file__)+'/FFMPEG/./ffprobe'
            versione = 'ffprobe'
        if os.path.exists(ffmpeg):
            self.comboBox.clear()
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()    
            self.videofile = None
            self.GPXfile = None
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.videofile, _ = QFileDialog.getOpenFileName(self,"Select Video File", "","All Files (*);;Video File (*.mp4 *.avi *.ogv)", options=options)
            if self.videofile:        
                self.GPXfile, _ = QFileDialog.getOpenFileName(self,"Select GPX file", "","All Files (*);;Video File (*.gpx)", options=options)
                if self.GPXfile:
                    self.Course = 0
                    self.ParseGpx(self.GPXfile)
                    self.LoadVideo(self.videofile)
                    self.replayPosition_label.setText( "-:- / -:-")
        else:
            ret = QMessageBox.warning(self, "Warning", 'missing ffprobe binaries, please download it from https://github.com/sagost/VideoUavTracker/blob/master/FFMPEG/'+versione+' and paste it in /.qgis3/python/plugins/Video_UAV_Tracker/FFMPEG/ ', QMessageBox.Ok)
            self.close()
            
    def ParseGpx(self,GPXfile):
        gpx = parse(GPXfile)
        track = gpx.getElementsByTagName("trkpt")
        GPXList = []
        Error = 0
        GpxProgressiveNumber = 0
        Timestamp = 'Segnaposto'
        for name in track:
            dict = {'Lat': 0, 'Lon': 0, 'Ele': 0, 'Time':0,'Course':0,'Pitch':0,'Roll':0}

            a = (name.toprettyxml(indent = '') ).split()
            for x in a:
                if x.find('lat') == 0:
                    lat = float(x.split('"')[1])
                    dict['Lat'] = float(x.split('"')[1])    
                elif x.find('lon') == 0:
                    lon = float(x.split('"')[1])
                    dict['Lon'] = float(x.split('"')[1])    
                elif x.find('<ele>') == 0:
                    dict['Ele'] = float(x[5:-6])   
                elif x.find('<time>') == 0:
                    
                    try:
                        
                        gpxtime = time.strftime('%Y-%m-%dT%H:%M:%S.%fZ',time.strptime(x[6:-7], '%Y-%m-%dT%H:%M:%S.%fZ'))
                        dict['Time']= x[6:-7]
                        
                    except ValueError:
                        try:
                            gpxtime = time.strftime('%Y-%m-%dT%H:%M:%SZ',time.strptime(x[6:-7],'%Y-%m-%dT%H:%M:%SZ'))
                            dict['Time']= x[6:-7]
                            
                        except ValueError:
                            try:
                                gpxtime = time.strftime('%Y-%m-%dT%H.%M.%S',time.strptime(x[6:-7],'%Y-%m-%dT%H.%M.%S')) 
                                dict['Time']= x[6:-7]
                                             
                            except ValueError:
                                try:
                                    gpxtime = time.strftime('%Y-%m-%dT%H.%M.%S',time.strptime(x[6:-13],'%Y-%m-%dT%H.%M.%S'))
                                    dict['Time']= x[6:-13] 
                                 
                                except ValueError:
                                    try:
                                        gpxtime = time.strftime('%Y-%m-%dT%H.%M.%S',time.strptime(x[6:-13],'%Y-%m-%dT%H:%M:%S'))
                                        dict['Time']= x[6:-13]
                                    except ValueError:
                                        try:
                                            gpxtime = time.strftime('%Y-%m-%dT%H.%M.%S',
                                                                    time.strptime(x[6:-7], '%Y-%m-%dT%H:%M:%S'))
                                            dict['Time'] = x[6:-7]
                                        except ValueError:
                                            Error = 1
                                            FormatoErrore = str(x)
                elif x.find('<course>')==0:
                    dict['Course'] = float(x[8:-9])
                    self.Course = 1
                elif x.find('<yaw>') == 0:
                    dict['Course'] = float(x[5:-6])
                    self.Course = 1
                elif x.find('<pitch>') == 0:
                    dict['Pitch'] = float(x[7:-8])
                elif x.find('<roll>') == 0:
                    dict['Roll'] = float(x[6:-7])


            if dict['Time'] != Timestamp:
                if self.Course == 1:
                    Point = [dict['Lat'], dict['Lon'], dict['Ele'], dict['Time'],dict['Course'],dict['Pitch'],dict['Roll']]
                else:
                    Point = [dict['Lat'],dict['Lon'],dict['Ele'],dict['Time']]
                self.comboBox.addItem(str(GpxProgressiveNumber) + '-'+ gpxtime )    
                GPXList.append([GpxProgressiveNumber,Point])
                GpxProgressiveNumber = GpxProgressiveNumber + 1
                Timestamp = dict['Time'] 
            else:
                Timestamp = dict['Time']
                
        if Error == 0:
            self.GPXList = GPXList
        else:
            ret = QMessageBox.warning(self, "Warning", FormatoErrore +'  UNKOWN GPX TIME FORMAT - ABORTED', QMessageBox.Ok)  
            self.close()
        
    def LoadVideo(self,videofile):
        fps = self.getVideoDetails(str(videofile))
        self.RealFps = float(fps)
        self.fps = (1 / self.RealFps )*1000
        url = QUrl.fromLocalFile(str(self.videofile))
        mc = QMediaContent(url)
        self.player.setMedia(mc)
        self.player.play()
          
    def setPosition(self, position):
        self.player.setPosition(position*1000)
    
    def durationChanged(self, duration):
        duration /= 1000
        self.horizontalSlider.setMaximum(duration)

    def secTotime(self,seconds): 
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            return "%d:%02d:%02d" % (h, m, s)
           
    def positionChanged(self, progress):
        duration = self.player.duration()
        totalTime = self.secTotime(duration/1000)
        actualTime = self.secTotime(progress/1000)
        self.replayPosition_label.setText(actualTime + ' / '+totalTime)
        progress /= 1000
        if not self.horizontalSlider.isSliderDown():
            self.horizontalSlider.setValue(progress) 
               
    def MuteUnmute(self):
        if self.player.mediaStatus() == 6 :
            if self.player.isMuted() == 1:
                self.player.setMuted(0)
                self.muteButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaVolume))
            elif self.player.isMuted() == 0:
                self.player.setMuted(1)
                self.muteButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
                                 
    def PlayPause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()
    
    def getVideoDetails(self,filepath):
        
        filepath2 = '"'+filepath+'"'
        if os.name == 'nt':
            ffmpeg = '"'+os.path.dirname(__file__)[0:-18]+'/Video_UAV_Tracker/FFMPEG/ffprobe.exe'+'"'
        else:
            ffmpeg = os.path.dirname(__file__)+'/FFMPEG/./ffprobe'

        p = os.popen(ffmpeg +  ' -v error -show_format -show_streams '+filepath2)
        lines = p.readlines()
        for l in lines:
            l = l.strip()
            if str(l).startswith("width"):
                self.VideoWidth = str(l).split('=')[1]
            elif str(l).startswith("height"):
                self.VideoHeight = str(l).split('=')[1]
            elif str(l).startswith("r_frame_rate"):
                fps = float(str(l).split('=')[1].split('/')[0] ) / float(str(l).split('=')[1].split('/')[1] )
                return fps

    def SkipForward(self): 
        position = self.player.position()
        self.player.setPosition(position+1000)
    
    def SkipBackward(self): 
        position = self.player.position()
        self.player.setPosition(position-1000)
    
    def ForwardFrame(self):  
        position = self.player.position()
        self.player.setPosition(position+int(self.fps))
    
    def BackwardFrame(self):
        position = self.player.position()
        self.player.setPosition(position-int(self.fps))

    def ManageDB(self):
        self.player.pause()
        shapeFileFirst,_ =  QFileDialog.getSaveFileName(caption = 'Save shape file', filter = "Esri shp (*.shp)")
        if shapeFileFirst:
            if shapeFileFirst.split('.')[-1] == 'shp':
                shapeFile = shapeFileFirst
            else:
                shapeFile = shapeFileFirst + '.shp'
            try:
                os.remove(shapeFile)
                os.remove(shapeFileFirst.split('.')[0]+'.qpg')
                os.remove(shapeFileFirst.split('.')[0]+'.prj')
                os.remove(shapeFileFirst.split('.')[0]+'.cpg')
                os.remove(shapeFileFirst.split('.')[0]+'.shx')
                os.remove(shapeFileFirst.split('.')[0]+'.dbf')
                
            except OSError:
                pass 
            crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            fields = QgsFields()
            QgsVectorFileWriter(shapeFile, "CP1250", fields, QgsWkbTypes.Point, crs, "ESRI Shapefile")
            EmptyLayer = QgsVectorLayer(shapeFile, shapeFile.split('.')[0].split('/')[-1], 'ogr')
            self.dialoga = TableManager(self.iface, EmptyLayer,self)
            self.dialoga.exec_()
    
    def AcceptNewDB(self,DB):
        self.DB = DB
        


########## CLASS TableManager ##############################

class TableManager(QDialog, Ui_Dialog):

  def __init__(self, iface, EmptyLayer, Main):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.Main = Main
    self.layer = EmptyLayer
    self.provider = self.layer.dataProvider()
    self.fields = self.readFields( self.provider.fields() )
    self.isUnsaved = False  # No unsaved changes yet
    if self.provider.storageType() == 'ESRI Shapefile': # Is provider saveable?
      self.isSaveable = True
    else:
      self.isSaveable = False
    self.needsRedraw = True # Preview table is redrawed only on demand. This is for initial drawing.
    self.lastFilter = None
    self.selection = -1     # Don't highlight any field on startup
    self.selection_list = [] #Update: Santiago Banchero 09-06-2009
    self.butUp.clicked.connect(self.doMoveUp)
    self.butDown.clicked.connect(self.doMoveDown)
    self.butDel.clicked.connect(self.doDelete)
    self.butIns.clicked.connect(self.doInsert)
    self.butClone.clicked.connect(self.doClone)
    self.butRename.clicked.connect(self.doRename)
    self.butSaveAs.clicked.connect(self.doSaveAs)
    self.fieldsTable.itemSelectionChanged.connect(self.selectionChanged)
    self.tabWidget.currentChanged.connect(self.drawDataTable)
    self.setWindowTitle(self.tr('Table Manager: {0}').format(self.layer.name()))
    self.drawFieldsTable()
    self.readData()

  def readFields(self, providerFields): # Populates the self.fields dictionary with providerFields
    fieldsDict = {}
    i=0
    for field in providerFields:
        fieldsDict.update({i:field})
        i+=1
    return fieldsDict

  def drawFieldsTable(self): # Draws the fields table on startup and redraws it when changed
    fields = self.fields
    self.fieldsTable.setRowCount(0)
    for i in range(len(fields)):
      self.fieldsTable.setRowCount(i+1)
      item = QTableWidgetItem(fields[i].name())
      item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
      item.setData(Qt.UserRole, i) # set field index
      self.fieldsTable.setItem(i,0,item)
      item = QTableWidgetItem(fields[i].typeName())
      item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
      self.fieldsTable.setItem(i,1,item)
    self.fieldsTable.setColumnWidth(0, 128)
    self.fieldsTable.setColumnWidth(1, 64)

  def readData(self): # Reads data from the 'provider' QgsDataProvider into the 'data' list [[column1] [column2] [column3]...]
    fields = self.fields
    self.data = []
    for i in range(len(fields)):
      self.data += [[]]
    steps = self.provider.featureCount()
    stepp = steps / 10
    if stepp == 0:
      stepp = 1
    progress = self.tr('Reading data ') # As a progress bar is used the main window's status bar, because the own one is not initialized yet
    n = 0
    for feat in self.provider.getFeatures():
        attrs = feat.attributes()
        for i in range(len(attrs)):
            self.data[i] += [attrs[i]]
        n += 1
        if n % stepp == 0:
            progress += '|'
            self.iface.mainWindow().statusBar().showMessage(progress)
    self.iface.mainWindow().statusBar().showMessage('')

  def drawDataTable(self,tab): # Called when user switches tabWidget to the Table Preview
    if tab != 1 or self.needsRedraw == False: return
    fields = self.fields
    self.dataTable.clear()
    self.repaint()
    self.dataTable.setColumnCount(len(fields))
    self.dataTable.setRowCount(self.provider.featureCount())
    header = []
    for i in fields.values():
      header.append(i.name())
    self.dataTable.setHorizontalHeaderLabels(header)
    formatting = True
    if formatting: # slower procedure, with formatting the table items
      for i in range(len(self.data)):
        for j in range(len(self.data[i])):
          item = QTableWidgetItem(unicode(self.data[i][j] or 'NULL'))
          item.setFlags(Qt.ItemIsSelectable)
          if fields[i].type() == 6 or fields[i].type() == 2:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
          self.dataTable.setItem(j,i,item)
    else: # about 25% faster procedure, without formatting
      for i in range(len(self.data)):
        for j in range(len(self.data[i])):
          self.dataTable.setItem(j,i,QTableWidgetItem(unicode(self.data[i][j] or 'NULL')))
    self.dataTable.resizeColumnsToContents()
    self.needsRedraw = False

  def setChanged(self): # Called after making any changes
    self.butSaveAs.setEnabled(True)
    self.isUnsaved = True       # data are unsaved
    self.needsRedraw = True     # preview table needs to redraw

  def selectionChanged(self): # Called when user is changing field selection of field
    self.selection_list = [i for i in range(self.fieldsTable.rowCount()) if self.fieldsTable.item(i,0).isSelected()]
    if len(self.selection_list)==1:
        self.selection = self.selection_list[0]
    else:
        self.selection = -1
    self.butDel.setEnabled( len(self.selection_list)>0 )
    item = self.selection
    if item == -1:
      self.butUp.setEnabled(False)
      self.butDown.setEnabled(False)
      self.butRename.setEnabled(False)
      self.butClone.setEnabled(False)
    else:
      if item == 0:
        self.butUp.setEnabled(False)
      else:
        self.butUp.setEnabled(True)
      if item == self.fieldsTable.rowCount()-1:
        self.butDown.setEnabled(False)
      else:
        self.butDown.setEnabled(True)
      if self.fields[item].type() in [2,6,10]:
         self.butRename.setEnabled(True)
         self.butClone.setEnabled(True)
      else:
        self.butRename.setEnabled(False)
        self.butClone.setEnabled(False)

  def doMoveUp(self): # Called when appropriate button was pressed
    item = self.selection
    tmp = self.fields[item]
    self.fields[item] = self.fields[item-1]
    self.fields[item-1] = tmp
    for i in range(0,2):
      tmp = QTableWidgetItem(self.fieldsTable.item(item,i))
      self.fieldsTable.setItem(item,i,QTableWidgetItem(self.fieldsTable.item(item-1,i)))
      self.fieldsTable.setItem(item-1,i,tmp)
    if item > 0:
      self.fieldsTable.clearSelection()
      self.fieldsTable.setCurrentCell(item-1,0)
    tmp = self.data[item]
    self.data[item]=self.data[item-1]
    self.data[item-1]=tmp
    self.setChanged()

  def doMoveDown(self): # Called when appropriate button was pressed
    item = self.selection
    tmp = self.fields[item]
    self.fields[self.selection] = self.fields[self.selection+1]
    self.fields[self.selection+1] = tmp
    for i in range(0,2):
      tmp = QTableWidgetItem(self.fieldsTable.item(item,i))
      self.fieldsTable.setItem(item,i,QTableWidgetItem(self.fieldsTable.item(item+1,i)))
      self.fieldsTable.setItem(item+1,i,tmp)
    if item < self.fieldsTable.rowCount()-1:
      self.fieldsTable.clearSelection()
      self.fieldsTable.setCurrentCell(item+1,0)
    tmp = self.data[item]
    self.data[item]=self.data[item+1]
    self.data[item+1]=tmp
    self.setChanged()

  def doRename(self): # Called when appropriate button was pressed
    dlg = DialogRename(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      newName = dlg.newName()
      self.fields[self.selection].setName(newName)
      item = self.fieldsTable.item(self.selection,0)
      item.setText(newName)
      self.fieldsTable.setItem(self.selection,0,item)
      self.fieldsTable.setColumnWidth(0, 128)
      self.fieldsTable.setColumnWidth(1, 64)
      self.setChanged()

  def doDelete(self): # Called when appropriate button was pressed
    #self.selection_list = sorted(self.selection_list,reverse=True)
    all_fields_to_del = [self.fields[i].name() for i in self.selection_list if i != -1]
    warning = self.tr('Are you sure you want to remove the following fields?\n{0}').format(", ".join(all_fields_to_del))
    if QMessageBox.warning(self, self.tr('Delete field'), warning , QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
        return
    self.selection_list.sort(reverse=True) # remove them in reverse order to avoid index changes!!!
    for r in self.selection_list:
        if r != -1:
            del(self.data[r])
            del(self.fields[r])
            self.fields = dict(zip(range(len(self.fields)), self.fields.values()))
            self.drawFieldsTable()
            self.setChanged()
    self.selection_list = []
    #</---- Update: Santiago Banchero 09-06-2009 ---->

  def doInsert(self): # Called when appropriate button was pressed
    dlg = DialogInsert(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      (aName, aType, aPos) = dlg.result()
      if aType == 0:
        aLength = 10
        aPrec = 0
        aVariant = QVariant.Int
        aTypeName = 'Integer'
      elif aType == 1:
        aLength = 32
        aPrec = 3
        aVariant = QVariant.Double
        aTypeName = 'Real'
      else:
        aLength = 80
        aPrec = 0
        aVariant = QVariant.String
        aTypeName = 'String'
      self.data += [[]]
      if aPos < len(self.fields):
        fieldsToMove = range(aPos+1,len(self.fields)+1)
        fieldsToMove = reversed(fieldsToMove)
        for i in fieldsToMove:
          self.fields[i] = self.fields[i-1]
          self.data[i] = self.data[i-1]
      self.fields[aPos] = QgsField(aName, aVariant, aTypeName, aLength, aPrec, "")
      aData = []
      if aType == 2:
        aItem = None
      else:
        aItem = None
      for i in range(len(self.data[0])):
        aData += [aItem]
      self.data[aPos] = aData
      self.drawFieldsTable()
      self.fieldsTable.setCurrentCell(aPos,0)
      self.setChanged()

  def doClone(self): # Called when appropriate button was pressed
    dlg = DialogClone(self.iface,self.fields,self.selection)
    if dlg.exec_() == QDialog.Accepted:
      (dst, newName) = dlg.result()
      self.data += [[]]
      movedField = QgsField(self.fields[self.selection])
      movedData = self.data[self.selection]
      if dst < len(self.fields):
        fieldsToMove = range(dst+1,len(self.fields)+1)
        fieldsToMove = reversed(fieldsToMove)
        for i in fieldsToMove:
          self.fields[i] = self.fields[i-1]
          self.data[i] = self.data[i-1]
      self.fields[dst] = movedField
      self.fields[dst].setName(newName)
      self.data[dst] = movedData
      self.drawFieldsTable()
      self.fieldsTable.setCurrentCell(dst,0)
      self.setChanged()

  def doSaveAs(self): # write data to memory layer
         
    # create destination layer
    fields = QgsFields()
    keys = list(self.fields.keys())
    keys.sort()
    for key in keys:
        fields.append(self.fields[key])
    qfields = []
    for field in fields:
        qfields.append(field)    
    self.provider.addAttributes([QgsField('id', QVariant.Int)])    
    self.provider.addAttributes(qfields)    
    self.provider.addAttributes([QgsField("Lon(WGS84)",  QVariant.String),
          QgsField("Lat(WGS84)", QVariant.String),
          QgsField('Image link', QVariant.String)])        
    self.layer.updateExtents()
    self.Main.AcceptNewDB(self.layer)
    self.close()
            
            
                 
class DialogRename(QDialog, Ui_Rename):
    
    
        def __init__(self, iface, fields, selection):
            QDialog.__init__(self)
            self.iface = iface
            self.setupUi(self)
            self.fields = fields
            self.selection = selection
            self.setWindowTitle(self.tr('Rename field: {0}').format(fields[selection].name()))
            self.lineEdit.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
            self.lineEdit.setText(fields[selection].name())
    
        def accept(self):
            if self.newName() == self.fields[self.selection].name():
                QDialog.reject(self)
                return
            for i in self.fields.values():
                if self.newName().upper() == i.name().upper() and i != self.fields[self.selection]:
                    QMessageBox.warning(self,self.tr('Rename field'),self.tr('There is another field with the same name.\nPlease type different one.'))
                    return
                if not self.newName():
                    QMessageBox.warning(self,self.tr('Rename field'),self.tr('The new name cannot be empty'))
                    self.lineEdit.setText(self.fields[self.selection].name())
                    return
                QDialog.accept(self)
                      
        def newName(self):
            return self.lineEdit.text()



########## CLASS DialogClone ##############################

class DialogClone(QDialog, Ui_Clone):
  def __init__(self, iface, fields, selection):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.fields = fields
    self.selection = selection
    self.setWindowTitle(self.tr('Clone field: ')+fields[selection].name())
    self.comboDsn.addItem(self.tr('at the first position'))
    for i in range(len(fields)):
        self.comboDsn.addItem(self.tr('after the {0} field').format(fields[i].name()))
    self.comboDsn.setCurrentIndex(selection+1)
    self.lineDsn.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
    self.lineDsn.setText(fields[selection].name()[:8] + '_2')

  def accept(self):
    if not self.result()[1]:
      QMessageBox.warning(self,self.tr('Clone field'),self.tr('The new name cannot be empty'))
      return
    if self.result()[1] == self.fields[self.selection].name():
        QMessageBox.warning(self,self.tr('Clone field'),self.tr('The new field\'s name must be different then source\'s one!'))
        return
    for i in self.fields.values():
      if self.result()[1].upper() == i.name().upper():
        QMessageBox.warning(self,self.tr('Clone field'),self.tr('There is another field with the same name.\nPlease type different one.'))
        return
    QDialog.accept(self)

  def result(self):
    return self.comboDsn.currentIndex(), self.lineDsn.text()



########## CLASS DialogInsert ##############################

class DialogInsert(QDialog, Ui_Insert):
  def __init__(self, iface, fields, selection):
    QDialog.__init__(self)
    self.iface = iface
    self.setupUi(self)
    self.fields = fields
    self.selection = selection
    self.setWindowTitle(self.tr('Insert field'))
    self.lineName.setValidator(QRegExpValidator(QRegExp('[\w\ _]{,10}'),self))
    self.comboType.addItem(self.tr('Integer'))
    self.comboType.addItem(self.tr('Real'))
    self.comboType.addItem(self.tr('String'))
    self.comboPos.addItem(self.tr('at the first position'))
    for i in range(len(fields)):
      self.comboPos.addItem(self.tr('after the {0} field').format(fields[i].name()))
    self.comboPos.setCurrentIndex(selection+1)

  def accept(self):
    if not self.result()[0]:
      QMessageBox.warning(self,self.tr('Insert new field'),self.tr('The new name cannot be empty'))
      return
    for i in self.fields.values():
      if self.result()[0].upper() == i.name().upper():
        QMessageBox.warning(self,self.tr('Insert new field'),self.tr('There is another field with the same name.\nPlease type different one.'))
        return
    QDialog.accept(self)

  def result(self):
    return self.lineName.text(), self.comboType.currentIndex(), self.comboPos.currentIndex()
