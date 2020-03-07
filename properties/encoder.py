from properties.generic import QDraggableLabel, PropertyEditorTree

import logics.encoder

from PyQt5 import QtWidgets

# Encoder
def buildEncoderEditor(obj : object, name : str, dispname : str, callback = None):
    wid = QtWidgets.QComboBox()
    wid.addItems(logics.encoder.encoderList)
    wid.setCurrentIndex(logics.encoder.EncoderFactory.searchEncoder(getattr(obj, name)))

    def updateEncoder(ind):
        nenc = logics.encoder.EncoderFactory.buildEncoder(ind)
        setattr(obj, name, nenc)
        if callback is not None:
            callback()

    wid.currentIndexChanged.connect(updateEncoder)

    return QtWidgets.QLabel(dispname), wid

def buildEncoderProperty(editor : PropertyEditorTree, obj : object, name : str, callback = None):
    return None
