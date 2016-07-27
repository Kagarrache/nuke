# Despill Edges 
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
# m.addCommand("Color/despillEdges", "nuke.createNode('despillEdges')")

def despillEdges_Evaluate():
	#
	# sample colors from source and despilled plate to get RGB values at picker positions
	#
	# Sample despilled  Multiplier = 1 1 1
	# reset multiplyer before testing
	nuke.toNode('GradeDespill')['multiply'].setValue((1,1,1,0))
	nuke.thisNode()['cp'].setValue((nuke.toNode('DefaultDespil').sample('red', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1]),nuke.nuke.toNode('DefaultDespil').sample('green', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1]),nuke.nuke.toNode('DefaultDespil').sample('blue', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1])))

	# Sample source

	nuke.thisNode()['cp1'].setValue((nuke.toNode('SourceColor').sample('red', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1]),nuke.toNode('SourceColor').sample('green', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1]),nuke.toNode('SourceColor').sample('blue', nuke.thisNode()['pos'].value()[0], nuke.thisNode()['pos'].value()[1])))

	smp=nuke.thisNode()['cp'].value()
	smp1=nuke.thisNode()['cp1'].value()
	
	# set min and max knobs values. helpful for debug
	# RGB values at smp[0] smp[1] smp[2]

	nuke.thisNode()['minCol'].setValue((smp[0]<min(smp[1],smp[2]),smp[1]<min(smp[0],smp[2]),smp[2]<min(smp[1],smp[0])))
	nuke.thisNode()['minColA'].setValue((smp[0]==min(smp[0],smp[2]),0,smp[2]==min(smp[0],smp[2])))
	
	if nuke.thisNode()['spillColor'].value()==0:
		maxVal=max(smp1[0],smp1[2])
		nuke.thisNode()['maxVal'].setValue( maxVal )
		nuke.thisNode()['minVal'].setValue( min(smp1[0],smp1[2]) )
		
	else:
		maxVal=max(smp1[0],smp1[1])
		nuke.thisNode()['maxVal'].setValue( maxVal )
		nuke.thisNode()['minVal'].setValue( min(smp1[0],smp1[1]) )
		
	#maxVal=nuke.thisNode()['minColA'].value()
	# set min and max knobs values. helpful for debug
	
	# Evaluate Multipliers 
	
	wt = nuke.toNode('WeightedAverage')['which'].value()
	
	if nuke.thisNode()['spillColor'].value()==0:
		avg =smp1[0]*(1-wt)+smp1[2]*(wt)
	else:
		avg =smp1[0]*(1-wt)+smp1[1]*(wt)
	
	# Checking which one is smaller R or B and setting max value Multiplier to 0. So for ex. if R >B then Xr =0 if B > R then Xb=0
	# examples for green spill colour
	# for B =>  R>B?(R-B)/(G - avg)
	# for G => (G-B)/(G - avg)
	if nuke.thisNode()['spillColor'].value()==0:
		# RED 
		if (smp[0]>smp[2]):
			Xr=0
		else:
			Xr=(maxVal-smp1[0])/(smp1[1] - avg)
		
		# BLUE
		if (smp[0]<smp[2]):
			Xb=0
		else:
			Xb=(maxVal-smp1[2])/(smp1[1] - avg)
		
		# GREEN
		Xg = (smp1[1]-maxVal)/(smp1[1] - avg)
	
	else:
		# RED 
		if (smp[0]>smp[1]):
			Xr=0
		else:
			Xr=(maxVal-smp1[0])/(smp1[2] - avg)
		
		# Green
		if (smp[0]<smp[1]):
			Xg=0
		else:
			Xg=(maxVal-smp1[1])/(smp1[2] - avg)
		
		# Blue
		Xb = (smp1[2]-maxVal)/(smp1[2] - avg)
	# Set Grade to neutral colors
	nuke.toNode('GradeDespill')['multiply'].setValue((Xr,Xg,Xb,0))


def despillEdges_Reset():
	# Reset grade to defaults same default color at the moment. Might be changed later.
	#
	if nuke.thisNode()['spillColor'].value()==0:
		nuke.toNode('GradeDespill')['multiply'].setValue((1,1,1,0))
	else:
		nuke.toNode('GradeDespill')['multiply'].setValue((1,1,1,0))


# knob visibility changes here

def despillEdges_knobChanged():
	n=nuke.thisNode()
	k=nuke.thisKnob()
	if k.name() == 'method':
	    if k.value()=='Subtract Luma':
			n['enableEdgeBias'].setVisible(True)
			n['spillBiasEdge'].setVisible(n['enableEdgeBias'].value())
			n['tuneLuma'].setVisible(True)
			n['bgMix'].setVisible(True)
			n['coreWeight'].setVisible(True)
			n['bgHighlights'].setVisible(True)
			n['stepbystepSub'].setVisible(True)
			n['stepbystepKey'].setVisible(False)
			n['screenColour'].setVisible(False)
			n['screenBalance'].setVisible(False)
			n['bgGrade'].setVisible(False)
			n['keylightLumahelper'].setVisible(False)
	    else:
			n['enableEdgeBias'].setVisible(False)
			n['spillBiasEdge'].setVisible(False)
			n['tuneLuma'].setVisible(False)
			n['bgMix'].setVisible(False)
			n['coreWeight'].setVisible(False)
			n['bgHighlights'].setVisible(False)
			n['stepbystepSub'].setVisible(False)
			n['stepbystepKey'].setVisible(True)
			n['screenColour'].setVisible(True)
			n['screenBalance'].setVisible(True)
			n['bgGrade'].setVisible(True)
			n['keylightLumahelper'].setVisible(True)

	
	if k.name() == 'showLumaMask':
		n['showLumaMaskB'].setValue(n['showLumaMask'].value())
	
	if k.name() == 'showLumaMaskB':
		n['showLumaMask'].setValue(n['showLumaMaskB'].value())
	
	if k.name() == 'enableEdgeBias':
	    if k.value()==1:
			n['spillBiasEdge'].setVisible(True)
	    else:
			n['spillBiasEdge'].setVisible(False)
