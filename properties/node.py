import globals
import logics.node2d

from properties.generic import PropertyEditorTree

from properties.pos2d import buildPos2DEditor
from properties.displayChain import buildDisplayChainEditor, buildDisplayChainProperty
from properties.shape import buildShapeEditor, buildShapeProperty
from properties.encoder import buildEncoderEditor, buildEncoderProperty
from properties.simple import buildIntEditor, buildFloatEditor

def buildNodeProperties(editor : PropertyEditorTree, node : logics.node2d.TreeNode):
    if type(node) == logics.node2d.TreeNode2D:
        return buildTreeNode2DProperties(editor, node)
    if type(node) ==  logics.node2d.SamplePoint:
        return buildSamplePointProperties(editor, node)
    if type(node) ==  logics.node2d.SamplePlane:
        pass
    if type(node) ==  logics.node2d.Image:
        return buildImageProperties(editor, node)
    if type(node) ==  logics.node2d.Video:
        return buildVideoProperties(editor, node)

    return []

def buildTreeNode2DProperties(editor : PropertyEditorTree, node : logics.node2d.TreeNode2D):
    rows = []

    def repaintCallback():
        if globals.repaintScreen is not None:
            globals.repaintScreen()

    editor.offPos = PropertyEditorTree()
    pl, pw = buildPos2DEditor(editor.offPos, node, 'offPos', "Position", repaintCallback)
    rows.append((pl, pw))

    if hasattr(node, "displayChain"):
        editor.displayChain = PropertyEditorTree()
        dl, dw = buildDisplayChainEditor(node, "displayChain", "Display Chain", repaintCallback)
        dp = buildDisplayChainProperty(editor.displayChain, node, "displayChain", repaintCallback)
        rows.append((dl, dw))
        rows.append(dp)
    
    return rows

def buildSamplePointProperties(editor : PropertyEditorTree, node : logics.node2d.SamplePoint):
    rows = []

    def repaintCallback():
        if globals.repaintScreen is not None:
            globals.repaintScreen()

    editor.offPos = PropertyEditorTree()
    pl, pw = buildPos2DEditor(editor.offPos, node, 'offPos', "Position", repaintCallback)
    rows.append((pl, pw))
    
    editor.sampleShape = PropertyEditorTree()
    sp = buildShapeProperty(editor.sampleShape, node, "sampleShape", repaintCallback)
    editor.sampleShape.Input = sp

    def changeShapeCallback():
        repaintCallback()
        osp = editor.sampleShape.Input
        host = osp.parentWidget()
        nsp = buildShapeProperty(editor.sampleShape, node, "sampleShape", repaintCallback)
        osp = host.layout().replaceWidget(osp, nsp)
        osp.widget().deleteLater()
        editor.sampleShape.Input = nsp

    sl, sw = buildShapeEditor(node, "sampleShape", "Sampling Shape", changeShapeCallback)
    rows.append((sl, sw))
    rows.append(sp)

    editor.encoder = PropertyEditorTree()
    el, ew = buildEncoderEditor(node, 'encoder', "Encoder", repaintCallback)
    ep = buildEncoderProperty(editor.encoder, node, 'encoder', repaintCallback)
    rows.append((el, ew))
    rows.append(ep)

    return rows

def buildImageProperties(editor : PropertyEditorTree, node : logics.node2d.Image):
    rows = []

    def repaintCallback():
        if globals.repaintScreen is not None:
            globals.repaintScreen()

    editor.offPos = PropertyEditorTree()
    pl, pw = buildPos2DEditor(editor.offPos, node, 'offPos', "Position", repaintCallback)
    rows.append((pl, pw))

    wl, ww = buildFloatEditor(node, 'widthScale', "Width Scale", repaintCallback)
    editor.widthScale = PropertyEditorTree(wl, ww)
    rows.append((wl, ww))

    return rows

def buildVideoProperties(editor : PropertyEditorTree, node : logics.node2d.Video):
    rows = []

    def repaintCallback():
        if globals.repaintScreen is not None:
            globals.repaintScreen()

    editor.offPos = PropertyEditorTree()
    pl, pw = buildPos2DEditor(editor.offPos, node, 'offPos', "Position", repaintCallback)
    rows.append((pl, pw))

    sl, sw = buildIntEditor(node, 'startFrame', "Start Frame", repaintCallback)
    editor.startFrame = PropertyEditorTree(sl, sw)
    rows.append((sl, sw))

    wl, ww = buildFloatEditor(node, 'widthScale', "Width Scale", repaintCallback)
    editor.widthScale = PropertyEditorTree(wl, ww)
    rows.append((wl, ww))

    return rows