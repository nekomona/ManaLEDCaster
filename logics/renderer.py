from logics.node2d import *
from logics.timedValue import TimedDiscreteValue
import logics.impainter as impainter

import threading
import queue
import time

import numpy as np
import cv2

wcnt = 0

def resetTimedValuesFrameLimit(pbase):
    if isinstance(pbase, SamplePoint) or isinstance(pbase, SamplePlane):
        if pbase.sampledValue:
            pbase.sampledValue.resetFrameLimit()
        else:
            pbase.sampledValue = TimedDiscreteValue()

    for ch in pbase.child:
        resetTimedValuesFrameLimit(ch)

class ThreadedRenderer(object):
    def __init__(self, tcount = 1):
        self.tcount = tcount
        self.rqueue = queue.Queue()
        self.videos = []
        
    def updateVideoWorker(self, node):
        if isinstance(node, Video):
            self.videos.append(node)

    def render(self, framestart, frameend, scale, pbase):
        self.scale = scale
        self.pbase = pbase
        
        self.videos.clear()
        self.pbase.iterChilds(self.updateVideoWorker)

        for i in range(framestart, frameend):
            self.rqueue.put(i)

        threads = []
        # Rendering threads
        for i in range(self.tcount):
            threads.append(RenderThread(i, self.rqueue, scale, pbase))
        # Video threads
        for i, v in enumerate(self.videos):
            v.setupThreading(self.tcount)
            threads.append(VideoThread(i, v.fetcher, framestart, frameend))

        for thr in threads:
            thr.start()
           
        self.rqueue.join()

        for v in self.videos:
            v.fetcher = None

class VideoThread(threading.Thread):
    def __init__(self, threadid, fetcher, framestart, frameend):
        threading.Thread.__init__(self)
        self.id = threadid
        self.fetcher = fetcher
        self.startframe = framestart
        self.endframe = frameend

    def run(self):
        self.fetcher.threadWorker(self.startframe, self.endframe)

class RenderThread(threading.Thread):
    def __init__(self, threadId, frameque, scale, pbase):
        threading.Thread.__init__(self)
        self.id = threadId
        self.que = frameque
        self.scale = scale
        self.pbase = pbase

    def run(self):
        print("Thread", self.id, "ready")
        while not self.que.empty():
            try:
                t0 = time.clock()
                frame = self.que.get()
                rnd = RenderWorker(frame, self.scale, self.pbase.copyPosTree())
                rnd.renderRun()
                t1 = time.clock()
                print("Thread", self.id, "processed frame", frame, "with", t1-t0)
                self.que.task_done()
            except:
                break
        print("Thread", self.id, "exit")

class RenderWorker(object):
    def __init__(self, frame, scale, pbase):
        self.pointRenderArea = [0, 0, 0, 0]
        self.frame = frame
        self.drawBuff = None
        self.offset = (0, 0)

        self.pointSamplers = []
        self.planeSamplers = []

        self.scale = scale
        self.pbase = pbase
    
    def updateSamplersWorker(self, node):
        if isinstance(node, SamplePoint):
            self.pointSamplers.append(node)
        elif isinstance(node, SamplePlane):
            self.planeSamplers.append(node)

    def updateSamplers(self):
        self.pointSamplers.clear()
        self.planeSamplers.clear()
        self.pbase.iterChilds(self.updateSamplersWorker)

    def updateRenderArea(self):
        edgel, edger = None, None
        edgeu, edged = None, None
        for pnt in self.pointSamplers:
            newEdgePoints = pnt.absPos.shiftPoints(pnt.sampleShape.getBoundingPoints(), self.scale)
            for epnt in newEdgePoints:
                if edgel is None or epnt[0] < edgel:
                    edgel = epnt[0]
                if edger is None or edger < epnt[0]:
                    edger = epnt[0]
                if edgeu is None or epnt[1] < edgeu:
                    edgeu = epnt[1]
                if edged is None or edged < epnt[1]:
                    edged = epnt[1]
        self.pointRenderArea = [int(edgel), int(edgeu), int(edger - edgel), int(edged - edgeu)]

        self.drawBuff = np.full((self.pointRenderArea[3], self.pointRenderArea[2], 3), (255, 255, 255), np.uint8)
        self.offset = (self.pointRenderArea[0], self.pointRenderArea[1])

    def renderPointArea(self):
        self.pbase.iterChilds(lambda node: node.absPos.setOffset(self.offset))
        impainter.paintImageTree(self.drawBuff, self.scale, self.pbase, self.frame)

    def renderPointSampler(self):
        for pnt in self.pointSamplers:
            samplemask = np.zeros(self.drawBuff.shape[:2], dtype=np.uint8)
            pnt.sampleShape.paintShape(samplemask, pnt.absPos, self.scale, 255, -1)
            
            samppnts = np.where(samplemask != 0)
            sampvals = self.drawBuff[samppnts[0], samppnts[1]]
            avgval = [int(i) for i in np.mean(sampvals, 0)]
            if pnt.sampledValue:
                pnt.sampledValue.setValue(self.frame, avgval)
            
    def renderRun(self):
        self.updateSamplers()
        self.pbase.evalPos()
        self.updateRenderArea()
        self.renderPointArea()
        self.renderPointSampler()

