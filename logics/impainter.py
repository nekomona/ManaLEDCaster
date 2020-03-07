import logics.node2d
import logics.linkercore

import cv2
import numpy as np
import math

def paintMinHeadArrow(img, spos, epos, color, width):
    linelen = ((spos[0]-epos[0])**2 + (spos[1]-epos[1])**2)**0.5
    minWidth = 4*2 / linelen
    cv2.arrowedLine(img, spos, epos, color, width, line_type=cv2.LINE_AA, tipLength = max(0.1, minWidth))

def paintSampledTree(img, scale, tree, frame = 0):
    for ch in tree.child:
        paintSampledTree(img, scale, ch, frame)
    paintNodeSampled(img, scale, tree, frame)

def paintNodeSampled(img, scale, node, frame):
    pos = node.absPos.getScaledPos(scale)
    imsize = img.shape # h, w

    if isinstance(node, logics.node2d.SamplePoint):
        if node.sampledValue:
            fcolor = node.sampledValue.getValue(frame)
            if fcolor:
                node.sampleShape.paintShape(img, node.absPos, scale, fcolor, -1)

def paintImageTree(img, scale, tree, frame = 0):
    for ch in tree.child:
        paintImageTree(img, scale, ch, frame)
    paintNodeImage(img, scale, tree, frame)

def paintNodeImage(img, scale, node, frame):
    pos = node.absPos.getScaledPos(scale)
    outputsize = img.shape[1:None:-1]
    imscale = scale * node.absPos.scale
    widthScale = None
    
    imang = -math.degrees(node.absPos.rotRad)

    nodeim = None
    if isinstance(node, logics.node2d.Image):
        nodeim = node.image
        widthScale = node.widthScale
    elif isinstance(node, logics.node2d.Video):
        nodeim = node.fetchFrame(frame)
        widthScale = node.widthScale

    if nodeim is not None:
        h, w = nodeim.shape[:2]
        if widthScale:
            wmod = w * widthScale
        else:
            wmod = w
        # Merge translate, rotate and scale into a single affine transform
        mask = np.full((h, w), 255, np.uint8)
        tmat = cv2.getRotationMatrix2D((wmod/2, h/2), imang, imscale)
        # Add translate and move image center to node position
        tmat[:, 2] += pos
        tmat[:, 2] -= (wmod/2, h/2)
        # Magic matrix operation for width rescale!
        # (Actually simplified matmul with diag(w, 1, 1))
        tmat[:, 0] *= widthScale
        # Transform on both image and mask
        nodeimout = cv2.warpAffine(nodeim, tmat, outputsize)
        maskout = cv2.warpAffine(mask, tmat, outputsize)
        # Mask add to blend frame into image
        ret, binmask = cv2.threshold(maskout, 10, 255, cv2.THRESH_BINARY)
        invmask = cv2.bitwise_not(binmask)
        imfg = cv2.bitwise_and(nodeimout, nodeimout, mask=binmask)
        imbg = cv2.bitwise_and(img, img, mask=invmask)
        cv2.add(imfg, imbg, img)

def paintSignTree(img, scale, tree):
    for ch in tree.child:
        paintSignTree(img, scale, ch)
    paintNodeSign(img, scale, tree)

def paintNodeSign(img, scale, node, selected = False):
    pos = node.absPos.getScaledPos(scale)
    imsize = img.shape # h, w

    if selected:
        if   0 <= pos[0] and pos[0] < imsize[1] and 0 <= pos[1] and pos[1] < imsize[0]:
            if type(node) is logics.node2d.SamplePoint:
                node.sampleShape.paintShape(img, node.absPos, scale, (255, 255, 255), 4)
                node.sampleShape.paintShape(img, node.absPos, scale, (128, 128, 0), 2)
                # cv2.circle(img, pos, int(node.sampleRadius*scale), (128, 128, 0), 2)
            else:
                cv2.circle(img, pos, 4, (255, 255, 255), 2)
                cv2.circle(img, pos, 4, (128, 0, 128), -1)
        else:
            if type(node) is logics.node2d.SamplePoint:
                paintOutsideArrow(img, pos, (128, 128, 0), 2)
            else:
                paintOutsideArrow(img, pos, (128, 0, 128), 2)
    else:
        if type(node) is logics.node2d.SamplePoint:
            node.sampleShape.paintShape(img, node.absPos, scale, (0, 0, 255), 1)
            # cv2.circle(img, pos, int(node.sampleRadius*scale), (0, 0, 255), 1)
        else:
            cv2.circle(img, pos, 4, (0, 255, 0), -1)

def paintLinkerTree(img, scale, tree):
    for ch in tree.nodes:
        if isinstance(ch, logics.linkercore.DisplayChain):
            paintLinkerTree(img, scale, ch)
    paintLinker(img, scale, tree)

def paintLinker(img, scale, chain, selected = False):
    pcolor = (128, 0, 128) if selected else (0, 128, 0)
    invcolor = [255 for p in pcolor]
    lastnode = None
    if chain.reverse:
        for n in reversed(chain.nodes):
            if isinstance(n, logics.linkercore.DisplayChain):
                n = n.attachedNode
            if lastnode:
                paintMinHeadArrow(img, lastnode.absPos.getScaledPos(scale), n.absPos.getScaledPos(scale),  invcolor, 6)
                paintMinHeadArrow(img, lastnode.absPos.getScaledPos(scale), n.absPos.getScaledPos(scale),  pcolor, 4)
            lastnode = n
    else:
        for n in chain.nodes:
            if isinstance(n, logics.linkercore.DisplayChain):
                n = n.attachedNode
            if lastnode:
                paintMinHeadArrow(img, lastnode.absPos.getScaledPos(scale), n.absPos.getScaledPos(scale),  invcolor, 6)
                paintMinHeadArrow(img, lastnode.absPos.getScaledPos(scale),  n.absPos.getScaledPos(scale),  pcolor, 4)
            lastnode = n
    
def paintOutsideArrow(img, pos, color, width):
    imsize = img.shape # h, w
    center = (imsize[1]//2, imsize[0]//2) # w, h

    # midpoint = p*end + (1-p)*start

    premix = []
    if pos[0] != center[0]:
        # pleft
        premix.append(-center[0] / (pos[0]-center[0]))
        # pright
        premix.append((imsize[1]-center[0]) / (pos[0]-center[0]))
    if pos[1] != center[1]:
        # pup
        premix.append((imsize[1]-center[0]) / (pos[0]-center[0]))
        #pdown
        premix.append((imsize[0]-center[1]) / (pos[1]-center[1]))

    aftmix = [v for v in premix if v > 0]
    p = min(aftmix)

    screenedge = (int(pos[0]*p + center[0]*(1-p)), int(pos[1]*p + center[1]*(1-p)))
    drawstart = (int(screenedge[0] * 0.75 + center[0] * 0.25), int(screenedge[1] * 0.75 + center[1] * 0.25))
    
    paintMinHeadArrow(img, drawstart, screenedge, color, width)