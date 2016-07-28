import nuke
import glob 
import os 
import re
import nukescripts 

def generateReadFromWrite():
    writeSelected = 0
    firstFrame = int(nuke.root().knob('first_frame').value())
    lastFrame = int(nuke.root().knob('last_frame').value())
    for i in nuke.selectedNodes():
		if i.Class() == 'Write':
			writeSelected = writeSelected + 1
			fileName = i.knob('file').value()
			newRead = nuke.createNode('Read')
			newRead.knob('file').setValue(fileName)

			cleanPath = nukescripts.replaceHashes(fileName) 
			padRE = re.compile('%0(\d+)d') 
			padMatch = padRE.search(cleanPath) 
			
			if padMatch: 
				padSize = int(padMatch.group(1)) 
				frameList = sorted(glob.iglob(padRE.sub('[0-9]' * padSize, cleanPath))) 
				first = os.path.splitext(frameList[0])[0][-padSize:] 
				last = os.path.splitext(frameList[-1])[0][-padSize:] 
				newRead['file'].fromUserText('%s %s-%s' % (cleanPath, first, last)) 

    if len(nuke.selectedNodes()) == 0:
        nuke.message('select a Write node')
        writeSelected = writeSelected + 1
    if writeSelected == 0:
        nuke.message('No Write nodes present in the current selection')