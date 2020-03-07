import numpy as np
import cv2
import math

class Shape(object):
    def __init__(self):
        pass

    def getBoundingPoints(self):
        return []

    def paintShape(self, img, pos, scale, color, thickness = None, linetype = None):
        pass

class Round(Shape):
    def __init__(self, radius = 1.0):
        self.radius = radius

    def getBoundingPoints(self):
        return [np.array([ self.radius,  self.radius, 1], np.float32), np.array([-self.radius,  self.radius, 1], np.float32),
                    np.array([ self.radius, -self.radius, 1], np.float32), np.array([-self.radius, -self.radius, 1], np.float32)]

    def paintShape(self, img, pos, scale, color, thickness = 1, linetype = cv2.LINE_8):
        cv2.circle(img, pos.getScaledPos(scale), int(self.radius*pos.scale*scale), color, thickness, linetype)

class Rectangle(Shape):
    def __init__(self, width = 1.0, height = 1.0):
        self.width = width
        self.height = height

    def getBoundingPoints(self):
        return [np.array([ self.width/2,  self.height/2, 1], np.float32), np.array([-self.width/2,  self.height/2, 1], np.float32),
                    np.array([-self.width/2, -self.height/2, 1], np.float32), np.array([ self.width/2, -self.height/2, 1], np.float32)]

    def paintShape(self, img, pos, scale, color, thickness = 1, linetype = cv2.LINE_8):
        pts = self.getBoundingPoints()
        ptarr = np.array(pos.shiftPoints(pts, scale))
        ## Rotate, translate and scale the edge points
        #rotmat = cv2.getRotationMatrix2D((0, 0), -math.degrees(pos.rotRad), pos.scale*scale)
        #rotmat[:,2] += pos.getScaledPos(scale)
        #pts = np.array([ np.matmul(rotmat, np.append(pt, 1.0)) for pt in pts])
        pv = ptarr.astype(np.int32)
        pvr = pv.reshape((-1, 1, 2))

        if thickness is not None and thickness > 0:
            cv2.polylines(img, [pvr], True, color, thickness, linetype)
        else:
            cv2.fillConvexPoly(img, pvr, color, linetype)

# Factory and list for UI

shapeList = [
    "round",
    "rectangle"
]

class ShapeFactory(object):
    @staticmethod
    def buildShape(ind):
        if ind == 0:
            return Round()
        elif ind == 1:
            return Rectangle()
        else:
            return None
    
    @staticmethod
    def searchShape(enc):
        if isinstance(enc, Round):
            return 0
        elif isinstance(enc, Rectangle):
            return 1
        else:
            return -1
