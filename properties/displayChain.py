from properties.generic import PropertyEditorTree
from PyQt5 import QtWidgets

# DisplayChain
def buildDisplayChainEditor(obj : object, name : str, dispname : str, callback = None):
    wid = QtWidgets.QPushButton("Remove")

    return QtWidgets.QLabel(dispname), wid

def buildDisplayChainProperty(editor : PropertyEditorTree, obj : object, name : str, callback = None):
    return None
