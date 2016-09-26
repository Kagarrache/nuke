import nuke 
import random


def autoBackdrop(name): 
    ''' 
    Automatically puts a backdrop behind the selected nodes. 
     
    The backdrop will be just big enough to fit all the select nodes in, with room 
    at the top for some text in a large font. 
    ''' 
    selNodes = nuke.selectedNodes() 
    if not selNodes: 
      return nuke.nodes.BackdropNode() 
   
    # Calculate bounds for the backdrop node. 
    bdX = min([node.xpos() for node in selNodes]) 
    bdY = min([node.ypos() for node in selNodes]) 
    bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX 
    bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY 
     
    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom 
    left, top, right, bottom = (-10, -80, 70, 10) 
    bdX += left 
    bdY += top 
    bdW += (right - left) 
    bdH += (bottom - top) 
     
    n = nuke.nodes.BackdropNode(xpos = bdX, 
                                bdwidth = bdW, 
                                ypos = bdY, 
                                bdheight = bdH, 
                                tile_color = int((random.random()*(200 - 100))) + 10, 
                                note_font_size=20,
                                label= name) 
   
    # revert to previous selection 
    n['selected'].setValue(False) 
    for node in selNodes: 
      node['selected'].setValue(False) 
    
    return n 


def autocomper():    
    global node
    node = nuke.selectedNode()
    global name    
    name = node.knob('name').value()
    global knob
    knob = ('[knob in]')
    autoComp(node)
    

def copy():
    if no_pass == 24:
        return
    nuke.Layer( name+'alphaStored', [name+'alphaStored.alpha'])
    global copyalpha
    copyalpha = nuke.nodes.Copy(inputs=[node, node] )
    copyalpha['from0'].setValue( 'rgba.alpha' )
    copyalpha['to0'].setValue( name+'alphaStored.alpha' )
    global alpha_copy
    alpha_copy = copyalpha['to0'].value()
    global main_dot
    main_dot = nuke.nodes.Dot( inputs=[ copyalpha ] )
    
   




def shuffleLayer( node, layer ):
    '''
    Shuffle a given layer into rgba
    args:
       node  - node to attach a Shuffle node to
       layer - layer to shuffle into rgba
    '''
    
    shuffleNode = nuke.nodes.Shuffle( label=knob, inputs=[punto] )
    shuffleNode['in'].setValue( layer )
    shuffleNode['postage_stamp'].setValue( True )
    return nuke.nodes.Dot( inputs=[ shuffleNode ] )


