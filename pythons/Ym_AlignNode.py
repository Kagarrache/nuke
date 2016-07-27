

"""
[ Ym_AlignNode ver 1.9 ]    update. 01 Sep 2014

This script helps to align for messed up nodes.

Align along X and Y axis.
Align equal interval between each node.
Similar interface like Adobe software align tool.

- Notice -
Request for improvement : feel free to contact me!

---------------- copyright (c) Yousuke Matsuno --------------------
yousuke.matsuno@gmail.com - http://www.mat-vfx.com
-------------------------------------------------------------------
"""


import nuke


##---------- def ----------
def F_CmpX(cx1,cx2):
    cx1centX = cx1.xpos() + cx1.screenWidth() / 2
    cx2centX = cx2.xpos() + cx2.screenWidth() / 2

    if cx1centX < cx2centX:
        return -1
    else:
        return 0


def F_CmpY(cy1,cy2):
    cy1centY = cy1.ypos() + cy1.screenHeight() / 2
    cy2centY = cy2.ypos() + cy2.screenHeight() / 2

    if cy1centY < cy2centY:
        return -1
    else:
        return 0


##---------- align left X ----------
def F_AlignLX():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []

        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)

        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpX)
            leftX =  nodeList[0].xpos() + nodeList[0].screenWidth() / 2
        
            for n in range(0, sn):
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(leftX - sizeGap)


##---------- align center X ----------
def F_AlignCX():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []

        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)

        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpX)
            centX =  (nodeList[0].xpos() + nodeList[0].screenWidth() / 2) + ((nodeList[sn-1].xpos() + nodeList[sn-1].screenWidth() / 2) - (nodeList[0].xpos() + nodeList[0].screenWidth() / 2)) / 2
                
            for n in range(0, sn):
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(centX - sizeGap)


##---------- align right X ----------
def F_AlignRX():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpX)
            rightX =  nodeList[sn-1].xpos() + nodeList[sn-1].screenWidth() / 2
        
            for n in range(0, sn):
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(rightX - sizeGap)


##---------- align top Y ----------
def F_AlignTY():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpY)
            topY = nodeList[0].ypos() + nodeList[0].screenHeight() / 2
        
            for n in range(0, sn):
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(topY - sizeGap)


##---------- align center Y ----------
def F_AlignCY():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpY)
            centY = (nodeList[0].ypos() + nodeList[0].screenHeight() / 2) + ((nodeList[sn-1].ypos() + nodeList[sn-1].screenHeight() / 2) - (nodeList[0].ypos() + nodeList[0].screenHeight() / 2)) / 2
        
            for n in range(0, sn):
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(centY - sizeGap)


##---------- align under Y ----------
def F_AlignUY():
    if len(nuke.selectedNodes()) > 1:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 1:
            sn = len(nodeList)
            nodeList.sort(F_CmpY)
            underY = nodeList[sn-1].ypos() + nodeList[sn-1].screenHeight() / 2
        
            for n in range(0, sn):
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(underY - sizeGap)


##---------- align interval X ----------
def F_Align_intX():
    if len(nuke.selectedNodes()) > 2:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 2:
            sn = len(nodeList)
            nodeList.sort(F_CmpX)
            intX = int(((nodeList[sn-1].xpos() + nodeList[sn-1].screenWidth() / 2) - (nodeList[0].xpos() + nodeList[0].screenWidth() / 2)) / float (sn-1))
        
            for n in range(0, sn):
                xl = (nodeList[0].xpos() + nodeList[0].screenWidth() / 2) + (intX*n)
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(xl - sizeGap)


##---------- align interval Y ----------
def F_Align_intY():
    if len(nuke.selectedNodes()) > 2:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 2:
            sn = len(nodeList)
            nodeList.sort(F_CmpY)
            intY = int(((nodeList[sn-1].ypos() + nodeList[sn-1].screenHeight() / 2) - (nodeList[0].ypos() + nodeList[0].screenHeight() / 2)) / float (sn-1))
        
            for n in range(0, sn):
                yl = (nodeList[0].ypos() + nodeList[0].screenHeight() / 2) + (intY*n)
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(yl - sizeGap)


##---------- align interval XX ----------
def F_Align_intXX():
    if len(nuke.selectedNodes()) > 2:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 2:
            sn = len(nodeList)
            nodeList.sort(F_CmpX)
            intX = int(((nodeList[sn-1].xpos() + nodeList[sn-1].screenWidth() / 2) - (nodeList[0].xpos() + nodeList[0].screenWidth() / 2)) / float (sn-1))
            intY = int(((nodeList[sn-1].ypos() + nodeList[sn-1].screenHeight() / 2) - (nodeList[0].ypos() + nodeList[0].screenHeight() / 2)) / float (sn-1))
            
            for n in range(0, sn):
                xl = (nodeList[0].xpos() + nodeList[0].screenWidth() / 2) + (intX*n)
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(xl - sizeGap)
            
            for n in range(0, sn):
                yl = (nodeList[0].ypos() + nodeList[0].screenHeight() / 2) + (intY*n)
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(yl - sizeGap)


##---------- align interval YY ----------
def F_Align_intYY():
    if len(nuke.selectedNodes()) > 2:
        nodeList = []
        for n in nuke.selectedNodes():
            if n.Class() != "BackdropNode" and n.Class() != "Viewer":
                nodeList.append(n)
        
        if len(nodeList) > 2:
            sn = len(nodeList)
            nodeList.sort(F_CmpY)
            intX = int(((nodeList[sn-1].xpos() + nodeList[sn-1].screenWidth() / 2) - (nodeList[0].xpos() + nodeList[0].screenWidth() / 2)) / float (sn-1))
            intY = int(((nodeList[sn-1].ypos() + nodeList[sn-1].screenHeight() / 2) - (nodeList[0].ypos() + nodeList[0].screenHeight() / 2)) / float (sn-1))
        
            for n in range(0, sn):
                yl = (nodeList[0].ypos() + nodeList[0].screenHeight() / 2) + (intY*n)
                sizeGap = nodeList[n].screenHeight() / 2
                nodeList[n].setYpos(yl - sizeGap)
            
            for n in range(0, sn):
                xl = (nodeList[0].xpos() + nodeList[0].screenWidth() / 2) + (intX*n)
                sizeGap = nodeList[n].screenWidth() / 2
                nodeList[n].setXpos(xl - sizeGap)