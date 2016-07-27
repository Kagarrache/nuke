import os
import sys
import nuke
import nukescripts

def makeShotDir():

    shotNameKnobs = [0]
    shotPathKnobs = [0]

    class shotFolderPanel(nukescripts.PythonPanel):
    
        q = nuke.Panel('Number of Shots')
        q.addSingleLineInput('number of shots', '1')
        ret = q.show()
        numshots = int(q.value('number of shots'))
    
        def __init__(self):
            nukescripts.PythonPanel.__init__(self, 'Create Shot Directories')
            num = 1
            self.jobKnobName = nuke.Text_Knob('folder to create shots')
            self.jobKnob = nuke.File_Knob('jobdrive', '')
            self.create1 = nuke.PyScript_Knob('create', 'Create')
            self.cancel1 = nuke.PyScript_Knob('cancel', 'Cancel')
            self.addKnob(self.jobKnobName)
            self.addKnob(self.jobKnob)
    
            while num <= self.numshots:
                shotNameKnobs.append(num)
                shotPathKnobs.append(num)
                shotNameKnobs[num] = nuke.String_Knob('shot'+str(num)+'name', 'shot name', 'Shot '+str(num))
                shotPathKnobs[num] = nuke.Text_Knob('shot'+str(num)+'path', 'shot path', self.jobKnob.value()+shotNameKnobs[num].value()+'/')
                self.addKnob(shotNameKnobs[num])
                self.addKnob(shotPathKnobs[num])
                num = num+1
    
            self.addKnob(self.create1)
            self.addKnob(self.cancel1)
    
            
        def knobChanged( self, knob ):
            
            if knob is self.jobKnob or shotPathKnobs:
                i = 1
                while i <=p.numshots:
                    shotPathKnobs[i].setValue(self.jobKnob.value()+shotNameKnobs[i].value()+'/')
                    i=i+1
    
            if knob is self.create1:
                if nuke.ask('Are you sure you want to create these Directories?'):
                    for d in shotPathKnobs[1:len(shotPathKnobs)]:
                        if not os.path.isdir(d.value()):
                                print  "making dir... "+d.value()
                                os.mkdir(d.value())
                        subDirs = ['2D_RENDERS', '3D_RENDERS', '3D_SCENES_ANIMATION', '3D_SCENES_RENDER', 'ANIMATION_DATA', 'CACHE_DATA', 'COMPS', 'EDIT_RENDERS', 'FOOTAGE', 'IMAGES', 'MOVIES', 'PREVIEWS', 'TRACKING']
                        for s in subDirs:
                            trgDir = d.value()+s+'/'
                            if not os.path.isdir(trgDir):
                                print  "making dir... "+trgDir
                                os.mkdir(trgDir)
                    self.finishModalDialog(True)
                    
            if knob is self.cancel1:
                self.finishModalDialog(False)

    p = shotFolderPanel()
    p.showModal()