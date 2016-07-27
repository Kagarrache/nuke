from PySide import QtGui, QtCore
import math
import os
import nuke, nukescripts



#keep this out as looks like nuke is not refreshing the geo otherwise
def getPoints():
    P=[]
    for v in nukescripts.snap3d.selectedPoints():
        P.append(v)
    return P


class LocoWidget(QtGui.QWidget):
    def __init__(self):
        super(LocoWidget,self).__init__()

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Locometry v2.1')
        self.header = QtGui.QPixmap(os.path.split(__file__)[0]+'/icons/logo.png')
        self.headerLBL = QtGui.QLabel()
        self.headerLBL.setPixmap(self.header)
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.addWidget(self.headerLBL)
        
        
        self.typeCombo = QtGui.QComboBox()
        self.typeCombo.addItems(['Axis','Card','Sphere','Cube','Cylinder','Selected Node'])
        self.frangeLBL = QtGui.QLabel('Frame Range')
        self.firstLE = QtGui.QLineEdit()
        self.lastLE = QtGui.QLineEdit()
        self.trackBTN = QtGui.QPushButton('snap')
        
        
        self.locoDic = {}
        
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(100)
        self.progressBar.setFormat('Snapping '+self.typeCombo.currentText())
        
        self.progressBar.setObjectName("progressBar")
        
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.typeCombo)
        self.layout.addWidget(self.frangeLBL)
        self.layout.addWidget(self.firstLE)
        self.layout.addWidget(self.lastLE)
        self.layout.addWidget(self.trackBTN)
        
        
        self.vLayout.addLayout(self.layout)
        self.vLayout.addWidget(self.progressBar)
        self.progressBar.hide()
        
        self.setLayout(self.vLayout)
        self.locoThread = None
        
        self.trackBTN.clicked.connect(self.trackSelectedVertices)

    def setProgress(self, progress):
    
        self.progressBar.setValue(progress)
        if self.progressBar.value()==100:
            self.progressBar.setValue(0)
            self.progressBar.hide()

    def trackSelectedVertices(self):
        if isinstance(int(self.firstLE.text()),int) and isinstance(int(self.lastLE.text()),int):
            
            self.trackBTN.setEnabled(False)
            self.typeCombo.setEnabled(False)
            self.locoThread = LocoThread(int(self.firstLE.text()),int(self.lastLE.text()), self.typeCombo.currentText(), self)
            self.locoThread.updateProgress.connect(self.setProgress)
            self.progressBar.setFormat('Snapping '+self.typeCombo.currentText())
            self.progressBar.show()
            self.locoThread.start()

class LocoThread(QtCore.QThread):

    updateProgress = QtCore.Signal(int)

    def __init__(self, first, last, node, gui):

        QtCore.QThread.__init__(self)

        self.first = first
        self.last = last
        self.node = node
        self.gui = gui
    
    
    def run(self):

        
        nodeToSnap = None
        if self.node == 'Axis':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.createNode,'Axis2')
        elif self.node == 'Card':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.createNode,'Card2')
        elif self.node == 'Sphere':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.createNode,'Sphere')
        elif self.node == 'Cube':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.createNode,'Cube')
        elif self.node == 'Cylinder':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.createNode,'Cylinder')
        elif self.node == 'Selected Node':
            nodeToSnap = nuke.executeInMainThreadWithResult(nuke.selectedNode,())


        nuke.executeInMainThreadWithResult(nodeToSnap['translate'].setAnimated,())

        nuke.executeInMainThreadWithResult(nodeToSnap['rotate'].setAnimated,())

        nuke.executeInMainThreadWithResult(nodeToSnap['rot_order'].setValue,(0))

        
        for frame in range(self.first,self.last+1):
            
            nuke.executeInMainThreadWithResult(nuke.frame,frame)
            P=nuke.executeInMainThreadWithResult(getPoints,())
            
            A = P[1] - P[0]
            B = P[2] - P[0]

            A.normalize()

            N = A.cross(B) #create the normal of A and B

            N.normalize()

            C = N.cross(A) #create the orthogonal axis

            centroid = (P[0]+P[1]+P[2])/3

            #generate the Rotation Matrix Colums
            r11 = A[0]
            r21 = A[1]
            r31 = A[2]
            r12 = C[0]
            r22 = C[1]
            r32 = C[2]
            r13 = N[0]
            r23 = N[1]
            r33 = N[2]

            #generate Euler Angles
            rx=math.atan2(r32,r33)
            ry=math.atan2(-r31,math.sqrt( r32**2 + r33**2))
            rz=math.atan2(r21,r11)
            
            # set the knobs
            nuke.executeInMainThreadWithResult(nodeToSnap['translate'].setValue,[centroid[0],centroid[1],centroid[2]])
            nuke.executeInMainThreadWithResult(nodeToSnap['rotate'].setValue,[math.degrees(rx),math.degrees(ry),math.degrees(rz)])
            self.updateProgress.emit((float(frame)/self.last*100))

        nuke.executeInMainThreadWithResult(nuke.frame,self.first)
        self.gui.trackBTN.setEnabled(True)
        self.gui.typeCombo.setEnabled(True)
            





