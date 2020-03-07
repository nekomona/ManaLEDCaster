from PyQt5 import QtWidgets, QtCore, Qt

modifyPrecision = 4

class PropertyEditorTree(object):
    def __init__(self, Label = None, Input = None):
        self.Label = Label
        self.Input = Input

class QDraggableLabel(QtWidgets.QLabel):
    # Add ability to drag on label to change paired value
    editFinished = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        self.mouseScale = 0.1
        self.pairedLine = None
        self.intValue = False

        self.mouseDown = False
        retval = super().__init__(*args, **kwargs)
        self.setCursor(Qt.QCursor(QtCore.Qt.SizeHorCursor))
        return retval
    
    def setEnabled(self, val):
        if val:
            self.setCursor(Qt.QCursor(QtCore.Qt.SizeHorCursor))
        else:
            self.setCursor(Qt.QCursor(QtCore.Qt.ArrowCursor))
        super().setEnabled(val)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self.mouseDown = True
            self.xpress = event.globalX()
            self.ypress = event.globalY()
            self.setCursor(Qt.QCursor(QtCore.Qt.BlankCursor)) # Hide cursor
            self.move = 0
            if self.pairedLine:
                self.baseValue = str2float(self.pairedLine.text())
    
    def mouseReleaseEvent(self, event):
        self.mouseDown = False
        self.setCursor(Qt.QCursor(QtCore.Qt.SizeHorCursor)) # Unhide cursor
        self.editFinished.emit()

    def mouseMoveEvent(self, event):
        if self.mouseDown:
            cmove = event.globalX() - self.xpress
            self.move += cmove
            # self.move += cmove * abs(cmove)**0.5
            Qt.QCursor.setPos(self.xpress, self.ypress)
            if self.pairedLine:
                nvalue = self.baseValue + self.move * self.mouseScale
                if self.intValue:
                    nvalue = int(nvalue)
                else:
                    nvalue = round(nvalue, modifyPrecision);
                self.pairedLine.setText(str(nvalue)) # Update new value

def str2int(text):
    if len(text) == 0 or text == '-':
        return 0
    else:
        return int(text)

def str2float(text):
    if len(text) == 0 or text == '-' or text == '.':
        return 0.0
    else:
        return float(text)    