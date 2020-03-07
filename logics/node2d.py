from logics.encoder import *
import logics.shape

from logics.property import Property

import threading

import copy
import numpy as np
import math
import cv2

class Pos2D(object):
    def __init__(self):
        self.posX = 0.0
        self.posY = 0.0
        self.scale = 1.0
        self.rotRad = 0.0
        self.lockScale = False

        self.evalOffset = None
    
    def __str__(self):
        return f'({self.posX}, {self.posY}) x{self.scale}{"!" if self.lockScale else ""} r{self.rotRad}'

    def __repr__(self):
        return 'Pos2d' + self.__str__()

    def getScaledPos(self, scale = 1.0, base = (0, 0)):
        px = int(self.posX * scale + base[0])
        py = int(self.posY * scale + base[1])
        if self.evalOffset:
            px -= self.evalOffset[0]
            py -= self.evalOffset[1]
        return px, py

    def updateCopy(self, base):
        self.posX = base.posX
        self.posY = base.posY
        self.scale = base.scale
        self.rotRad = base.rotRad
        self.lockScale = base.lockScale
        
    def updateShift(self, base, offset):
        offlen = math.sqrt(offset.posX ** 2 + offset.posY ** 2)
        offrad = math.atan2(offset.posY, offset.posX)
        offrad += base.rotRad
        
        self.posX = base.posX + base.scale * offlen * math.cos(offrad)
        self.posY = base.posY + base.scale * offlen * math.sin(offrad)
        self.scale = 1.0 if offset.lockScale else base.scale * offset.scale
        self.rotRad = base.rotRad + offset.rotRad

    def getAbsDifference(self, rhs):
        res = Pos2D()
        # Buggy, require vector angle in consideration
        diffx = self.posX - rhs.posX
        diffy = self.posY - rhs.posY
        
        offlen = math.sqrt(diffx ** 2 + diffy ** 2)
        offrad = math.atan2(diffy, diffx)
        offrad -= rhs.rotRad

        res.posX = offlen * math.cos(offrad)
        res.posY = offlen * math.sin(offrad)
        res.scale = self.scale / rhs.scale
        res.rotRad = self.rotRad - rhs.rotRad
        return res
    
    def shiftPoints(self, pts, scale):
        # Rotate, translate and scale points
        rotmat = np.float32(cv2.getRotationMatrix2D((0, 0), -math.degrees(self.rotRad), self.scale*scale))
        rotmat[:,2] +=  np.float32(self.getScaledPos(scale))
        return [np.dot(rotmat, pt) for pt in pts]
    
    def setOffset(self, offset):
        self.evalOffset = offset

