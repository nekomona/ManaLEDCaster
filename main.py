import globals

from logics.property import PropertyContainer
import logics.linkercore
import properties.propertyEditor as propertyEditor

import logics.impainter as impainter
import logics.renderer as renderer

from PyQt5 import QtGui, QtWidgets, QtCore 
from ledsampler import Ui_MainWindow

import sys
import time
import numpy as np
import cv2

def buildQtTree(root, tree):
    cpt = QtWidgets.QTreeWidgetItem(root)
    cpt.setText(0, tree.name)
    cpt.setText(1, str(type(tree)))
    cpt.node = tree

    for ch in tree.child:
        buildQtTree(cpt, ch)

def updateQtTreeName(root):
    root.setText(0, root.node.name)
    chcnt = root.childCount()
    for i in range(chcnt):
        ch = root.child(i)
        updateQtTreeName(ch)

def buildQtLinkerTree(root, tree):
    cpt = QtWidgets.QTreeWidgetItem(root)

    if isinstance(tree, logics.linkercore.DisplayChain):
        cpt.setText(0, tree.attachedNode.name)
        
        for ch in tree.nodes:
            buildQtLinkerTree(cpt, ch)
    else:
        cpt.setText(0, tree.name)

    cpt.setText(1, str(type(tree)))
    cpt.node = tree

def clearLayout(layout : QtWidgets.QLayout):
    if layout is None:
        return
    for i in reversed(range(layout.count())):
        item = layout.takeAt(i)
        if item.widget() is not None:
            item.widget().deleteLater()
        else:
            clearLayout(item.layout())

        
def cvMatToQimg(mat):#将opencv格式的文件转化为pyqt5的文件格式 
    mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    h, w, ch = mat.shape
    qimg = QtGui.QImage(mat.tostring(), w, h, ch * w, QtGui.QImage.Format_RGB888)
    # qimg = QtGui.QImage(mat.data, w, h, ch * w, QtGui.QImage.Format_RGB888).rgbSwapped()
    return qimg

