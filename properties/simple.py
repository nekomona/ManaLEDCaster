from properties.generic import *

from PyQt5 import QtGui, QtWidgets

# Int
def buildIntEditor(obj : object, name : str, dispname : str, callback = None):
    wid = QtWidgets.QLineEdit(str(getattr(obj, name)))
    wid.setValidator(QtGui.QIntValidator())
    
    def updateInt(val):
        setattr(obj, name, str2int(val))
        if callback is not None:
            callback()
    
    wid.textChanged.connect(updateInt)
    
    lwid = QDraggableLabel(dispname)
    lwid.intValue = True
    lwid.pairedLine = wid
    return lwid, wid

# Float / Real
def buildFloatEditor(obj : object, name : str, dispname : str, callback = None):
    wid = QtWidgets.QLineEdit(str(getattr(obj, name)))
    wid.setValidator(QtGui.QDoubleValidator())

    def updateFloat(val):
        setattr(obj, name, str2float(val))
        if callback is not None:
            callback()

    wid.textChanged.connect(updateFloat)
    
    lwid = QDraggableLabel(dispname)
    lwid.pairedLine = wid
    return lwid, wid