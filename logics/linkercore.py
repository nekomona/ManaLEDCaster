from logics.property import *
from logics.encoder import SampledValue

mergeTypes = [
    "Append",
    "Concat",
    "BitMerge",
    "UpperAppend"
    ]

lcnt = 0

class DisplayChain(object):
    def __init__(self, parent = None):
        self.nodes = []
        self.attachedNode = None
        self.mergeType = "Append"
        self.reverse = False
        if parent:
            parent.nodes.append(self)

    def attachTreeNode(self, tree):
        tree.attachProperty("linker", self, Property("DisplayChain", "Linker"))
        tree.displayChain = self
        self.attachedNode = tree

    def readChain(self):
        global lcnt
        localResult = []
        lowerAppend = False

        for n in self.nodes:
            if isinstance(n, DisplayChain):
                localResult.append(n.readChain())
                if n.mergeType == "UpperAppend":
                    lowerAppend = True
                else:
                    if lowerAppend:
                        raise Exception("UpperAppend chain requires uniform type of element")
            else:
                localResult.append(SampledValue(16, lcnt))
                lcnt += 1

        if self.reverse:
            localResult.reverse()
        
        if lowerAppend:
            localResult = list(map(list, zip(*localResult)))

        if self.mergeType == "Concat":
            localResult = sum(localResult, [])
        elif self.mergeType == "BitMerge":
            localResult = sum(localResult, SampledValue())

        return localResult

class PixelFetcher(object):
    def __init__(self):
        self.source = None
    
    def fetch(self):
        return None

class PointPixelFetcher(PixelFetcher):
    def __init__(self, pixel):
        self.source = pixel
    
    def fetch(self):
        return self.source.value

class PlanePixelFetcher(PixelFetcher):
    def __init__(self, plane, px, py):
        self.source = plane
        self.px = px
        self.py = py
     
    def fetch(self):
        return self.source.image[self.px][self.py]