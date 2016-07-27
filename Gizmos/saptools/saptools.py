import nuke
from s_lockviewer import LockViewer

m = nuke.menu('Nodes').addMenu('Sap Tools', icon = "saptools.png")

m.addCommand( 's_PointsToCornerPin', lambda: nuke.createNode( 's_PointsToCornerPin' ), icon = 's_PointsToCornerPin.png' )
m.addCommand( 's_TrackReformat', lambda: nuke.createNode( 's_TrackReformat' ), icon = 's_TrackReformat.png' )
m.addCommand( 's_MaskedBlur', lambda: nuke.createNode( 's_MaskedBlur' ), icon = 's_MaskedBlur.png' )

### Lockviewer
l = LockViewer()

def onScriptLoadCallback():
	for n in nuke.allNodes():
		if n.Class() == "Viewer":
			if n.knob('locked0'):
				for i in range(10):
					if n.input(i) != None:
						l.lockInput(True, i, n, n.input(i))

nuke.addOnScriptLoad(onScriptLoadCallback)

m = nuke.menu( 'Nuke' ).addMenu('Sap Tools')
subm = m.addMenu('Lock Selected Node to Viewer')
subm.addCommand( 'lockViewer1', lambda: l.lockInput(True,0,nuke.activeViewer().node(),nuke.selectedNode()), '#1')
subm.addCommand( 'unlockViewer1', lambda: l.lockInput(False,0,nuke.activeViewer().node(),None), '^#1')
subm.addCommand( 'lockViewer2', lambda: l.lockInput(True,1,nuke.activeViewer().node(),nuke.selectedNode()), '#2')
subm.addCommand( 'unlockViewer2', lambda: l.lockInput(False,1,nuke.activeViewer().node(),None), '^#2')
subm.addCommand( 'lockViewer3', lambda: l.lockInput(True,2,nuke.activeViewer().node(),nuke.selectedNode()), '#3')
subm.addCommand( 'unlockViewer3', lambda: l.lockInput(False,2,nuke.activeViewer().node(),None), '^#3')
subm.addCommand( 'lockViewer4', lambda: l.lockInput(True,3,nuke.activeViewer().node(),nuke.selectedNode()), '#4')
subm.addCommand( 'unlockViewer4', lambda: l.lockInput(False,3,nuke.activeViewer().node(),None), '^#4')
subm.addCommand( 'lockViewer5', lambda: l.lockInput(True,4,nuke.activeViewer().node(),nuke.selectedNode()), '#5')
subm.addCommand( 'unlockViewer5', lambda: l.lockInput(False,4,nuke.activeViewer().node(),None), '^#5')
subm.addCommand( 'lockViewer6', lambda: l.lockInput(True,5,nuke.activeViewer().node(),nuke.selectedNode()), '#6')
subm.addCommand( 'unlockViewer6', lambda: l.lockInput(False,5,nuke.activeViewer().node(),None), '^#6')
subm.addCommand( 'lockViewer7', lambda: l.lockInput(True,6,nuke.activeViewer().node(),nuke.selectedNode()), '#7')
subm.addCommand( 'unlockViewer7', lambda: l.lockInput(False,6,nuke.activeViewer().node(),None), '^#7')
subm.addCommand( 'lockViewer8', lambda: l.lockInput(True,7,nuke.activeViewer().node(),nuke.selectedNode()), '#8')
subm.addCommand( 'unlockViewer8', lambda: l.lockInput(False,7,nuke.activeViewer().node(),None), '^#8')
subm.addCommand( 'lockViewer9', lambda: l.lockInput(True,8,nuke.activeViewer().node(),nuke.selectedNode()), '#9')
subm.addCommand( 'unlockViewer9', lambda: l.lockInput(False,8,nuke.activeViewer().node(),None), '^#9')
subm.addCommand( 'lockViewer10', lambda: l.lockInput(True,9,nuke.activeViewer().node(),nuke.selectedNode()), '#0')
subm.addCommand( 'unlockViewer10', lambda: l.lockInput(False,9,nuke.activeViewer().node(),None), '^#0')