# by Simon Moreau
# visualprocess.blogspot.com

import nuke

def imagePlane() :
	cam = nuke.selectedNode()
	x = cam['xpos'].value()
	y = cam['ypos'].value()
	card = nuke.createNode("Card")
	card['xpos'].setValue(x+150)
	card['ypos'].setValue(x)
	transGeo = nuke.createNode("TransformGeo")
	transGeo['xpos'].setValue(x+150)
	transGeo['ypos'].setValue(x+50)
	transGeo.setInput(1, cam)
	transGeo.setInput(0, card)
	card.knob("lens_in_focal").setExpression("parent." + cam.name() + ".focal")
	card.knob("lens_in_haperture").setExpression("parent." + cam.name() + ".haperture")
	card['z'].setValue(100)