class FixedPosRenderer(object):
    def __init__(self, tcount=1):
        self.pointRenderArea = [0, 0, 0, 0]
        self.offset = (0, 0)

        self.tcount = tcount
        self.rqueue = queue.Queue()
        self.videos = []

        self.pointSamplers = []
        self.pointSamplerAreas = []
        self.planeSamplers = []

        self.scale = 1.0
        self.pbase = None

    def updateSamplersAndVideosWorker(self, node):
        if isinstance(node, Video):
            self.videos.append(node)
        if isinstance(node, SamplePoint):
            self.pointSamplers.append(node)
        elif isinstance(node, SamplePlane):
            self.planeSamplers.append(node)

    def updateSamplersAndVideos(self):
        self.videos.clear()
        self.pointSamplers.clear()
        self.planeSamplers.clear()
        self.pbase.iterChilds(self.updateSamplersAndVideosWorker)

    def updateRenderArea(self):
        edgel, edger = None, None
        edgeu, edged = None, None
        for pnt in self.pointSamplers:
            newEdgePoints = pnt.absPos.shiftPoints(pnt.sampleShape.getBoundingPoints(), self.scale)
            for epnt in newEdgePoints:
                if edgel is None or epnt[0] < edgel:
                    edgel = epnt[0]
                if edger is None or edger < epnt[0]:
                    edger = epnt[0]
                if edgeu is None or epnt[1] < edgeu:
                    edgeu = epnt[1]
                if edged is None or edged < epnt[1]:
                    edged = epnt[1]
        self.pointRenderArea = [int(edgel), int(edgeu), int(edger - edgel), int(edged - edgeu)]

        self.offset = (self.pointRenderArea[0], self.pointRenderArea[1])

        self.pointSamplerAreas.clear()
        for pnt in self.pointSamplers:
            samplemask = np.zeros((self.pointRenderArea[3], self.pointRenderArea[2]), dtype=np.uint8)
            pnt.absPos.setOffset(self.offset)
            pnt.sampleShape.paintShape(samplemask, pnt.absPos, self.scale, 255, -1)
            pnt.absPos.setOffset(None)
            
            self.pointSamplerAreas.append(np.where(samplemask != 0))

    def render(self, framestart, frameend, scale, pbase):
        self.scale = scale
        self.pbase = pbase
        
        self.updateSamplersAndVideos()
        self.pbase.evalPos()
        self.updateRenderArea()

        for i in range(framestart, frameend):
            self.rqueue.put(i)

        threads = []
        # Rendering threads
        for i in range(self.tcount):
            threads.append(FixedPosRenderThread(i, self.rqueue, self, pbase))
        # Video threads
        for i, v in enumerate(self.videos):
            v.setupThreading(self.tcount)
            threads.append(VideoThread(i, v.fetcher, framestart, frameend))

        for thr in threads:
            thr.start()
           
        self.rqueue.join()

        for v in self.videos:
            v.fetcher = None

class FixedPosRenderThread(threading.Thread):
    def __init__(self, threadId, frameque, fprenderer, pbase):
        threading.Thread.__init__(self)
        self.id = threadId
        self.que = frameque
        self.pbase = pbase
        self.fprenderer = fprenderer

    def run(self):
        print("Thread", self.id, "ready")
        while not self.que.empty():
            try:
                t0 = time.clock()
                frame = self.que.get()
                rnd = FixedPosRenderWorker(frame, self.fprenderer, self.pbase.copyPosTree())
                rnd.renderRun()
                t1 = time.clock()
                print("Thread", self.id, "processed frame", frame, "with", t1-t0)
                self.que.task_done()
            except:
                break
        print("Thread", self.id, "exit")

class FixedPosRenderWorker(object):
    def __init__(self, frame, fprenderer, pbase):
        self.frame = frame
        self.drawBuff = np.full((fprenderer.pointRenderArea[3], fprenderer.pointRenderArea[2], 3), (255, 255, 255), np.uint8)
        self.offset = fprenderer.offset

        self.pointSamplers = fprenderer.pointSamplers
        self.pointSamplerAreas = fprenderer.pointSamplerAreas
        self.planeSamplers = fprenderer.planeSamplers

        self.scale = fprenderer.scale
        self.pbase = pbase
    
    def renderPointArea(self):
        self.pbase.evalPos()
        self.pbase.iterChilds(lambda node: node.absPos.setOffset(self.offset))
        impainter.paintImageTree(self.drawBuff, self.scale, self.pbase, self.frame)

    def renderPointSampler(self):
        for i, pnt in enumerate(self.pointSamplers):
            samppnts = self.pointSamplerAreas[i]
            sampvals = self.drawBuff[samppnts[0], samppnts[1]]
            avgval = [int(i) for i in (sampvals.sum(0) / sampvals.shape[0])]
            if pnt.sampledValue:
                pnt.sampledValue.setValue(self.frame, avgval)

    def renderRun(self):
        self.renderPointArea()
        self.renderPointSampler()