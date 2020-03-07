import logics.shape

from properties.generic import PropertyEditorTree
import properties.simple

from PyQt5 import QtWidgets

# Shape
def buildShapeEditor(obj : object, name : str, dispname : str, callback = None):
    wid = QtWidgets.QComboBox()
    wid.addItems(logics.shape.shapeList)
    wid.setCurrentIndex(logics.shape.ShapeFactory.searchShape((getattr(obj, name))))

    def updateShape(ind):
        nshape = logics.shape.ShapeFactory.buildShape(ind)
        setattr(obj, name, nshape)
        if callback is not None:
            callback()

    wid.currentIndexChanged.connect(updateShape)

    return QtWidgets.QLabel(dispname), wid

def buildShapeProperty(editor : PropertyEditorTree, obj : object, name : str, callback = None):
    lshape = getattr(obj, name)

    fwidget = QtWidgets.QWidget()

    flayout = QtWidgets.QFormLayout()
    flayout.setHorizontalSpacing(12)
    flayout.setContentsMargins(20, 0, 0, 0)

    if isinstance(lshape, logics.shape.Round):
        labelr, liner = properties.simple.buildFloatEditor(lshape, 'radius', "Radius", callback)
        editor.radius = PropertyEditorTree(labelr, liner)
        flayout.addRow(labelr, liner)
    elif isinstance(lshape, logics.shape.Rectangle):
        labelw, linew = properties.simple.buildFloatEditor(lshape, 'width', "Width", callback)
        editor.width = PropertyEditorTree(labelw, linew)
        flayout.addRow(labelw, linew)
        labelh, lineh = properties.simple.buildFloatEditor(lshape, 'height', "Height", callback)
        editor.width = PropertyEditorTree(labelh, lineh)
        flayout.addRow(labelh, lineh)

    fwidget.setLayout(flayout)

    return fwidget