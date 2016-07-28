# Generate Postage Stamp from Node 1.0
# Copyright (c) 2011 Victor Perez.  All Rights Reserved.
### Add to menu.py ###
#import postageStampGenerator
#VictorMenu = nuke.menu('Nuke').addMenu('V!ctor')
#VictorMenu.addCommand('Generate PostageStamp from node', 'postageStampGenerator.postageStampGenerator()', 'ctrl+alt+p')
###

import nuke

def postageStampGenerator():
   nodeSelection = []
   for n in nuke.selectedNodes():
       node = n
       nodeName = node.knob('name').value()
       nodeXPosition = node['xpos'].value()
       nodeYPosition = node['ypos'].value()
       nodeColor = node.knob('tile_color').getValue()
       node.knob('selected').setValue(False)
       PS = nuke.createNode('PostageStamp', inpanel = False)
       PS.setInput(0,node)
       checkName = nodeName+'_PostageStamp'
       nodeNameCheck = 1
       nameIncrements = 0
       nameNumberFound = False
       while nameNumberFound is False:
           for i in nuke.allNodes():
               if i.knob('name').value() == checkName+str(nodeNameCheck):
                   print i.knob('name').value()
                   nodeNameCheck = nodeNameCheck + 1
           nameIncrements = nameIncrements + 1
           if nodeNameCheck == nameIncrements:
               nameNumberFound = True
       PS.knob('name').setValue(checkName+str(nodeNameCheck))
       if node.Class() == 'Read':
           PS.knob('label').setValue('[file tail [value '+nodeName+'.file]]\n[value '+nodeName+'.label]')
       else:
           PS.knob('label').setValue('[value '+nodeName+'.label]')
       PS['xpos'].setValue(nodeXPosition+75)
       PS['ypos'].setValue(nodeYPosition+75)
       PS.knob('hide_input').setValue(True)
       PS.knob('selected').setValue(False)
       nodeSelection.append(n)
   for y in nodeSelection:
       y.knob('selected').setValue(True)
       print nodeSelection

   if len(nuke.selectedNodes()) == 0:
       nuke.message('No nodes selected')