class TreeNode(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.child = []
        
        self.name = "TreeNode"

        if parent:
            parent.child.append(self)

    def iterChilds(self, func):
        func(self)
        for ch in self.child:
            ch.iterChilds(func)

class PosTreeNode2D(TreeNode):
    def __init__(self, parent = None):
        TreeNode.__init__(self, parent)
       
        self.name = "PosTreeNode2D"

        self.offPos = Pos2D()
        self.absPos = Pos2D()

    def evalPos(self):
        if self.parent:
            self.absPos.updateShift(self.parent.absPos, self.offPos)
        else:
            self.absPos.updateCopy(self.offPos)
        
        for ch in self.child:
            ch.evalPos()

    def copyPosTree(self, parent = None):
        nnode = PosTreeNode2D(parent)
        nnode.offPos = copy.copy(self.offPos)
        for ch in self.child:
            ch.copyPosTree(nnode)
        return nnode

class TreeNode2D(PosTreeNode2D):
    def __init__(self, parent = None):
        PosTreeNode2D.__init__(self, parent)

        self.name = "TreeNode2D"

        self.property = {}
        self.property['offPos'] = Property("Pos2D", "Position")

    def attachProperty(self, name, value, property):
        setattr(self, name, value)
        self.property[name] = property

    def detatchProperty(self, name):
        setattr(self, name, None)
        self.property.pop(name)


class SamplePoint(TreeNode2D):
    def __init__(self, parent = None):
        TreeNode2D.__init__(self, parent)
        
        self.name = "SamplePoint"

        self.property['encoder'] = Property('Encoder', 'Encoder')
        self.property['sampleShape'] = Property('Shape', 'Sampling Shape')

        self.encoder = BinaryEncoder()
        self.sampledValue = None
        
        self.sampleShape = logics.shape.Round()

    def copyPosTree(self, parent = None):
        nnode = SamplePoint(parent)
        nnode.offPos = copy.copy(self.offPos)
        nnode.sampledValue = self.sampledValue
        nnode.sampleShape = self.sampleShape

        for ch in self.child:
            ch.copyPosTree(nnode)

class SamplePlane(TreeNode2D):
    def __init__(self, parent = None):
        TreeNode2D.__init__(self, parent)
        
        self.name = "SamplePlane"
        
        self.property['encoder'] = Property('Encoder', 'Encoder')
        self.property['pixelWidth'] = Property('Int', 'Pixel Width')
        self.property['pixelHeight'] = Property('Int', 'Pixel Height')
        self.property['sampleShape'] = Property('Shape', 'Sampling Shape')

        self.encoder = BinaryEncoder()
        self.sampledImage = None
        
        self.pixelWidth  = 320
        self.pixelHeight = 240
        
        self.sampleShape = logics.shape.Rectangle(32, 24)
        
    def copyPosTree(self, parent = None):
        nnode = SamplePlane(parent)
        nnode.offPos = copy.copy(self.offPos)
        nnode.pixelWidth = self.pixelWidth
        nnode.pixelHeight = self.pixelHeight
        nnode.sampledImage = self.sampledValue
        nnode.sampleShape = self.sampleShape

        for ch in self.child:
            ch.copyPosTree(nnode)

class Image(TreeNode2D):
    def __init__(self, parent = None):
        TreeNode2D.__init__(self, parent)

        self.name = "Image"

        self.property['file'] = Property('ImageFile', 'Image')
        self.property['widthScale'] = Property('Real', 'Width Scale')

        self.file = ""
        self.image = None

        self.imageSize = [0, 0]
        self.widthScale = 1.0

    def copyPosTree(self, parent = None):
        nnode = Image(parent)
        nnode.offPos = copy.copy(self.offPos)
        nnode.image = self.image

        for ch in self.child:
            ch.copyPosTree(nnode)

class Video(TreeNode2D):
    def __init__(self, parent = None):
        TreeNode2D.__init__(self, parent)

        self.name = "Video"

        self.property['file'] = Property('VideoFile', 'Video')
        self.property['startFrame'] = Property('Int', 'Start Frame')
        self.property['widthScale'] = Property('Real', 'Width Scale')

        self.file = ""
        self.videocap = None
        self.fetcher = None

        self.frameSize = [0, 0]
        self.widthScale = 1.0

        self.overrunMode = "repeat"
        self.startFrame = 0
        self.frameLength = 0

    def loadVideo(self):
        self.videocap = cv2.VideoCapture(self.file)
        self.frameLength = int(self.videocap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameSize[0] = int(self.videocap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frameSize[1] = int(self.videocap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def getMappedFrame(self, frame):
        if self.overrunMode == "none":
            if frame < self.startFrame or frame >= self.startframe + self.frameLength:
                return None
            else:
                frame -= self.startFrame
        elif self.overrunMode == "hold":
            if frame < self.startFrame:
                frame = self.startFrame
            if frame >= self.startFrame + self.frameLength:
                frame = self.startFrame + self.frameLength - 1
        elif self.overrunMode == "repeat":
            frame = (frame - self.startFrame) % self.frameLength
        return frame

    def fetchFrame(self, frame):
        nframe = self.getMappedFrame(frame)
        if nframe is None:
            return None

        self.videocap.set(cv2.CAP_PROP_POS_FRAMES, nframe)
        retval, rim = self.videocap.read()

        return rim

    def setupThreading(self, numthread):
        self.fetcher = ThreadedFetcher(self.getMappedFrame, self.file, numthread)

    def copyPosTree(self, parent = None):
        nnode = ThreadedVideo(parent)
        nnode.offPos = copy.copy(self.offPos)
        nnode.videocap = self.videocap
        nnode.fetcher = self.fetcher
        nnode.frameSize = self.frameSize
        nnode.overrunMode = self.overrunMode
        nnode.startFrame = self.startFrame
        nnode.frameLength = self.frameLength

        for ch in self.child:
            ch.copyPosTree(nnode)

class ThreadedFetcher(object):
    def __init__(self, getMappedFrame, file, numthread=1):
        self.getMappedFrame = getMappedFrame
        self.file = file
        self.eventDict = {}
        self.updateEvent = threading.Event()
        self.dictLock = threading.Lock()
        self.numthread = numthread

    def threadWorker(self, startframe, endframe):
        videocap = cv2.VideoCapture(self.file)
        lframe = -1
        limg = None

        for frame in range(startframe, endframe):
            # Fetch next frame
            nframe = self.getMappedFrame(frame)
            if nframe == lframe+1:
                retval, nimg = videocap.read()
            elif nframe == lframe:
                nimg = limg
            else:
                videocap.set(cv2.CAP_PROP_POS_FRAMES, nframe)
                retval, nimg = videocap.read()

            lframe = nframe
            limg = nimg

            # Push frame into dict
            with self.dictLock:
                if frame in self.eventDict:
                    # Renderer waiting with a event
                    self.eventDict[frame][1] = nimg
                    self.eventDict[frame][0].set()
                else:
                    self.eventDict[frame] = [None, nimg]

            if len(self.eventDict) > self.numthread:
                self.updateEvent.clear()
                self.updateEvent.wait()

        videocap.release()

    def fetchFrame(self, frame):
        # Check event dict
        with self.dictLock:
            if frame in self.eventDict:
                # Frame already in queue
                res = self.eventDict[frame][1]
                event = None
                self.eventDict.pop(frame)
            else:
                # Set a event to wait for frame
                event = threading.Event()
                self.eventDict[frame] = [event, None]
        if event:
            event.wait()
            res = self.eventDict[frame][1]
            self.eventDict.pop(frame)
        self.updateEvent.set()
        return res

class ThreadedVideo(Video):
    def __init__(self, parent = None):
        Video.__init__(self, parent)
        
    def fetchFrame(self, frame):
        if self.fetcher:
            return self.fetcher.fetchFrame(frame)
        else:
            return Video.fetchFrame(self, frame)