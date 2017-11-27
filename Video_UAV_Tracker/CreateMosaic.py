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
import ast

def CreateMosaic(VideoFile,OutputFile,Startmseconds,VideoTime,VideoWidth,VideoHeight,PointList,OutEPSG,BoundingBoxString):
        
        Startmseconds = float(Startmseconds)
        VideoTime = float(VideoTime)
        VideoWidth = int(float(VideoWidth))
        VideoHeight = int(float(VideoHeight))
        PointList = ast.literal_eval(PointList)
        OutEPSG = int(OutEPSG)
        
        FrameSecond = VideoTime   + Startmseconds
        if os.name == 'nt':
            ffmpeg = ('"'+os.path.dirname(__file__)[0:-18]+'/Video_UAV_Tracker/FFMPEG/ffmpeg.exe'+'"')
            a = os.popen(ffmpeg + ' -hide_banner -loglevel quiet -ss ' + str(FrameSecond) + ' -i "' + str(
                VideoFile) + '" -t 1 "' + str(OutputFile) + '"')
        else:
            ffmpeg = os.path.dirname(__file__) + '/FFMPEG/./ffmpeg'
            a = os.system( ffmpeg+' -hide_banner -loglevel quiet -ss '+str(FrameSecond)+' -i "'+str(VideoFile)+'" -t 1 "'+str(OutputFile)+'"')

        UL_pixel = (0.1*VideoWidth/2, 0.1*VideoHeight/2)
        MU_pixel = (VideoWidth/2, 0.1*VideoHeight/2)
        UR_pixel = (1.9*VideoWidth/2, 0.1*VideoHeight/2)
        MR_pixel = (1.9*VideoWidth/2, VideoHeight/2)
        LR_pixel = (1.9*VideoWidth/2, 1.9*VideoHeight/2 )
        MD_pixel = (VideoWidth/2, 1.9*VideoHeight/2)
        LL_pixel = (0.1*VideoWidth/2, 1.9*VideoHeight/2)
        ML_pixel = (0.1*VideoWidth/2, VideoHeight/2)
        Center_pixel = (VideoWidth/2, VideoHeight/2)
        vrtFile = OutputFile.split('.')[0]+'_tmp.vrt'
        tifFile = OutputFile.split('.')[0]+'.tif'
        a = os.system('gdal_translate -quiet -a_srs EPSG:'+str(OutEPSG)+' -gcp '+str(UL_pixel[0])+' '+str(UL_pixel[1])+' '+str(PointList[0][0])+' '+str(PointList[0][1])+' '+str(PointList[0][2])
                                                        +' -gcp '+str(MU_pixel[0])+' '+str(MU_pixel[1])+' '+str(PointList[1][0])+' '+str(PointList[1][1])+' '+str(PointList[1][2])
                                                        +' -gcp '+str(UR_pixel[0])+' '+str(UR_pixel[1])+' '+str(PointList[2][0])+' '+str(PointList[2][1])+' '+str(PointList[2][2])
                                                        +' -gcp '+str(MR_pixel[0])+' '+str(MR_pixel[1])+' '+str(PointList[3][0])+' '+str(PointList[3][1])+' '+str(PointList[3][2])
                                                        +' -gcp '+str(LR_pixel[0])+' '+str(LR_pixel[1])+' '+str(PointList[4][0])+' '+str(PointList[4][1])+' '+str(PointList[4][2])
                                                        +' -gcp '+str(MD_pixel[0])+' '+str(MD_pixel[1])+' '+str(PointList[5][0])+' '+str(PointList[5][1])+' '+str(PointList[5][2])
                                                        +' -gcp '+str(LL_pixel[0])+' '+str(LL_pixel[1])+' '+str(PointList[6][0])+' '+str(PointList[6][1])+' '+str(PointList[6][2])
                                                        +' -gcp '+str(ML_pixel[0])+' '+str(ML_pixel[1])+' '+str(PointList[7][0])+' '+str(PointList[7][1])+' '+str(PointList[7][2])
                                                        +' -gcp '+str(Center_pixel[0])+' '+str(Center_pixel[1])+' '+str(PointList[8][0])+' '+str(PointList[8][1])+' '+str(PointList[8][2])
                                                        +' -of VRT '+str(OutputFile)+' '+str(vrtFile)    )


        a = os.system('gdalwarp -quiet -order 2 -dstalpha -overwrite -t_srs EPSG:'+str(OutEPSG)+' '+str(vrtFile)+' '+str(tifFile))
        os.remove(vrtFile)
        os.remove(OutputFile)
        Dir = VideoFile.split('.')[0] + '_Mosaic/'
        a = os.system('gdalbuildvrt '+BoundingBoxString+' -overwrite -srcnodata "0 0 0 0" ' + Dir + str(VideoFile.split('.')[0].split('/')[-1])+'_Video_Mosaic.vrt ' + Dir + '*.tif')
CreateMosaic(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9])
