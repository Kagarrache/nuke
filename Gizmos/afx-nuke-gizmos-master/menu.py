# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2017, Ryan P. Wilson
#
#      Authority FX, Inc.
#      www.authorityfx.com

afx_gizmo_path = os.path.dirname(os.path.realpath(__file__))
nuke.pluginAddPath(os.path.join(afx_gizmo_path, 'icons'))

# Example function to adjust default knob values
# Function called by OnCreate callback
#def afxGlowDefaults():
#    n = nuke.thisNode()
#    if n.Class() == "afx_glow.gizmo":
#        n.knob("exposure").setDefaultValue([0])
#        n.knob("threshold").setDefaultValue([1])
#        n.knob("threshold_falloff").setDefaultValue([0.25])
#        n.knob("size").setDefaultValue([250])
#        n.knob("softness").setDefaultValue([0])
#        n.knob("diffusion").setDefaultValue([0.5])
#        n.knob("quality").setDefaultValue([0.5])
#        n.knob("replicate").setDefaultValue([0])
#        n.knob("expand_box").setDefaultValue([0])
            
nuke.menu('Nodes').addMenu('Authority FX', icon='afx.png')
for path in nuke.pluginPath():

    if os.path.isfile(path + '/AFXGlow.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXGlow...gizmo', lambda: nuke.createNode('AFXGlow.gizmo'), icon='afx.png')
        #Example on-create callback to adjust defaults knob values
        #nuke.addOnCreate(afxGlowDefaults, nodeClass = "afx_glow.gizmo")
    if os.path.isfile(path + '/AFXThreshold.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXThreshold...gizmo', lambda: nuke.createNode('AFXThreshold.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXSoftClip.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXSoftClip...gizmo', lambda: nuke.createNode('AFXSoftClip.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXMatteAdjust.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXMatteAdjust...gizmo', lambda: nuke.createNode('AFXMatteAdjust.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXToneMap.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXToneMap...gizmo', lambda: nuke.createNode('AFXToneMap.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXDeSpill.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXDeSpill...gizmo', lambda: nuke.createNode('AFXDeSpill.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXSpillReplace.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXSpillReplace...gizmo', lambda: nuke.createNode('AFXSpillReplace.gizmo'), icon='afx.png')
    if os.path.isfile(path + '/AFXEdgeExtend.gizmo') == True:
        nuke.menu('Nodes').addCommand('Authority FX/AFXEdgeExtend...gizmo', lambda: nuke.createNode('AFXEdgeExtend.gizmo'), icon='afx.png')