def autoComp( node ):
    channels = node.channels()
    layers = list( set([c.split('.')[0] for c in channels]) )
    none = ('none')
    layers.sort()
    layers.insert(0, none)
    node['selected'].setValue(False)
    # CREATE SIMPLE PANEL TO MAP THE BUFFERS
    p = nuke.Panel( 'AOVs' )
    p.addEnumerationPulldown( 'raw_(total)lighting', ' '.join( layers ) )
    p.addEnumerationPulldown( 'raw_shadow', ' '.join( layers ) )
    p.addEnumerationPulldown( 'diffuse', ' '.join( layers ) )
    p.addEnumerationPulldown( '(total)lighting', ' '.join( layers ) )
    p.addEnumerationPulldown( 'shadow', ' '.join( layers ) )
    p.addEnumerationPulldown( 'GI', ' '.join( layers ) )
    p.addEnumerationPulldown( 'reflection', ' '.join( layers ) )
    p.addEnumerationPulldown( 'specular', ' '.join( layers ) )
    p.addEnumerationPulldown( 'refraction', ' '.join( layers ) )
    p.addEnumerationPulldown( 'subsurface', ' '.join( layers ) )
    p.addEnumerationPulldown( 'self_illumination', ' '.join( layers ) )
    p.addEnumerationPulldown( 'light_1', ' '.join( layers ) )
    p.addEnumerationPulldown( 'light_2', ' '.join( layers ) )
    p.addEnumerationPulldown( 'light_3', ' '.join( layers ) )
    p.addEnumerationPulldown( 'light_4', ' '.join( layers ) )
    p.addEnumerationPulldown( 'light_5', ' '.join( layers ) )
    p.addEnumerationPulldown( 'ID_1', ' '.join( layers ) )
    p.addEnumerationPulldown( 'ID_2', ' '.join( layers ) )
    p.addEnumerationPulldown( 'ID_3', ' '.join( layers ) )
    p.addEnumerationPulldown( 'ID_4', ' '.join( layers ) )
    p.addEnumerationPulldown( 'ID_5', ' '.join( layers ) )
    p.addEnumerationPulldown( 'amb_occlusion', ' '.join( layers ) )
    p.addEnumerationPulldown( 'normals', ' '.join( layers ) )
    p.addEnumerationPulldown( 'position', ' '.join( layers ) )
    p.addEnumerationPulldown( 'depth', ' '.join( layers ) )
    p.addBooleanCheckBox( 'get rawlight by dividing', False)
    p.addBooleanCheckBox( 'create new alpha copy', True)
    p.addBooleanCheckBox( 'unpremult passes', True )
    if not p.show():
        return
    global main_dot
    global no_pass
    global place_x
    global x_value
    global copied
    global active_rawlight
    copied = False
    x_value = 180
    place_x = x_value
    no_pass = 0
    global first_shuffle
    first_shuffle = False
    global merge_raw_diffuse
    merge_raw_diffuse = False
    global div_diff_total
    div_diff_total = False
    active_rawlight = False

    # STORE PANEL RESULT IN VARIABLES FOR EASE OF USE

    restore_alpha = ('Restore_alpha')
    raw_lighting = p.value( 'raw_(total)lighting' )
    raw_shadow = p.value( 'raw_shadow' )
    diffuse = p.value( 'diffuse' )
    total_lighting = p.value( '(total)lighting' )
    shadow = p.value( 'shadow' )
    reflection = p.value( 'reflection' )
    spec = p.value( 'specular' )
    gi = p.value( 'GI' )
    refraction = p.value( 'refraction' )
    subsurface = p.value( 'subsurface' )
    self_illumination = p.value( 'self_illumination' )
    light_1 = p.value( 'light_1' )
    light_2 = p.value( 'light_2' )
    light_3 = p.value( 'light_3' )
    light_4 = p.value( 'light_4' )
    light_5 = p.value( 'light_5' )
    amb_occlusion = p.value( 'amb_occlusion' )
    ID_1 = p.value( 'ID_1' )
    ID_2 = p.value( 'ID_2' )
    ID_3 = p.value( 'ID_3' )
    ID_4 = p.value( 'ID_4' )
    ID_5 = p.value( 'ID_5' )
    normals = p.value( 'normals' )
    position = p.value( 'position' )
    depth = p.value( 'depth' )
    dividing = p.value( 'get rawlight by dividing' )
    alpha_layer = p.value( 'create new alpha copy')
    unpremult = p.value( 'unpremult passes' )
    # CREATE COPY NODE
    if ( p.value( 'create new alpha copy' ) == True): 
        copy()
        copied = True
        dots = main_dot
    else:
        main_dot = nuke.nodes.Dot( inputs=[ node ] )
        dots = main_dot
    copy_dot_xpos = dots.xpos()
    copy_dot_ypos = dots.ypos()
    dots['xpos'].setValue( copy_dot_xpos )
    dots['ypos'].setValue( copy_dot_ypos+25 )


    # CREATE SHUFFLE NODES


    if( p.value( 'get rawlight by dividing' ) == True):
        if( p.value( 'diffuse' ) == 'none') or ( p.value( '(total)lighting' ) == 'none'):
            if( p.value( 'raw_(total)lighting' ) == 'none'):
                no_pass = no_pass+1
                pass
            else:
                active_rawlight = True
        else:
            dot_diff = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_diff
            if first_shuffle == False:
                dot_xpos = dot_diff.xpos()
                dot_ypos = dot_diff.ypos()
                dot_diff['xpos'].setValue( dot_xpos )
                dot_diff['ypos'].setValue( dot_ypos+150 )
                xPos_diff = dot_xpos
                yPos_diff = dot_ypos
            else:
                dot_diff['xpos'].setValue( dot_xpos+place_x )
                dot_diff['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            diffNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            diffNode['in'].setValue( diffuse )
            diffNode['in2'].setValue( 'alpha' )
            diffNode['alpha'].setValue( 'alpha2' )
            diffNode['postage_stamp'].setValue( True )
            diffNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_diffNode = nuke.nodes.Unpremult(inputs=[diffNode] )
                diffNode = Un_diffNode

            dot_shuffle = nuke.nodes.Dot( inputs=[ diffNode ] )
            dot_shuffle['selected'].setValue(True)
            preserve_dot = dot_shuffle
            autoBackdrop(diffuse)
            
            dot_total = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_total
            dot_total['xpos'].setValue( dot_xpos+place_x )
            dot_total['ypos'].setValue( dot_ypos+150 )
            place_x = place_x+x_value
            totlightNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            totlightNode['in'].setValue( total_lighting )
            totlightNode['in2'].setValue( 'alpha' )
            totlightNode['alpha'].setValue( 'alpha2' )
            totlightNode['postage_stamp'].setValue( True )
            totlightNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_totlightNode = nuke.nodes.Unpremult(inputs=[totlightNode] )
                totlightNode = Un_totlightNode

            mergemult = nuke.nodes.Merge2( operation='divide', inputs=[ dot_shuffle, totlightNode ], output='rgb' )
            mergemult['selected'].setValue(True)
            dot_shuffle = mergemult
            div_diff_total = True
            first_shuffle = True
            autoBackdrop(total_lighting)
    else:
    
        if( p.value( 'raw_(total)lighting' ) == 'none'):
                no_pass = no_pass+1
                pass
        else:
                dot_raw = nuke.nodes.Dot( inputs=[ dots ] )
                dots = dot_raw
                if first_shuffle == False:
                    dot_xpos = dot_raw.xpos()
                    dot_ypos = dot_raw.ypos()
                    dot_raw['xpos'].setValue( dot_xpos )
                    dot_raw['ypos'].setValue( dot_ypos+150 )
                    xPos_raw = dot_xpos
                    yPos_raw = dot_ypos
                else:
                    dot_raw['xpos'].setValue( dot_xpos+place_x )
                    dot_raw['ypos'].setValue( dot_ypos+150 )
                    place_x = place_x+x_value   
                rawlightNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
                rawlightNode['in'].setValue( raw_lighting )
                rawlightNode['in2'].setValue( 'alpha' )
                rawlightNode['alpha'].setValue( 'alpha2' )
                rawlightNode['postage_stamp'].setValue( True )
                rawlightNode['selected'].setValue(True)
                if ( p.value( 'unpremult passes' ) == True):
                    Un_rawlightNode = nuke.nodes.Unpremult(inputs=[rawlightNode] )
                    rawlightNode = Un_rawlightNode
                dot_shuffle = nuke.nodes.Dot( inputs=[ rawlightNode ] )
                rawlightNode = dot_shuffle
                dot_shuffle['selected'].setValue(True)
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(raw_lighting)
                #shuffleLayer( node, raw_lighting )

    if( p.value( 'raw_shadow' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_rawshadow = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_rawshadow
            if first_shuffle == False:
                dot_xpos = dot_rawshadow.xpos()
                dot_ypos = dot_rawshadow.ypos()
                dot_rawshadow['xpos'].setValue( dot_xpos )
                dot_rawshadow['ypos'].setValue( dot_ypos+150 )
                xPos_rawshadow = dot_xpos
                yPos_rawshadow = dot_ypos
            else:
                dot_rawshadow['xpos'].setValue( dot_xpos+place_x )
                dot_rawshadow['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            rawshadowNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            rawshadowNode['in'].setValue( raw_shadow )
            rawshadowNode['in2'].setValue( 'alpha' )
            rawshadowNode['alpha'].setValue( 'alpha2' )
            rawshadowNode['postage_stamp'].setValue( True )
            rawshadowNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_rawshadowNode = nuke.nodes.Unpremult(inputs=[rawshadowNode] )
                rawshadowNode = Un_rawshadowNode
            if first_shuffle == True:
                    mergemult = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, rawshadowNode ], mix=0, output='rgb' )
                    dot_shuffle = mergemult
                    mergemult['selected'].setValue(True)                  
                    autoBackdrop(raw_shadow)
            else:  
                    dot_shuffle = nuke.nodes.Dot( inputs=[ rawshadowNode ] )
                    dot_shuffle['selected'].setValue(True)
                    rawshadowNode = dot_shuffle
                    dot_merge_xpos = dot_shuffle.xpos()
                    dot_merge_ypos = dot_shuffle.ypos()
                    dot_shuffle['xpos'].setValue( dot_merge_xpos )
                    dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                    first_shuffle = True
                    autoBackdrop(raw_shadow)

            #rawshadowNode = shuffleLayer( node, raw_shadow )

    if( p.value( 'diffuse' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            if div_diff_total == True:
                new_dot = nuke.nodes.Dot( inputs=[ preserve_dot ] )
                dot_merge_xpos = new_dot.xpos()
                dot_merge_ypos = new_dot.ypos()
                new_dot['xpos'].setValue( dot_merge_xpos )
                new_dot['ypos'].setValue( dot_merge_ypos+100 )
                mergemult = nuke.nodes.Merge2( operation='multiply', inputs=[ dot_shuffle, new_dot ], output='rgb' )
                dot_shuffle = mergemult
            else:
                dot_diff = nuke.nodes.Dot( inputs=[ dots ] )
                dots = dot_diff
                if first_shuffle == False:
                    dot_xpos = dot_diff.xpos()
                    dot_ypos = dot_diff.ypos()
                    dot_diff['xpos'].setValue( dot_xpos )
                    dot_diff['ypos'].setValue( dot_ypos+150 )
                    xPos_diff = dot_xpos
                    yPos_diff = dot_ypos
                else:
                    dot_diff['xpos'].setValue( dot_xpos+place_x )
                    dot_diff['ypos'].setValue( dot_ypos+150 )
                    place_x = place_x+x_value

                diffNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
                diffNode['in'].setValue( diffuse )
                diffNode['in2'].setValue( 'alpha' )
                diffNode['alpha'].setValue( 'alpha2' )
                diffNode['postage_stamp'].setValue( True )
                diffNode['selected'].setValue(True)
                if ( p.value( 'unpremult passes' ) == True):
                    Un_diffNode = nuke.nodes.Unpremult(inputs=[diffNode] )
                    diffNode = Un_diffNode
    
                if first_shuffle == True:
                        mergemult = nuke.nodes.Merge2( operation='multiply', inputs=[ dot_shuffle, diffNode ], output='rgb' )
                        dot_shuffle = mergemult
                        merge_raw_diffuse = True
                        mergemult['selected'].setValue(True)                  
                        autoBackdrop(diffuse)
                else:  
                        dot_shuffle = nuke.nodes.Dot( inputs=[ diffNode ] )
                        dot_shuffle['selected'].setValue(True)
                        diffNode = dot_shuffle
                        dot_merge_xpos = dot_shuffle.xpos()
                        dot_merge_ypos = dot_shuffle.ypos()
                        dot_shuffle['xpos'].setValue( dot_merge_xpos )
                        dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                        first_shuffle = True
                        autoBackdrop(diffuse)
                #shuffleLayer( node, diffuse )

    if( p.value( '(total)lighting' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            if div_diff_total == True:
                pass
            else:
                dot_total = nuke.nodes.Dot( inputs=[ dots ] )
                dots = dot_total
                if first_shuffle == False:
                    dot_xpos = dot_total.xpos()
                    dot_ypos = dot_total.ypos()
                    dot_total['xpos'].setValue( dot_xpos )
                    dot_total['ypos'].setValue( dot_ypos+150 )
                    xPos_total = dot_xpos
                    yPos_total = dot_ypos
                else:
                    dot_total['xpos'].setValue( dot_xpos+place_x )
                    dot_total['ypos'].setValue( dot_ypos+150 )
                    place_x = place_x+x_value
                totlightNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
                totlightNode['in'].setValue( total_lighting )
                totlightNode['in2'].setValue( 'alpha' )
                totlightNode['alpha'].setValue( 'alpha2' )
                totlightNode['postage_stamp'].setValue( True )
                totlightNode['selected'].setValue(True)
                totlightNode['selected'].setValue(True)
                if ( p.value( 'unpremult passes' ) == True):
                    Un_totlightNode = nuke.nodes.Unpremult(inputs=[totlightNode] )
                    totlightNode = Un_totlightNode
    
                if first_shuffle == True:
                        mergeplus1 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, totlightNode ], output='rgb' )
                        if merge_raw_diffuse == True:
                            mergeplus1['disable'].setValue(1)
                        dot_shuffle = mergeplus1
                        mergeplus1['selected'].setValue(True)                  
                        autoBackdrop(total_lighting)
                else:  
                        dot_shuffle = nuke.nodes.Dot( inputs=[ totlightNode ] ) 
                        dot_shuffle['selected'].setValue(True)                       
                        totlightNode = dot_shuffle
                        dot_merge_xpos = dot_shuffle.xpos()
                        dot_merge_ypos = dot_shuffle.ypos()
                        dot_shuffle['xpos'].setValue( dot_merge_xpos )
                        dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                        first_shuffle = True
                        autoBackdrop(total_lighting) 
    
                #totlightNode = shuffleLayer( node, total_lighting )


    if( p.value( 'shadow' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_shadow = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_shadow
            if first_shuffle == False:
                dot_xpos = dot_shadow.xpos()
                dot_ypos = dot_shadow.ypos()
                dot_shadow['xpos'].setValue( dot_xpos )
                dot_shadow['ypos'].setValue( dot_ypos+150 )
                xPos_shadow = dot_xpos
                yPos_shadow = dot_ypos
            else:
                dot_shadow['xpos'].setValue( dot_xpos+place_x )
                dot_shadow['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            shadowNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            shadowNode['in'].setValue( shadow )
            shadowNode['in2'].setValue( 'alpha' )
            shadowNode['alpha'].setValue( 'alpha2' )
            shadowNode['postage_stamp'].setValue( True )
            shadowNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_shadowNode = nuke.nodes.Unpremult(inputs=[shadowNode] )
                shadowNode = Un_shadowNode
            if first_shuffle == True:
                    mergeplus2 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, shadowNode ], mix=0, output='rgb')
                    dot_shuffle = mergeplus2
                    mergeplus2['selected'].setValue(True)                  
                    autoBackdrop(shadow)                   
                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ shadowNode ] )
                dot_shuffle['selected'].setValue(True)
                shadowNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(shadow)

            #shadowNode = shuffleLayer( node, shadow )

    if( p.value( 'GI' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_gi = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_gi
            
            if first_shuffle == False:
                dot_xpos = dot_gi.xpos()
                dot_ypos = dot_gi.ypos()
                dot_gi['xpos'].setValue( dot_xpos )
                dot_gi['ypos'].setValue( dot_ypos+150 )
                xPos_gi = dot_xpos
                yPos_gi = dot_ypos
            else:
                dot_gi['xpos'].setValue( dot_xpos+place_x )
                dot_gi['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            giNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            giNode['in'].setValue( gi )
            giNode['in2'].setValue( 'alpha' )
            giNode['alpha'].setValue( 'alpha2' )
            giNode['postage_stamp'].setValue( True )
            giNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_giNode = nuke.nodes.Unpremult(inputs=[giNode] )
                giNode = Un_giNode
            if first_shuffle == True:
                    mergeplus3 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, giNode ], output='rgb' )
                    dot_shuffle = mergeplus3
                    mergeplus3['selected'].setValue(True)                  
                    autoBackdrop(gi)
                            
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ giNode ] )
                dot_shuffle['selected'].setValue(True)
                giNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(gi)
    
                #giNode = shuffleLayer( node, gi )


    if( p.value( 'reflection' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_reflect = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_reflect
            if first_shuffle == False:
                dot_xpos = dot_reflect.xpos()
                dot_ypos = dot_reflect.ypos()
                dot_reflect['xpos'].setValue( dot_xpos )
                dot_reflect['ypos'].setValue( dot_ypos+150 )
                xPos_reflect = dot_xpos
                yPos_reflect = dot_ypos
            else:
                dot_reflect['xpos'].setValue( dot_xpos+place_x )
                dot_reflect['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            reflectNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            reflectNode['in'].setValue( reflection )
            reflectNode['in2'].setValue( 'alpha' )
            reflectNode['alpha'].setValue( 'alpha2' )
            reflectNode['postage_stamp'].setValue( True )
            reflectNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_reflectNode = nuke.nodes.Unpremult(inputs=[reflectNode] )
                reflectNode = Un_reflectNode
            if first_shuffle == True:
                    mergeplus4 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, reflectNode ], output='rgb' )
                    dot_shuffle = mergeplus4
                    mergeplus4['selected'].setValue(True)                                      
                    autoBackdrop(reflection)
                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ reflectNode ] )
                dot_shuffle['selected'].setValue(True)
                reflectNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(reflection)
            #reflectNode = shuffleLayer( node, reflection )

    if( p.value( 'specular' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_specular = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_specular
            if first_shuffle == False:
                dot_xpos = dot_specular.xpos()
                dot_ypos = dot_specular.ypos()
                dot_specular['xpos'].setValue( dot_xpos )
                dot_specular['ypos'].setValue( dot_ypos+150 )
                xPos_specular = dot_xpos
                yPos_specular = dot_ypos
            else:
                dot_specular['xpos'].setValue( dot_xpos+place_x )
                dot_specular['ypos'].setValue( dot_ypos+150 )
                place_x = place_x+x_value
            specNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            specNode['in'].setValue( spec )
            specNode['postage_stamp'].setValue( True )
            specNode['in2'].setValue( 'alpha' )
            specNode['alpha'].setValue( 'alpha2' )
            specNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_specNode = nuke.nodes.Unpremult(inputs=[specNode] )
                specNode = Un_specNode
            if first_shuffle == True:
                    mergeplus5 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, specNode ], output='rgb' )
                    dot_shuffle = mergeplus5
                    mergeplus5['selected'].setValue(True)                                      
                    autoBackdrop(spec)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ specNode ] )
                dot_shuffle['selected'].setValue(True)
                specNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(spec)

            #specNode = shuffleLayer( node, spec )

    if( p.value( 'refraction' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_refract = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_refract
            if first_shuffle == False:
               dot_xpos = dot_refract.xpos()
               dot_ypos = dot_refract.ypos()
               dot_refract['xpos'].setValue( dot_xpos )
               dot_refract['ypos'].setValue( dot_ypos+150 )
               xPos_refract = dot_xpos
               yPos_refract = dot_ypos
            else:
               dot_refract['xpos'].setValue( dot_xpos+place_x )
               dot_refract['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            refractNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            refractNode['in'].setValue( refraction )
            refractNode['in2'].setValue( 'alpha' )
            refractNode['alpha'].setValue( 'alpha2' )
            refractNode['postage_stamp'].setValue( True )
            refractNode['selected'].setValue(True)  
            if ( p.value( 'unpremult passes' ) == True):
                Un_refractNode = nuke.nodes.Unpremult(inputs=[refractNode] )
                refractNode = Un_refractNode
            if first_shuffle == True:
                    mergeplus6 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, refractNode ], output='rgb' )
                    dot_shuffle = mergeplus6
                    mergeplus6['selected'].setValue(True)                                      
                    autoBackdrop(refraction)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ refractNode ] )
                dot_shuffle['selected'].setValue(True)
                refractNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(refraction)
            #refractNode = shuffleLayer( node, refraction )

    if( p.value( 'subsurface' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_subsurface = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_subsurface
            if first_shuffle == False:
               dot_xpos = dot_subsurface.xpos()
               dot_ypos = dot_subsurface.ypos()
               dot_subsurface['xpos'].setValue( dot_xpos )
               dot_subsurface['ypos'].setValue( dot_ypos+150 )
               xPos_subsurface = dot_xpos
               yPos_subsurface = dot_ypos
            else:
               dot_subsurface['xpos'].setValue( dot_xpos+place_x )
               dot_subsurface['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            subsurfaceNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            subsurfaceNode['in'].setValue( subsurface )
            subsurfaceNode['postage_stamp'].setValue( True )
            subsurfaceNode['in2'].setValue( 'alpha' )
            subsurfaceNode['alpha'].setValue( 'alpha2' )
            subsurfaceNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_subsurfaceNode = nuke.nodes.Unpremult(inputs=[subsurfaceNode] )
                subsurfaceNode = Un_subsurfaceNode
            if first_shuffle == True:
                    mergeplus7 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, subsurfaceNode ], output='rgb' )
                    dot_shuffle = mergeplus7 
                    mergeplus7['selected'].setValue(True)                                      
                    autoBackdrop(subsurface)                       
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ subsurfaceNode ] )
                dot_shuffle['selected'].setValue(True)
                subsurfaceNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(subsurface)
            #subsurfaceNode = shuffleLayer( node, subsurface )

    if( p.value( 'self_illumination' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_self = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_self
            if first_shuffle == False:
               dot_xpos = dot_self.xpos()
               dot_ypos = dot_self.ypos()
               dot_self['xpos'].setValue( dot_xpos )
               dot_self['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_self['xpos'].setValue( dot_xpos+place_x )
               dot_self['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            selfNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            selfNode['in'].setValue( self_illumination )
            selfNode['in2'].setValue( 'alpha' )
            selfNode['alpha'].setValue( 'alpha2' )
            selfNode['postage_stamp'].setValue( True )
            selfNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_selfNode = nuke.nodes.Unpremult(inputs=[selfNode] )
                selfNode = Un_selfNode
            if first_shuffle == True:
                    mergeplus8 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, selfNode ], output='rgb' )
                    dot_shuffle = mergeplus8
                    mergeplus8['selected'].setValue(True)                                      
                    autoBackdrop(self_illumination)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ selfNode ] )
                dot_shuffle['selected'].setValue(True)
                selfNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(self_illumination)
            #selfNode = shuffleLayer( node, self_illumination )


    if( p.value( 'light_1' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_light1 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_light1
            if first_shuffle == False:
               dot_xpos = dot_light1.xpos()
               dot_ypos = dot_light1.ypos()
               dot_light1['xpos'].setValue( dot_xpos )
               dot_light1['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_light1['xpos'].setValue( dot_xpos+place_x )
               dot_light1['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            light1Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            light1Node['in'].setValue( light_1 )
            light1Node['in2'].setValue( 'alpha' )
            light1Node['alpha'].setValue( 'alpha2' )
            light1Node['postage_stamp'].setValue( True )
            light1Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_light1Node = nuke.nodes.Unpremult(inputs=[light1Node] )
                light1Node = Un_light1Node
            if first_shuffle == True:
                    mergeplus9 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, light1Node ], output='rgb' )
                    dot_shuffle = mergeplus9
                    mergeplus9['selected'].setValue(True)                                      
                    autoBackdrop(light_1)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ light1Node ] )
                dot_shuffle['selected'].setValue(True)
                light1Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(light_1)
            #light1Node = shuffleLayer( node, light_1 )

    if( p.value( 'light_2' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_light2 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_light2
            if first_shuffle == False:
               dot_xpos = dot_light2.xpos()
               dot_ypos = dot_light2.ypos()
               dot_light2['xpos'].setValue( dot_xpos )
               dot_light2['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_light2['xpos'].setValue( dot_xpos+place_x )
               dot_light2['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            light2Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            light2Node['in'].setValue( light_2 )
            light2Node['in2'].setValue( 'alpha' )
            light2Node['alpha'].setValue( 'alpha2' )
            light2Node['postage_stamp'].setValue( True )
            light2Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_light2Node = nuke.nodes.Unpremult(inputs=[light2Node] )
                light2Node = Un_light2Node
            if first_shuffle == True:
                    mergeplus10 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, light2Node ], output='rgb' )
                    dot_shuffle = mergeplus10
                    mergeplus10['selected'].setValue(True)                                      
                    autoBackdrop(light_2)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ light2Node ] )
                dot_shuffle['selected'].setValue(True)
                light2Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(light_2)
            #light2Node = shuffleLayer( node, light_2 )

    if( p.value( 'light_3' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_light3 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_light3
            if first_shuffle == False:
               dot_xpos = dot_light3.xpos()
               dot_ypos = dot_light3.ypos()
               dot_light3['xpos'].setValue( dot_xpos )
               dot_light3['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_light3['xpos'].setValue( dot_xpos+place_x )
               dot_light3['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            light3Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            light3Node['in'].setValue( light_3 )
            light3Node['in2'].setValue( 'alpha' )
            light3Node['alpha'].setValue( 'alpha2' )
            light3Node['postage_stamp'].setValue( True )
            light3Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_light3Node = nuke.nodes.Unpremult(inputs=[light3Node] )
                light3Node = Un_light3Node
            if first_shuffle == True:
                    mergeplus11 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, light3Node ], output='rgb' )
                    dot_shuffle = mergeplus11
                    mergeplus11['selected'].setValue(True)                                      
                    autoBackdrop(light_3)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ light3Node ] )
                dot_shuffle['selected'].setValue(True)
                light3Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(light_3)            
            #light3Node = shuffleLayer( node, light_3 )

    if( p.value( 'light_4' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_light4 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_light4
            if first_shuffle == False:
               dot_xpos = dot_light4.xpos()
               dot_ypos = dot_light4.ypos()
               dot_light4['xpos'].setValue( dot_xpos )
               dot_light4['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_light4['xpos'].setValue( dot_xpos+place_x )
               dot_light4['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            light4Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            light4Node['in'].setValue( light_4 )
            light4Node['in2'].setValue( 'alpha' )
            light4Node['alpha'].setValue( 'alpha2' )
            light4Node['postage_stamp'].setValue( True )
            light4Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_light4Node = nuke.nodes.Unpremult(inputs=[light4Node] )
                light4Node = Un_light4Node
            if first_shuffle == True:
                    mergeplus12 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, light4Node ], output='rgb' )
                    dot_shuffle = mergeplus12
                    mergeplus12['selected'].setValue(True)                                      
                    autoBackdrop(light_4)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ light4Node ] )
                dot_shuffle['selected'].setValue(True)
                light4Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(light_4)
            #light4Node = shuffleLayer( node, light_4 )

    if( p.value( 'light_5' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_light5 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_light5
            if first_shuffle == False:
               dot_xpos = dot_light5.xpos()
               dot_ypos = dot_light5.ypos()
               dot_light5['xpos'].setValue( dot_xpos )
               dot_light5['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_light5['xpos'].setValue( dot_xpos+place_x )
               dot_light5['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            light5Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            light5Node['in'].setValue( light_5 )
            light5Node['in2'].setValue( 'alpha' )
            light5Node['alpha'].setValue( 'alpha2' )
            light5Node['postage_stamp'].setValue( True )
            light5Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_light5Node = nuke.nodes.Unpremult(inputs=[light5Node] )
                light5Node = Un_light5Node
            if first_shuffle == True:
                    mergeplus13 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, light5Node ], output='rgb' )
                    dot_shuffle = mergeplus13
                    mergeplus13['selected'].setValue(True)                                      
                    autoBackdrop(light_5)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ light5Node ] )
                dot_shuffle['selected'].setValue(True)
                light5Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(light_5)
            #light5Node = shuffleLayer( node, light_5 )


    if( p.value( 'ID_1' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_id1 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_id1
            if first_shuffle == False:
               dot_xpos = dot_id1.xpos()
               dot_ypos = dot_id1.ypos()
               dot_id1['xpos'].setValue( dot_xpos )
               dot_id1['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_id1['xpos'].setValue( dot_xpos+place_x )
               dot_id1['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            id1Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            id1Node['in'].setValue( ID_1 )
            id1Node['in2'].setValue( 'alpha' )
            id1Node['alpha'].setValue( 'alpha2' )
            id1Node['postage_stamp'].setValue( True )
            id1Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_id1Node = nuke.nodes.Unpremult(inputs=[id1Node] )
                id1Node = Un_id1Node
            if first_shuffle == True:
                    mergeplus14 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, id1Node ], output='rgb' )
                    mergeplus14['disable'].setValue(1)
                    dot_shuffle = mergeplus14
                    mergeplus14['selected'].setValue(True)                                      
                    autoBackdrop(ID_1)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ id1Node ] )
                dot_shuffle['selected'].setValue(True)
                id1Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(ID_1)

            #id1Node = shuffleLayer( node, ID_1 )

    if( p.value( 'ID_2' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_id2 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_id2
            if first_shuffle == False:
               dot_xpos = dot_id2.xpos()
               dot_ypos = dot_id2.ypos()
               dot_id2['xpos'].setValue( dot_xpos )
               dot_id2['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_id2['xpos'].setValue( dot_xpos+place_x )
               dot_id2['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            id2Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            id2Node['in'].setValue( ID_2 )
            id2Node['in2'].setValue( 'alpha' )
            id2Node['alpha'].setValue( 'alpha2' )
            id2Node['postage_stamp'].setValue( True )
            id2Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_id2Node = nuke.nodes.Unpremult(inputs=[id2Node] )
                id2Node = Un_id2Node
            if first_shuffle == True:
                    mergeplus15 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, id2Node ], output='rgb' )
                    mergeplus15['disable'].setValue(1)
                    dot_shuffle = mergeplus15
                    mergeplus15['selected'].setValue(True)                                      
                    autoBackdrop(ID_2)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ id2Node ] )
                dot_shuffle['selected'].setValue(True)
                id2Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(ID_2)

            #id2Node = shuffleLayer( node, ID_2 )

    if( p.value( 'ID_3' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_id3 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_id3
            if first_shuffle == False:
               dot_xpos = dot_id3.xpos()
               dot_ypos = dot_id3.ypos()
               dot_id3['xpos'].setValue( dot_xpos )
               dot_id3['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_id3['xpos'].setValue( dot_xpos+place_x )
               dot_id3['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            id3Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            id3Node['in'].setValue( ID_3 )
            id3Node['in2'].setValue( 'alpha' )
            id3Node['alpha'].setValue( 'alpha2' )
            id3Node['postage_stamp'].setValue( True )
            id3Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_id3Node = nuke.nodes.Unpremult(inputs=[id3Node] )
                id3Node = Un_id3Node
            if first_shuffle == True:
                    mergeplus16 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, id3Node ], output='rgb' )
                    mergeplus16['disable'].setValue(1)
                    dot_shuffle = mergeplus16
                    mergeplus16['selected'].setValue(True)                                      
                    autoBackdrop(ID_3)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ id3Node ] )
                dot_shuffle['selected'].setValue(True)
                id3Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(ID_3)

            #id3Node = shuffleLayer( node, ID_3 )

    if( p.value( 'ID_4' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_id4 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_id4
            if first_shuffle == False:
               dot_xpos = dot_id4.xpos()
               dot_ypos = dot_id4.ypos()
               dot_id4['xpos'].setValue( dot_xpos )
               dot_id4['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_id4['xpos'].setValue( dot_xpos+place_x )
               dot_id4['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            id4Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            id4Node['in'].setValue( ID_4 )
            id4Node['in2'].setValue( 'alpha' )
            id4Node['alpha'].setValue( 'alpha2' )
            id4Node['postage_stamp'].setValue( True )
            id4Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_id4Node = nuke.nodes.Unpremult(inputs=[id4Node] )
                id4Node = Un_id4Node
            if first_shuffle == True:
                    mergeplus17 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, id4Node ], output='rgb' )
                    mergeplus17['disable'].setValue(1)
                    dot_shuffle = mergeplus17
                    mergeplus17['selected'].setValue(True)                                      
                    autoBackdrop(ID_4)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ id4Node ] )
                dot_shuffle['selected'].setValue(True)
                id4Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(ID_4)
            

            #id4Node = shuffleLayer( node, ID_4 )
    
    if( p.value( 'ID_5' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_id5 = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_id5
            if first_shuffle == False:
               dot_xpos = dot_id5.xpos()
               dot_ypos = dot_id5.ypos()
               dot_id5['xpos'].setValue( dot_xpos )
               dot_id5['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_id5['xpos'].setValue( dot_xpos+place_x )
               dot_id5['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            id5Node = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            id5Node['in'].setValue( ID_5 )
            id5Node['in2'].setValue( 'alpha' )
            id5Node['alpha'].setValue( 'alpha2' )
            id5Node['postage_stamp'].setValue( True )
            id5Node['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_id5Node = nuke.nodes.Unpremult(inputs=[id5Node] )
                id5Node = Un_id5Node
            if first_shuffle == True:
                    mergeplus18 = nuke.nodes.Merge2( operation='plus', inputs=[ dot_shuffle, id5Node ], output='rgb' )
                    mergeplus18['disable'].setValue(1)
                    dot_shuffle = mergeplus18
                    mergeplus18['selected'].setValue(True)                                      
                    autoBackdrop(ID_5)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ id5Node ] )
                dot_shuffle['selected'].setValue(True)
                id5Node = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(ID_5)

            #id5Node = shuffleLayer( node, ID_5 )


    if( p.value( 'amb_occlusion' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_occlusion = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_occlusion
            if first_shuffle == False:
               dot_xpos = dot_occlusion.xpos()
               dot_ypos = dot_occlusion.ypos()
               dot_occlusion['xpos'].setValue( dot_xpos )
               dot_occlusion['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_occlusion['xpos'].setValue( dot_xpos+place_x )
               dot_occlusion['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            amb_occlusionNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            amb_occlusionNode['in'].setValue( amb_occlusion )
            amb_occlusionNode['in2'].setValue( 'alpha' )
            amb_occlusionNode['alpha'].setValue( 'alpha2' )
            amb_occlusionNode['postage_stamp'].setValue( True )
            amb_occlusionNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_amb_occlusionNode = nuke.nodes.Unpremult(inputs=[amb_occlusionNode] )
                amb_occlusionNode = Un_amb_occlusionNode
            if first_shuffle == True:
                    mergeplus19 = nuke.nodes.Merge2( operation='multiply', inputs=[ dot_shuffle, amb_occlusionNode ], output='rgb' )
                    dot_shuffle = mergeplus19
                    mergeplus19['selected'].setValue(True)                                      
                    autoBackdrop(amb_occlusion)                        
            else:  
                dot_shuffle = nuke.nodes.Dot( inputs=[ amb_occlusionNode ] )
                dot_shuffle['selected'].setValue(True)
                amb_occlusionNode = dot_shuffle
                dot_merge_xpos = dot_shuffle.xpos()
                dot_merge_ypos = dot_shuffle.ypos()
                dot_shuffle['xpos'].setValue( dot_merge_xpos )
                dot_shuffle['ypos'].setValue( dot_merge_ypos+100 )
                first_shuffle = True
                autoBackdrop(amb_occlusion)
            #amb_occlusionNode = shuffleLayer( node, amb_occlusion )

    if( p.value( 'normals' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_normals = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_normals
            if first_shuffle == False:
               dot_xpos = dot_normals.xpos()
               dot_ypos = dot_normals.ypos()
               dot_normals['xpos'].setValue( dot_xpos )
               dot_normals['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_normals['xpos'].setValue( dot_xpos+place_x )
               dot_normals['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            normalsNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            normalsNode['in'].setValue( normals )
            normalsNode['in2'].setValue( 'alpha' )
            normalsNode['alpha'].setValue( 'alpha2' )
            normalsNode['postage_stamp'].setValue( True )
            normalsNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_normalsNode = nuke.nodes.Unpremult(inputs=[normalsNode] )
                normalsNode = Un_normalsNode 
            dot_shuffle_normals = nuke.nodes.Dot( inputs=[ normalsNode ] )
            dot_shuffle_normals['selected'].setValue(True)
            normalsNode = dot_shuffle_normals
            dot_merge_xpos = dot_shuffle_normals.xpos()
            dot_merge_ypos = dot_shuffle_normals.ypos()
            dot_shuffle_normals['xpos'].setValue( dot_merge_xpos )
            dot_shuffle_normals['ypos'].setValue( dot_merge_ypos+100 )
            first_shuffle = True
            autoBackdrop(normals)

            #normalsNode = shuffleLayer( node, normals )

    if( p.value( 'position' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_position = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_position
            if first_shuffle == False:
               dot_xpos = dot_position.xpos()
               dot_ypos = dot_position.ypos()
               dot_position['xpos'].setValue( dot_xpos )
               dot_position['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_position['xpos'].setValue( dot_xpos+place_x )
               dot_position['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            positionNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            positionNode['in'].setValue( position )
            positionNode['postage_stamp'].setValue( True )
            positionNode['in2'].setValue( 'alpha' )
            positionNode['alpha'].setValue( 'alpha2' )
            positionNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_positionNode = nuke.nodes.Unpremult(inputs=[positionNode] )
                positionNode = Un_positionNode
            dot_shuffle_position = nuke.nodes.Dot( inputs=[ positionNode ] )
            dot_shuffle_position['selected'].setValue(True)
            positionNode = dot_shuffle_position
            dot_merge_xpos = dot_shuffle_position.xpos()
            dot_merge_ypos = dot_shuffle_position.ypos()
            dot_shuffle_position['xpos'].setValue( dot_merge_xpos )
            dot_shuffle_position['ypos'].setValue( dot_merge_ypos+100 )
            first_shuffle = True
            autoBackdrop(position)
            #positionNode = shuffleLayer( node, position )

    if( p.value( 'depth' ) == 'none'):
            no_pass = no_pass+1
            pass
    else:
            dot_depth = nuke.nodes.Dot( inputs=[ dots ] )
            dots = dot_depth
            if first_shuffle == False:
               dot_xpos = dot_depth.xpos()
               dot_ypos = dot_depth.ypos()
               dot_depth['xpos'].setValue( dot_xpos )
               dot_depth['ypos'].setValue( dot_ypos+150 )
               xPos_self = dot_xpos
               yPos_self = dot_ypos
            else:
               dot_depth['xpos'].setValue( dot_xpos+place_x )
               dot_depth['ypos'].setValue( dot_ypos+150 )
               place_x = place_x+x_value
            depthNode = nuke.nodes.Shuffle( label=knob, inputs=[dots] )
            depthNode['in'].setValue( depth )
            depthNode['in2'].setValue( 'alpha' )
            depthNode['alpha'].setValue( 'alpha2' )
            depthNode['postage_stamp'].setValue( True )
            depthNode['selected'].setValue(True)
            if ( p.value( 'unpremult passes' ) == True):
                Un_depthNode = nuke.nodes.Unpremult(inputs=[depthNode] )
                depthNode = Un_depthNode
            dot_shuffle_depth = nuke.nodes.Dot( inputs=[ depthNode ] )
            dot_shuffle_depth['selected'].setValue(True)
            depthNode = dot_shuffle_depth
            dot_merge_xpos = dot_shuffle_depth.xpos()
            dot_merge_ypos = dot_shuffle_depth.ypos()
            dot_shuffle_depth['xpos'].setValue( dot_merge_xpos )
            dot_shuffle_depth['ypos'].setValue( dot_merge_ypos+100 )
            first_shuffle = True
            autoBackdrop(depth)

            #depthNode = shuffleLayer( node, depth )





    if ( p.value( 'create new alpha copy' ) == True): 
        if no_pass == 25:
            nuke.delete(main_dot)
            nuke.delete(copyalpha)  

    if ( p.value( 'create new alpha copy' ) == False): 
        if no_pass == 25:
            nuke.delete(main_dot) 

    if ( p.value( 'create new alpha copy' ) == True): 
        if no_pass == 24 and active_rawlight == True:
            nuke.delete(main_dot)
            nuke.delete(copyalpha)
    
    if copied == True and no_pass !=25:
        try:
            copyalpha2 = nuke.nodes.Copy(inputs=[dot_shuffle, dot_shuffle] )
            copyalpha2['from0'].setValue( alpha_copy )
            copyalpha2['to0'].setValue( 'rgba.alpha' )
            copy2_xpos = copyalpha2.xpos()
            copy2_ypos = copyalpha2.ypos()
            copyalpha2['xpos'].setValue( copy2_xpos )
            copyalpha2['ypos'].setValue( copy2_ypos+150 )
            premultNode = nuke.nodes.Premult(inputs=[copyalpha2])
            premultNode_ypos = premultNode.ypos()
            premultNode['ypos'].setValue( premultNode_ypos+25 )
            copyalpha2['selected'].setValue(True)  
            premultNode['selected'].setValue(True)                
            autoBackdrop(restore_alpha)
            
        except:
            pass

def start():
    autocomper()








 




