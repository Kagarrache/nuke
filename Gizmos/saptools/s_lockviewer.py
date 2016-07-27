import nuke

class LockViewer:

	selNodesLs = [None]*10
	
	def lockInput(self,lockBool,connectionInput,viewerNode,connectNode):
		viewer = viewerNode
		
		for i in range(10):
			if not viewer.knob('locked%d' %i):
				k = nuke.Boolean_Knob('locked%d' %i, 'locked%d' %i, False)
				k.setFlag(nuke.INVISIBLE)
				viewer.addKnob(k)

		viewer['locked%d' %connectionInput].setValue(lockBool)
				
		if viewer['locked%d' %connectionInput].value():
			self.selNodesLs[connectionInput] = connectNode
			viewer.setInput(connectionInput, self.selNodesLs[connectionInput])
				
		#GUI
		strText = "Locked "
		textBool = False
		for s in range(10):
			if viewer['locked%d' %s].value():
				strText += str(s+1)
				strText += ','
				textBool = True
				
		if textBool:
			viewer['label'].setValue(strText[:-1])
			viewer['tile_color'].setValue(640034559)
		else:
			viewer['label'].setValue('')
			viewer['tile_color'].setValue(0)
			
		#Callback
		def knobChangedCallback():
			if nuke.thisKnob().name() == 'inputChange':
				for i in range(10):
					if viewer['locked%d' %i].value():
						viewer.setInput(i,self.selNodesLs[i])

		
		nuke.addKnobChanged(knobChangedCallback,nodeClass='Viewer')