# V!ctor Tools
# Copyright (c) 2011 Victor Perez.  All Rights Reserved.

import nuke, colorsys, operator

### Preset Backdrop
def presetBackdrop():
    customPreset = None
    sep = '"'
    presets = ['Additive_Key','Bloom','Camera_Projection','Camera_Setup','CG','CG:Ambient','CG:Diffuse','CG:Reflection','CG:Refraction','CG:Shadow','CG:Specular','Cleanup','Controllers','Color_Correction','Despill','Edge_Fixes','Elements','FX','Key','Matte','Lens_Flare','Light_Setup','Light_Wrap','Output','Previous_Versions','References','Relight','Resources','Rig_Removal','Roto','Set_Extension','Stereo_Fixes','Temp','Test','Transformations']
    p = nuke.Panel('Preset Backdrop')
    p.addEnumerationPulldown('Preset',' '.join(presets))
    p.addSingleLineInput('Custom Label','')
    if p.show():
        customPreset = p.value('Preset')
        customLabel = p.value('Custom Label')
    
    # Backdrop presets
    if customPreset == 'Additive_Key':
        presetLabel = 'Additive Key'
        presetIcon = 'Keyer.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)
        
    if customPreset == 'Bloom':
        presetLabel = 'Bloom'
        presetIcon = 'Glint.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.5)
        
    if customPreset == 'Camera_Projection':
        presetLabel = 'Camera Projection'
        presetIcon = 'Card.png'
        presetColor = colorsys.hsv_to_rgb(0.667, 1, 0.5)
        
    if customPreset == 'Camera_Setup':
        presetLabel = 'Camera Setup'
        presetIcon = 'Camera.png'
        presetColor = colorsys.hsv_to_rgb(0, 1, 0.5)
        
    if customPreset == 'CG':
        presetLabel = 'CG'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Ambient':
        presetLabel = 'CG: Ambient'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Diffuse':
        presetLabel = 'CG: Diffuse'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Reflection':
        presetLabel = 'CG: Reflection'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Refraction':
        presetLabel = 'CG: Refraction'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Shadow':
        presetLabel = 'CG: Shadow'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'CG:Specular':
        presetLabel = 'CG: Specular'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
        
    if customPreset == 'Cleanup':
        presetLabel = 'Cleanup'
        presetIcon = 'DustBust.png'
        presetColor = colorsys.hsv_to_rgb(0.450, 0.44, 0.384)
        
    if customPreset == 'Controllers':
        presetLabel = 'Controllers'
        presetIcon = 'LevelSet.png'
        presetColor = colorsys.hsv_to_rgb(0.805, 1, 0.3)
        
    if customPreset == 'Color_Correction':
        presetLabel = 'Color Correction'
        presetIcon = 'ColorLookup.png'
        presetColor = colorsys.hsv_to_rgb(0.607, 0.528, 0.5)
        
    if customPreset == 'Despill':
        presetLabel = 'Despill'
        presetIcon = 'HueCorrect.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0.528, 0.5)
        
    if customPreset == 'Edge_Fixes':
        presetLabel = 'Edge Fixes'
        presetIcon = 'EdgeDetect.png'
        presetColor = colorsys.hsv_to_rgb(0.256, 0.354, 0.5)
        
    if customPreset == 'Elements':
        presetLabel = 'Elements'
        presetIcon = 'Read.png'
        presetColor = colorsys.hsv_to_rgb(0.125, 1, 0.5)
        
    if customPreset == 'FX':
        presetLabel = 'FX'
        presetIcon = ':qrc/images/ToolbarFilter.png'
        presetColor = colorsys.hsv_to_rgb(0.812, 1, 0.5)
        
    if customPreset == 'Key':
        presetLabel = 'Key'
        presetIcon = 'Keyer.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)
        
    if customPreset == 'Matte':
        presetLabel = 'Matte'
        presetIcon = 'Radial.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.1)
        
    if customPreset == 'Lens_Flare':
        presetLabel = 'Lens Flare'
        presetIcon = 'Flare.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0.354, 0.5)
        
    if customPreset == 'Light_Setup':
        presetLabel = 'Light Setup'
        presetIcon = 'SpotLight.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0, 0.5)
        
    if customPreset == 'Light_Wrap':
        presetLabel = 'Light Wrap'
        presetIcon = 'LightWrap.png'
        presetColor = colorsys.hsv_to_rgb(0.91, 0.62, 0.5)
        
    if customPreset == 'Output':
        presetLabel = 'Output'
        presetIcon = 'Write.png'
        presetColor = colorsys.hsv_to_rgb(0.167, 1, 0.373)
        
    if customPreset == 'Previous_Versions':
        presetLabel = 'Previous Versions'
        presetIcon = 'Viewer.png'
        presetColor = colorsys.hsv_to_rgb(0.125, 0, 0.3)
        
    if customPreset == 'References':
        presetLabel = 'References'
        presetIcon = 'SideBySide.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0, 0.298)
        
    if customPreset == 'Relight':
        presetLabel = 'Relight'
        presetIcon = 'ReLight.png'
        presetColor = colorsys.hsv_to_rgb(0.938, 1, 0.5)
        
    if customPreset == 'Resources':
        presetLabel = 'Resources'
        presetIcon = 'Merge.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0, 0.298)
        
    if customPreset == 'Rig_Removal':
        presetLabel = 'Rig Removal'
        presetIcon = 'MarkerRemoval.png'
        presetColor = colorsys.hsv_to_rgb(0, 0.443, 0.38)    
        
    if customPreset == 'Roto':
        presetLabel = 'Roto'
        presetIcon = 'Roto.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 0.430, 0.384)
        
    if customPreset == 'Set_Extension':
        presetLabel = 'Set Extension'
        presetIcon = 'Reformat.png'
        presetColor = colorsys.hsv_to_rgb(0.2, 1, 0.5)
        
    if customPreset == 'Stereo_Fixes':
        presetLabel = 'Stereo Fixes'
        presetIcon = 'Anaglyph.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.267)
        
    if customPreset == 'Temp':
        presetLabel = 'Temp'
        presetIcon = 'CheckerBoard.png'
        presetColor = colorsys.hsv_to_rgb(0, 1, 1)
        
    if customPreset == 'Test':
        presetLabel = 'Test'
        presetIcon = 'ClipTest.png'
        presetColor = colorsys.hsv_to_rgb(0, 0, 0.3)
        
    if customPreset == 'Transformations':
        presetLabel = 'Transformations'
        presetIcon = '2D.png'
        presetColor = colorsys.hsv_to_rgb(0.819, 0.286, 0.329)
        
        
    ### Backdrop creation based on presets
    if customPreset is not None:
        # RGB to HEX
        r = presetColor[0]
        g = presetColor[1]
        b = presetColor[2]
        hexColour = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,1), 16)
        
        if presetIcon == '':
            icon = ''
        else:
            icon = '<img src='+sep+presetIcon+sep+'> '
            
        selNodes = nuke.selectedNodes()
        if not selNodes:
            if customLabel == '':
                return nuke.nodes.BackdropNode(label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
            else:
                return nuke.nodes.BackdropNode(label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
    
       
        # Find Min. and Max. of Positions
        positions = [(i.xpos(), i.ypos()) for i in selNodes]
        xPos = sorted(positions, key = operator.itemgetter(0))
        yPos = sorted(positions, key = operator.itemgetter(1))
        xMinMaxPos = (xPos[0][0], xPos[-1:][0][0])
        yMinMaxPos = (yPos[0][1], yPos[-1:][0][1])
        
        if customLabel == '':
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
        else:
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
            
        n['selected'].setValue(False)
       
        # Revert to Previous Selection
        [i['selected'].setValue(True) for i in selNodes]
        
        return n
    else:
        pass