#
# chTextPlus
# allows to animate text on a per character level
# Timur Khodzhaev 2013
# www.chimuru.com
#
##############################################
#
# Installation:
#
# menubar=nuke.menu("Nuke")
# m=menubar.addMenu("chTools")
#
# m.addCommand("Animation/Text Plus", "nuke.createNode('chTextPlus.gizmo')")

import threading

def chTP_refresh():

# Cleanup
	
	all=nuke.allNodes()
	for i in all:
		if i.name().split('_')[0]=='chSub':
			nuke.delete(i)
	
# Create new nodes		
	prevLetterWidth=0
	
# Creating task	
	task = nuke.ProgressTask("Generating letters")
		
	for i in range(0,len(nuke.thisNode().input(0)['message'].getValue())):
	
		if task.isCancelled():
			nuke.executeInMainThread( nuke.message, args=( "Generation of letters canceled!" ) )
			break;
		task.setProgress((100*len(nuke.thisNode().input(0)['message'].getValue())+1)/(i+1))

		nukescripts.clear_selection_recursive() 
		
		letter = nuke.thisNode().input(0)['message'].getValue()[i]
		
		task.setMessage("Creating :"+letter)
		
		if letter not in [' ','/n']:
			n=nuke.createNode('Text',inpanel=False)
			n['name'].setValue('chSub_'+str(i))
			n['message'].setValue(letter)
			n['xpos'].setValue(i*150)
			n['ypos'].setValue(0)
			
			n['size'].setExpression('parent.font_size')
			n['kerning'].setExpression('parent.kerning')
			n['box'].setExpression('parent.box')
			n['translate'].setExpression('parent.translate')
			n['rotate'].setExpression('parent.rotate')
			n['scale'].setExpression('parent.scale')
			n['skewX'].setExpression('parent.skewX')
			n['skewY'].setExpression('parent.skewY')
			n['center'].setExpression('parent.center')
			
			t=nuke.createNode('Transform',inpanel=False)
			t['name'].setValue('chSub_Translate_'+str(i))

	#		Positioning Letters
	#		if i>1:		

			t['translate'].setExpression(str(prevLetterWidth)+'+parent.p_translate',0)
			t['translate'].setExpression('parent.p_translate',1)
			t['rotate'].setExpression('parent.p_rotate')
			t['scale'].setExpression('parent.p_scale')
			t['center'].setExpression('[python {nuke.thisNode().input(0).bbox().w()/2+nuke.thisNode().input(0).bbox().x()}]',0)
			t['center'].setExpression('[python {nuke.thisNode().input(0).bbox().h()/2+nuke.thisNode().input(0).bbox().y()}]',1)
			#'nuke.thisNode().input(0)['translate'].getValue()[1]')
			
			prevLetterWidth=prevLetterWidth+n.bbox().w()
			t.setInput(0,n)

			b=nuke.createNode('Blur',inpanel=False)
			b['name'].setValue('chSub_Blur_'+str(i))
			b['size'].setValue((0,0))
			b['size'].setExpression('parent.size')
			b.setInput(0,t)
			
			o=nuke.createNode('Multiply',inpanel=False)
			o['name'].setValue('chSub_Multiply_'+str(i))
			o['value'].setExpression('parent.opacity')
			o.setInput(0,b)

			to=nuke.createNode('TimeOffset',inpanel=False)
			to['name'].setValue('chSub_TimeOffset_'+str(i))
			to.setInput(0,o)
			chNodeNum = nuke.Int_Knob('chNodeNum','NodeNumber',0)
			to.addKnob(chNodeNum)
			to['chNodeNum'].setExpression('[python {nuke.thisNode().name().split("_")[2]}]')
			to['time_offset'].setExpression('parent.animation?random(chNodeNum*parent.seed)*parent.timeoffset:chNodeNum*parent.timeoffset')
			
			nmrg=nuke.createNode('Merge',inpanel=False)
			nmrg['name'].setValue('chSub_Merge_'+str(i))
			if i>0:
				nmrg.setInput(1,lastMerge)
			lastMerge=nmrg
					
		else:
			prevLetterWidth=prevLetterWidth+nuke.thisNode()['font_size'].getValue()/3
			
	n=nuke.toNode('Switch')
	n.setInput(1,nmrg)
	