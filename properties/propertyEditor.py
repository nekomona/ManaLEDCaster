import globals

import logics.node2d

from properties.generic import QDraggableLabel, PropertyEditorTree
from properties.node import buildNodeProperties

from PyQt5 import QtGui, QtWidgets

def buildNodePropertyPage(mwindow, node : logics.node2d.TreeNode):
    if node is not None:
        host = mwindow.propertyWidget.layout()

        globals.propertyContainer.activeNode = node
        editorBase = PropertyEditorTree()
        host.addLayout(buildNodeHeader(editorBase, node))
        
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        host.addWidget(line)

        flayout = QtWidgets.QFormLayout()
        flayout.setHorizontalSpacing(12)
        editorBase.flayout = flayout
        editorBase.mwindow = mwindow
        for rows in buildNodeProperties(editorBase, node):
            if type(rows) == tuple:
                flayout.addRow(*rows)
            elif rows is not None:
                flayout.addRow(rows)
        host.addLayout(flayout)

        nsp = QtWidgets.QSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding))
        host.addItem(nsp)

        return editorBase

def buildNodeHeader(editor : PropertyEditorTree, node : logics.node2d.TreeNode2D):
    # icon | name
    #           type
    nname = QtWidgets.QLineEdit(node.name)
    nname.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    
    def updateName(nval):
        node.name = nval
        editor.mwindow.updateTreeName()

    nname.textChanged.connect(updateName)
    editor.name = nname

    ntype = QtWidgets.QLabel(str(type(node)))
    ntype.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    
    nicon = QtWidgets.QLabel()
    nicon.setMinimumSize(32, 32)
    nicon.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    editor.icon = nicon

    # R side layout
    rlayout = QtWidgets.QVBoxLayout()
    rlayout.addWidget(nname)
    rlayout.addWidget(ntype)
    # Header layout
    hlayout = QtWidgets.QHBoxLayout()
    hlayout.addWidget(nicon)
    hlayout.addLayout(rlayout)

    return hlayout