class LSWindow(QtWidgets.QMainWindow, Ui_MainWindow): 
    # 建立的是Main Window项目，故此处导入的是QMainWindow 
    # class myform(QWidget,Ui_Form):如建立的是Widget项目，导入的是QWidget 
    def __init__(self): 
        super(LSWindow, self).__init__() 
        self.setupUi(self)

        self.scale = 5
        self.frame = 0

        self.oldResizeEvent = self.resizeEvent
        self.resizeEvent = self.onResize

        globals.rebuildTree = self.buildTree
        globals.rebuildProperty = lambda : self.buildProperty(globals.propertyContainer.activeNode)
        globals.repaintScreen = self.paintScreen
        globals.propertyContainer = PropertyContainer()

        self.pbase = None
        self.lbase = None
        self.sbase = None
        self.ebase = None

        self.buildTree()
        self.paintScreen()
        self.buildProperty(None)

        self.tree_inspector.clicked.connect(self.treeClick)
        self.tree_linker.clicked.connect(self.linkerTreeClick)

        self.mm_designing.clicked.connect(self.paintScreen)
        self.mm_linking.clicked.connect(self.paintScreen)
        self.mm_editing.clicked.connect(self.paintScreen)
        self.mm_exporting.clicked.connect(self.paintScreen)

        self.hs_currframe.setMaximum(globals.frameLength)
        self.hs_currframe.valueChanged.connect(self.hscrollChange)

        self.pushButton.clicked.connect(self.renderTest)
        self.pushButton_2.clicked.connect(self.renderAll)

        self.pushButton_6.clicked.connect(self.frameBack)
        self.pushButton_5.clicked.connect(self.framePlayPause)
        self.pushButton_4.clicked.connect(self.frameAdvance)

        self.playTimer = QtCore.QTimer()
        self.playTimer.timeout.connect(self.frameAdvance)
        self.playTimer.setInterval(33)
        self.ltime = None

    def setTreeBase(self, pbase):
        self.pbase = pbase
        self.buildTree()
        self.paintScreen()
        self.buildProperty(None)
        if self.pbase:
            renderer.resetTimedValuesFrameLimit(self.pbase)

    def setLinkerBase(self, lbase):
        self.lbase = lbase
        self.paintOverlay()

    def renderTest(self):
        rnd = renderer.RenderWorker(self.frame, 5, self.pbase.copyPosTree())
        rnd.renderRun()

    def renderAll(self):
        t0 = time.clock()

        tcon = renderer.FixedPosRenderer(2)
        tcon.render(0, globals.frameLength, 5, self.pbase)
        
        t1 = time.clock()

        print("Avg", (t1-t0)/globals.frameLength)

    # Tree builders
    def buildTree(self):
        self.tree_inspector.clear()
        if self.pbase:
            buildQtTree(self.tree_inspector, self.pbase)

    def updateTreeName(self):
        chcnt = self.tree_inspector.topLevelItemCount()
        for i in range(chcnt):
            ch = self.tree_inspector.topLevelItem(i)
            updateQtTreeName(ch)

    def buildLinkerTree(self):
        self.tree_linker.clear()
        if self.lbase:
            buildQtLinkerTree(self.tree_linker, self.lbase)

    def paintScreen(self):
        self.paintWorld()
        self.paintOverlay()

    # Painters
    def paintWorld(self):
        geom = self.label_viewport.geometry()
        imsize = (geom.height(), geom.width(), 3)
        self.worldImg = np.full(imsize, 32, np.uint8)

        if self.pbase:
            self.pbase.evalPos()
            if self.mm_editing.isChecked() or self.mm_exporting.isChecked():
                impainter.paintSampledTree(self.worldImg, self.scale, self.pbase, self.frame)
            if self.mm_designing.isChecked() or self.mm_linking.isChecked():
                if globals.enable_opencl:
                    bgim = cv2.UMat(self.worldImg)
                    impainter.paintImageTree(bgim, self.worldImg.shape, self.scale, self.pbase, self.frame)
                    self.worldImg = bgim.get()
                else:
                    impainter.paintImageTree(self.worldImg, self.worldImg.shape, self.scale, self.pbase, self.frame)
            if not self.mm_exporting.isChecked():
                impainter.paintSignTree(self.worldImg, self.scale, self.pbase)

    def paintOverlay(self):
        img = self.worldImg.copy()

        if self.mm_linking.isChecked() and self.lbase:
            impainter.paintLinkerTree(img, self.scale, self.lbase)

        if globals.propertyContainer.activeNode:
            impainter.paintNodeSign(img, self.scale, globals.propertyContainer.activeNode, True)
        if globals.propertyContainer.activeTreeLine:
            if isinstance(globals.propertyContainer.activeTreeLine.node, logics.linkercore.DisplayChain):
                impainter.paintLinker(img, self.scale, globals.propertyContainer.activeTreeLine.node, True)

        self.label_viewport.setPixmap(QtGui.QPixmap.fromImage(cvMatToQimg(img)))

    # Properties
    def buildProperty(self, node):
            clearLayout(self.propertyWidget.layout())
            propertyEditor.buildNodePropertyPage(self, node)

    # UI callbacks
    def treeClick(self, qModelIndex):
        item = self.tree_inspector.currentItem()
        globals.propertyContainer.activeTreeLine = item
        
        if not globals.propertyContainer.activeNode is item.node:
            self.buildProperty(item.node)
            self.paintOverlay()

    def linkerTreeClick(self, qModelIndex):
        item = self.tree_linker.currentItem()
        globals.propertyContainer.activeTreeLine = item
        
        if isinstance(item.node, logics.linkercore.DisplayChain):
            if not globals.propertyContainer.activeNode is item.node.attachedNode:
                self.buildProperty(item.node.attachedNode)
                self.paintOverlay()
        else:
            if not globals.propertyContainer.activeNode is item.node:
                self.buildProperty(item.node)
                self.paintOverlay()

    def frameBack(self):
        self.frame -= 1
        if self.frame < 0:
            self.frame = 0

        self.hs_currframe.setValue(self.frame)

    def frameAdvance(self):
        self.frame += 1
        if self.frame >= globals.frameLength:
            self.frame = globals.frameLength - 1
            self.playTimer.stop()

        self.hs_currframe.setValue(self.frame)

    def framePlayPause(self):
        if self.playTimer.isActive():
            self.playTimer.stop()
        else:
            self.playTimer.start()

    def hscrollChange(self, value):
        self.frame = value
        self.label_currframe.setText(f"{value}/{self.hs_currframe.maximum()}")
        self.paintScreen()

    def onResize(self, a0):
        if self.oldResizeEvent:
            self.oldResizeEvent(a0)
        self.paintScreen()