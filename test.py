from logics.node2d import *
from logics.linkercore import DisplayChain
import logics.shape

pbase = TreeNode2D()

pim = Image(pbase)
pim.image = cv2.imread('iconode.png')

pvid = Video(pbase)
pvid.file = "ba.flv"
pvid.loadVideo()

lbase = DisplayChain()
lbase.attachTreeNode(pbase)

# Rectangular LED array

parr = TreeNode2D(pbase)
parr.offPos.posX = 40
parr.offPos.posY = 40

larr = DisplayChain(lbase)
larr.mergeType = "UpperAppend"
larr.attachTreeNode(parr)

for y in range(8):
    pline = TreeNode2D(parr)
    pline.offPos.posX = 2 - 16
    pline.offPos.posY = 2 - 16 + y * 4
    pline.name = "Line" + str(y)
    
    lline = DisplayChain(larr)
    lline.mergeType = "BitMerge"
    lline.attachTreeNode(pline)
    for x in range(8):
        pnt = SamplePoint(pline)
        pnt.name += str(y) + str(x)
        pnt.offPos.posX = x*4
        pnt.sampleShape = logics.shape.Rectangle(3, 3)
        lline.nodes.append(pnt)

# Round LED array

for i in range(1):
    for j in range(1):
        parr = TreeNode2D(pbase)
        parr.offPos.posX = 80 + 32*i
        parr.offPos.posY = 40 + 32*j

        larr = DisplayChain(lbase)
        larr.mergeType = "UpperAppend"
        larr.attachTreeNode(parr)

        for y in range(8):
            pline = TreeNode2D(parr)
            pline.offPos.posX = 2 - 16
            pline.offPos.posY = 2 - 16 + y * 4
            pline.name = "Line" + str(y)
    
            lline = DisplayChain(larr)
            lline.mergeType = "BitMerge"
            lline.attachTreeNode(pline)
            for x in range(8):
                pnt = SamplePoint(pline)
                pnt.name += str(y) + str(x)
                pnt.offPos.posX = x*4
                pnt.sampleShape.radius = 1.5
                lline.nodes.append(pnt)

pbase.evalPos()

from main import LSWindow
from PyQt5 import QtWidgets
import sys

if __name__ == '__main__': 
    app = QtWidgets.QApplication(sys.argv) 

    window = LSWindow()
    window.setTreeBase(pbase)
    window.setLinkerBase(lbase)
    window.show() 
    # window=myform() #如果是QWidget 
    #windows.show() 
    #app.exec_() 
    try:
        sys.exit(app.exec()) 
    except:
        pass


