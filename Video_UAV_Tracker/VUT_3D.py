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
import time

from direct.showbase.ShowBase import ShowBase
from direct.task import Task


from panda3d.core import ShaderTerrainMesh, Shader, load_prc_file_data, PNMImage, Filename, BitMask32
from panda3d.core import Vec3, PerspectiveLens
from panda3d.core import Point3,LineSegs,LPoint2f

from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress,NetDatagram

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import ZUp

from direct.interval.LerpInterval import LerpPosHprInterval
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.PythonUtil import fitDestAngle2Src

import numpy
from osgeo import gdal,osr,ogr
import png


class Video_UAV_Tracker_3D(ShowBase):

    def __init__(self, Input16bitTif,Texture,HFilmSize,VFilmSize,FocalLenght,VUTProject,Directory,videoFile,VideoWidth,VideoHeight,StartSecond,BBXMin,BBYMin,BBXMax,BBYMax):  # , cameraCoord):

        load_prc_file_data("", """
            textures-power-2 none
            gl-coordinate-system default
            window-title Video UAV Tracker 3D
        """)

        ShowBase.__init__(self)

        self.set_background_color(0.4, 0.4, 1)
        self.setFrameRateMeter(True)

        self.lens = PerspectiveLens()
        self.lens.setFilmSize(float(HFilmSize)/1000, float(VFilmSize)/1000)
        self.lens.setFocalLength(float(FocalLenght)/1000)
        base.cam.node().setLens(self.lens)



        self.VRTBoundingBox = str(BBXMin) + ',' + str(BBYMin) + ':' + str(BBXMax) + ',' + str(BBYMax)
        self.SetupCommunication()
        self.ManageDEM(Input16bitTif)
        self.SetupTexture(Texture)
        self.SetupVisibleTerrain()
        self.SetupBulletTerrain()
        self.accept("f3", self.toggleWireframe)
        self.EraseTmpFiles()
        self.Directory = Directory
        self.SetupModel(VUTProject)
        self.VideoFile = videoFile
        self.VideoWidth = VideoWidth
        self.VideoHeight = VideoHeight
        self.StartSecond = StartSecond
        self.OutputDir = self.VideoFile.split('.')[0]+'_Mosaic/'
        self.Mosaic = False
        self.MosaicCounter = 0
        self.taskMgr.setupTaskChain('MosaicChain', numThreads = 1, tickClock = None,
                       threadPriority = None, frameBudget = None,
                       frameSync = None, timeslicePriority = None)
        self.SendReadySignal(str(Directory))

    def ActivateMosaics(self):
        if not self.Mosaic:
            self.Mosaic = True
            self.TaskCounter = 0
            self.LastProjectedPolygon = None
            if not os.path.exists(self.OutputDir):
                os.makedirs(self.OutputDir)
            self.task_mgr.add(self.ProcessFrustrum,'CreateMosaic',taskChain='MosaicChain')
        else:
            self.Mosaic = False
            self.task_mgr.remove('CreateMosaic')

    def RayTrace(self,ScreenPoint):
        pFrom = Point3()
        pTo = Point3()
        self.cam.node().getLens().extrude(ScreenPoint, pFrom, pTo)

        pFrom = self.render.getRelativePoint(self.cam, pFrom)
        pTo = self.render.getRelativePoint(self.cam, pTo)
        result = self.world.rayTestClosest(pFrom, pTo)

        result2 = self.render.getRelativePoint(self.worldNP, result.getHitPos())
        return (result2[0] + self.Origin[0], result2[1] + self.Origin[1], result2[2])

    def ProcessFrustrum(self,task):

        VideoTime = self.Moves.get_t()
        UL = LPoint2f(-0.9,0.9)     #Up left
        MU = LPoint2f(0,0.9)        #Middle Up
        UR = LPoint2f(0.9,0.9)      #Up Right
        MR = LPoint2f(0.9,0)        #Middle Right
        LR = LPoint2f(0.9, -0.9)    #Low Right
        MD = LPoint2f(0, -0.9)      #Middle Down
        LL = LPoint2f(-0.9, -0.9)   #Low Left
        ML = LPoint2f(-0.9, 0)      #Middle Left

        UL_XYZ = self.RayTrace(UL)
        UR_XYZ = self.RayTrace(UR)
        LR_XYZ = self.RayTrace(LR)
        LL_XYZ = self.RayTrace(LL)

        ring = ogr.Geometry(type=ogr.wkbLinearRing)
        ring.AddPoint(UL_XYZ[0], UL_XYZ[1],0)
        ring.AddPoint(UR_XYZ[0], UR_XYZ[1],0)
        ring.AddPoint(LR_XYZ[0], LR_XYZ[1],0)
        ring.AddPoint(LL_XYZ[0], LL_XYZ[1],0)
        ring.AddPoint(UL_XYZ[0], UL_XYZ[1],0)

        # Create polygon
        poly = ogr.Geometry(type=ogr.wkbPolygon)
        poly.AddGeometry(ring)

        if self.TaskCounter == 0:
            self.LastProjectedPolygon = poly
            self.TaskCounter = 1
        else:
            Area1 = poly.GetArea()
            intersection = self.LastProjectedPolygon.Intersection(poly)
            if intersection:
                result = intersection.GetArea()/Area1
                if result < self.MosaicOverlap:
                    Center = self.RayTrace(LPoint2f(0,0))
                    MU_XYZ = self.RayTrace(MU)
                    MR_XYZ = self.RayTrace(MR)
                    MD_XYZ = self.RayTrace(MD)
                    ML_XYZ = self.RayTrace(ML)
                    PointList = [UL_XYZ,MU_XYZ,UR_XYZ,MR_XYZ,LR_XYZ,MD_XYZ,LL_XYZ,ML_XYZ,Center]
                    OutputFile = self.OutputDir+'Mosaic_'+str(self.MosaicCounter)+'.bmp'
                    ScriptName = str(os.path.dirname(__file__)+'/CreateMosaic.py')
                    command = ('python3 '+ ScriptName+ ' '+self.VideoFile+' '+OutputFile+' '+str(self.StartSecond)+
                        ' '+str(VideoTime)+' '+str(self.VideoWidth)+' '+str(self.VideoHeight)+
                        ' "'+str(PointList)+'" '+str(self.OutEPSG)+' "'+str(self.BoundingBoxStr)+'"')
                    
                    os.system(command)
                    
                    self.MosaicCounter = self.MosaicCounter + 1

                    self.LastProjectedPolygon = poly

        return Task.cont

    def SetupModel(self,VUTProject):
        source = osr.SpatialReference()
        source.ImportFromEPSG(4326)
        target = osr.SpatialReference()
        target.ImportFromEPSG(int(self.OutEPSG))
        transform = osr.CoordinateTransformation(source, target)

        BBxMin = float(self.VRTBoundingBox.split(':')[0].split(',')[0])
        BByMin = float(self.VRTBoundingBox.split(':')[0].split(',')[1])
        BBxMax = float(self.VRTBoundingBox.split(':')[1].split(',')[0])
        BByMax = float(self.VRTBoundingBox.split(':')[1].split(',')[1])

        XLenght = BBxMax - BBxMin
        YLenght = BByMax - BByMin
        NewBBxMax = BBxMax + XLenght/2
        NewBBxMin = BBxMin - XLenght/2
        NewBByMax = BByMax + YLenght / 2
        NewBByMin = BByMin - YLenght / 2

        pointMax = ogr.Geometry(ogr.wkbPoint)
        pointMax.AddPoint(NewBBxMax,NewBByMax)
        pointMax.Transform(transform)

        pointMin = ogr.Geometry(ogr.wkbPoint)
        pointMin.AddPoint(NewBBxMin, NewBByMin)
        pointMin.Transform(transform)

        self.BoundingBoxStr = '-te '+str(pointMin.GetX())+' '+str(pointMin.GetY())+' '+str(pointMax.GetX())+' '+str(pointMax.GetY())+' '

        self.Moves = Sequence()
        Line = LineSegs('Path')
        with open(VUTProject,'r') as File:
            Counter = 0
            i = 0
            PrevCourse = None
            PrevPos = None
            PrevHPr = None
            for line in File:
                if Counter < 6:
                    pass
                else:
                    line = line.split()
                    lat = float(line[0])
                    lon = float(line[1])
                    ele = float(line[2])
                    course = float(line[4])
                    pitch = float(line[5])
                    roll = float(line[6])
                    if course < 180:
                        course = -course
                    elif course > 180:
                        course = abs(course-360)

                    point = ogr.Geometry(ogr.wkbPoint)
                    point.AddPoint(lon, lat)
                    point.Transform(transform)
                    if i == 0:
                        FirstPos = (point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele)
                        FirstHpr = (course, pitch, roll)
                        self.cam.setPos(FirstPos)
                        self.cam.setHpr(FirstHpr)
                        Line.move_to(point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele)
                    elif i == 1:
                        self.Moves.append(LerpPosHprInterval(self.cam, 1, (
                        point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele), (fitDestAngle2Src(PrevCourse,course), pitch, roll),
                                                             startPos=FirstPos, startHpr=FirstHpr,
                                                             name='Interval',other=self.render))
                        Line.draw_to(point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele)
                    else:
                        self.Moves.append(LerpPosHprInterval(self.cam, 1, (
                        point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele), (fitDestAngle2Src(PrevCourse,course), pitch, roll),
                                                             startPos=PrevPos, startHpr=PrevHPr,
                                                             name='Interval',other=self.render))
                        Line.draw_to(point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele)
                    i = i + 1
                    PrevCourse = course
                    PrevPos = (point.GetX() - self.Origin[0], point.GetY() - self.Origin[1], ele)
                    PrevHPr = (course, pitch, roll)
                Counter = Counter + 1
                Line.setColor(1, 0.5, 0.5, 1)
                Line.setThickness(3)
                node = Line.create(False)
                nodePath = self.render.attachNewNode(node)

    def RunModel(self,start,Starttime):
        while time.time() < Starttime:
            pass
        self.Moves.start(startT= start)

    def StopModel(self,stop):
        start = stop-0.001
        self.Moves.start(startT=start,endT=stop)

    def SendReadySignal(self,Directory):
        with open(Directory+'/tmpConnection.txt','w') as output:
            output.write('1')

    def SetupCommunication(self):
        cManager = QueuedConnectionManager()
        cListener = QueuedConnectionListener(cManager, 0)
        cReader = QueuedConnectionReader(cManager, 0)
        self.activeConnections = []  # We'll want to keep track of these later
        port_address = 9098  # No-other TCP/IP services are using this port
        backlog = 1000  # If we ignore 1,000 connection attempts, something is wrong!
        tcpSocket = cManager.openTCPServerRendezvous(port_address, backlog)
        cListener.addConnection(tcpSocket)

        def tskListenerPolling(taskdata):
            if cListener.newConnectionAvailable():

                rendezvous = PointerToConnection()
                netAddress = NetAddress()
                newConnection = PointerToConnection()

                if cListener.getNewConnection(rendezvous, netAddress, newConnection):
                    newConnection = newConnection.p()
                    self.activeConnections.append(newConnection)  # Remember connection
                    cReader.addConnection(newConnection)  # Begin reading connection
            return Task.cont

        def tskReaderPolling(taskdata):
            if cReader.dataAvailable():
                datagram = NetDatagram()  # catch the incoming data in this instance
                # Check the return value; if we were threaded, someone else could have
                # snagged this data before we did
                if cReader.getData(datagram):
                    self.myProcessDataFunction(datagram)
            return Task.cont

        self.taskMgr.add(tskReaderPolling, "Poll the connection reader", -40)
        self.taskMgr.add(tskListenerPolling, "Poll the connection listener", -39)

    def myProcessDataFunction(self,netDatagram):
        myIterator = PyDatagramIterator(netDatagram)
        msgID = myIterator.getUint8()
        messageToPrint = myIterator.getString().split(',')
        #print( messageToPrint)
        if msgID == 1:                                          #start
            Starttime = float((messageToPrint)[0])
            start = float((messageToPrint)[1])
            self.RunModel(start,Starttime)
        if msgID == 2:                              #pause
            Stoptime = float((messageToPrint)[0])
            self.StopModel(Stoptime)
        if msgID == 3:
            sys.exit()
        if msgID == 4:
            self.MosaicOverlap = float((messageToPrint)[1])
            self.ActivateMosaics()
        if msgID == 5:
            pos = float(messageToPrint[0])
            Pixelx = float(messageToPrint[1])
            Pixely = float(messageToPrint[2])
            self.get2DPoint(pos,Pixelx,Pixely)

    def get2DPoint(self,time,Pixelx,Pixely):
        # DO 3d and send data out
        start = time - 0.1
        self.Moves.start(startT=start, endT=time)
        while self.Moves.getT() < time:
            pass

        ScreenPointx = Pixelx / float(self.VideoWidth) * 2 - 1
        ScreenPointy = 1 - (Pixely / float(self.VideoHeight) * 2)
        ScreenPointXY = LPoint2f(ScreenPointx, ScreenPointy)


        UTMPoint = self.RayTrace(ScreenPointXY)
        source = osr.SpatialReference()
        source.ImportFromEPSG(int(self.OutEPSG))
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(source, target)
        Point = ogr.Geometry(ogr.wkbPoint)
        Point.AddPoint(UTMPoint[0], UTMPoint[1])
        Point.Transform(transform)
        with open(self.Directory+'/tmpCoordinate.txt','w') as output:
            output.write(str(Point.GetX())+' '+str(Point.GetY())+' '+str(UTMPoint[2])+' '+str(ScreenPointXY)+'\n')
            output.write('blablabala'*30)

    def ManageDEM(self, DEM):


        def UniformOver16Bit(DN,range,NodataValue,OffsetHeight):
            if DN == NodataValue:
                DN = OffsetHeight

            if OffsetHeight < 0:
                DN = DN + abs(OffsetHeight)
            elif OffsetHeight > 0:
                DN = DN - abs(OffsetHeight)

            value = (DN*65535)/range
            return int(round(value))


        vfunc = numpy.vectorize(UniformOver16Bit)

        ds = gdal.Open(DEM)

        NodataValue = ds.GetRasterBand(1).GetNoDataValue()

        widthRaster = ds.RasterXSize
        heightRaster = ds.RasterYSize
        prj = ds.GetProjection()  # .GetAttrValue("AUTHORITY", 1)
        srs = osr.SpatialReference(wkt=prj)
        self.OutEPSG = srs.GetAttrValue("AUTHORITY", 1)
        gt = ds.GetGeoTransform()
        minx = gt[0]
        miny = gt[3] + widthRaster * gt[4] + heightRaster * gt[5]
        maxx = gt[0] + widthRaster * gt[1] + heightRaster * gt[2]
        maxy = gt[3]

        self.Origin = (minx, miny)


        MeterXScale = (maxx - minx) / widthRaster
        MeterYScale = (maxy - miny) / heightRaster
        self.MeterScale = (MeterXScale + MeterYScale) / 2
        myarray = numpy.array(ds.GetRasterBand(1).ReadAsArray())

        maskedForMinMax = numpy.ma.masked_array(myarray, mask=(myarray==NodataValue))


        self.OffsetHeight = maskedForMinMax.min()
        MaxValue = maskedForMinMax.max()


        TotalRelativeHeight = MaxValue - self.OffsetHeight


        self.HeightRange =  TotalRelativeHeight         #MaxValue

        ds = None

        arrayH = myarray.shape[0]
        arrayW = myarray.shape[1]
        MaxValue = (max(arrayH, arrayW))

        ExpandTo = (1 << (MaxValue - 1).bit_length())
        self.PixelNr = ExpandTo
        ExpandH = ExpandTo - arrayH
        ExpandW = ExpandTo - arrayW
        ExpandHArray = numpy.full((ExpandH, arrayW), self.OffsetHeight)
        tmpArray = numpy.vstack((ExpandHArray, myarray))
        ExpandWArray = numpy.full((ExpandTo, ExpandW), self.OffsetHeight)
        FinalArray = numpy.hstack((tmpArray, ExpandWArray))

        xxx = vfunc(FinalArray,self.HeightRange, NodataValue,self.OffsetHeight)

        self.PngDEM = DEM.split('.')[0] + '_tmp_.png'
        with open(self.PngDEM, 'wb') as f:
            writer = png.Writer(width=FinalArray.shape[1], height=FinalArray.shape[0], bitdepth=16, greyscale=True,
                                alpha=False)
            list = xxx.tolist()
            writer.write(f, list)

    def SetupTexture(self,Texture):

        ds = gdal.Open(Texture)
        ulx = self.Origin[0]
        uly = self.Origin[1] + (self.PixelNr * self.MeterScale)
        lrx = self.Origin[0] + (self.PixelNr * self.MeterScale)
        lry = self.Origin[1]
        projwin = [ulx, uly, lrx, lry]

        self.TextureImage = Texture.split('.')[0]+'_tmp.png'
        ds = gdal.Translate(self.TextureImage, ds, projWin=projwin, format='PNG')

        ds = None

    def SetupVisibleTerrain(self):

        self.terrain_node = ShaderTerrainMesh()

        self.terrain_node.heightfield = self.loader.loadTexture(self.PngDEM)

        self.terrain_node.target_triangle_width = 100.0

        self.terrain_node.generate()


        self.terrain = self.render.attach_new_node(self.terrain_node)


        self.terrain.set_scale(self.PixelNr * self.MeterScale, self.PixelNr * self.MeterScale,
                               self.HeightRange)

        terrain_shader = Shader.load(Shader.SL_GLSL, "terrain.vert.glsl", "terrain.frag.glsl")
        self.terrain.set_shader(terrain_shader)
        self.terrain.set_shader_input("camera", self.camera)

        grass_tex = self.loader.loadTexture(self.TextureImage)
        grass_tex.set_anisotropic_degree(16)



        self.terrain.set_texture(grass_tex)

        self.terrain.setPos(0,0, self.OffsetHeight)

    def SetupBulletTerrain(self):
        self.worldNP = self.render.attachNewNode('World')
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        img = PNMImage(Filename(self.PngDEM))
        if self.MeterScale < 1.1:
            shape = BulletHeightfieldShape(img, self.HeightRange , ZUp)
        else:
            shape = BulletHeightfieldShape(img, self.HeightRange , ZUp)

        shape.setUseDiamondSubdivision(True)

        np = self.worldNP.attachNewNode(BulletRigidBodyNode('Heightfield'))
        np.node().addShape(shape)

        offset = self.MeterScale * self.PixelNr / 2.0
        np.setPos(+ offset, + offset, + (self.HeightRange  / 2.0) + self.OffsetHeight)

        np.setSx(self.MeterScale)
        np.setSy(self.MeterScale)
        np.setCollideMask(BitMask32.allOn())

        self.world.attachRigidBody(np.node())

    def EraseTmpFiles(self):
        os.remove(self.TextureImage)
        os.remove(self.PngDEM)

        
        
Video_UAV_Tracker_3D(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10],sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14],sys.argv[15]).run()

