from properties.generic import PropertyEditorTree
from properties.simple import buildFloatEditor

from PyQt5 import QtWidgets

# Pos2D
def buildPos2DEditor(editor : PropertyEditorTree, obj : object, name : str, dispname: str, callback = None):
    base = QtWidgets.QHBoxLayout()
    base.setSpacing(8);
    fleft = QtWidgets.QFormLayout()
    fright = QtWidgets.QFormLayout()

    posObj = getattr(obj, name)

    lx, wx = buildFloatEditor(posObj, 'posX', "X", callback)
    editor.posX = PropertyEditorTree(lx, wx)
    ly, wy = buildFloatEditor(posObj, 'posY', "Y", callback)
    editor.posY = PropertyEditorTree(ly, wy)
    ls, ws = buildFloatEditor(posObj, 'scale', "Scale", callback)
    editor.scale = PropertyEditorTree(ls, ws)
    lr, wr = buildFloatEditor(posObj, 'rotRad', "Angle", callback)
    editor.rotRad = PropertyEditorTree(lr, wr)
    lr.mouseScale = 0.0001

    wslock = QtWidgets.QCheckBox("Lock Scale")
    wslock.setChecked(posObj.lockScale)
    editor.lockScale = wslock

    wslock.stateChanged.connect(lambda nval=0, swid=ls: swid.setEnabled(nval <= 0) )
    wslock.stateChanged.connect(lambda nval=0, swid=ws: swid.setEnabled(nval <= 0) )
    wslock.stateChanged.connect(lambda nval=0, lobj=posObj: setattr(lobj, 'lockScale', nval > 0) )
    ws.setEnabled(not posObj.lockScale)
    ls.setEnabled(not posObj.lockScale)

    fleft.addRow(lx, wx)
    fright.addRow(ly, wy)
    fleft.addRow(ls, ws)
    fright.addRow(lr, wr)
    fleft.addRow(wslock)

    base.addLayout(fleft)
    base.addLayout(fright)

    return QtWidgets.QLabel(dispname), base