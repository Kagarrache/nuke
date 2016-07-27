'''
DAG Panel

create a picture with dots inside the nodegraph sampling a read node or any other node inside the pipe 
by falk Hofmann 2013
Falk@Kombinat-13b.de

import DAGPanel
menu=nuke.menu("Nuke")
mb=menu.addMenu( "Custom Menu" )
mb.addCommand ( "DAG Panel", 'DAGPanel.check()' )
'''


import nuke
def check():
    sel=nuke.selectedNode() 
    width = sel.width()
    height = sel.height()
    question = 'this is very heavy computing \n I highly recommend to use a small format such as 50x50  \n\n your current format is %sx%s \n\n continue?'%(width,height)
    if nuke.ask(question):
        draw(sel, width,height)

def draw(sel, width,height):
    px = width*height
    selX = sel ['xpos' ] .value()
    selY = sel ['ypos' ] .value()
    tempPosX = selX + 100
    tempPosY = selY
    x = 0
    y = 0
    for i in xrange ((px-1) + width ) :
        if x < width:
            n = nuke.nodes.Dot ( xpos = tempPosX, ypos = tempPosY )
            n [ 'hide_input' ] .setValue (True)
    
            r = max (0, sel.sample ( 'red', x, y ))
            g = max (0, sel.sample ( 'green', x, y ))
            b = max (0,sel.sample ( 'blue', x, y ))

            hexColor = int ( '%02x%02x%02x%02x' % (r*255, g*255, b*255, 1 ), 16 ) 
            n [ 'tile_color' ] .setValue ( hexColor )
            
            tempPosX = tempPosX + 10
            x = x +1
    
        elif x == width:            
            x = 0
            y = y + 1
            tempPosX = selX + 100
            tempPosY = tempPosY - 10