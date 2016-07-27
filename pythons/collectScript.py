# -*- coding: utf8 -*-

'''
NUKE Collector Files
by Mathieu Vallet

www.mathieuvallet.com

Updated on 24 Sept 2015

All Rights Reserved.

'''

import nuke, os
import shutil        # Operations on files and collections of files
import re


### SET VARIABLES ###
scriptName = ""
outDir = ""
selectedRead = []
readList = []

# Building of the Panel Functions
def mainFunction():
	cp = nuke.Panel("Collect Script Nodes...                   by Mathieu Vallet", 430)
	cp.addSingleLineInput("Script Name ", nuke.scriptName().split('/')[-1][:-3])
	cp.addFilenameSearch("Output Folder ", os.getcwd().replace('\\', '/') + '/')
	cp.addEnumerationPulldown("Needed Nodes ","All_Nodes Selected_Nodes")
	cp.addButton("Cancel")
	cp.addButton("Collect")
	
	# Show the collectPanel
	result = cp.show()
	
	# If the user press Collect
	if result == 1:

		# Get the script name
		scriptName = cp.value("Script Name ")
		
		# Get the output folder
		outDir = cp.value("Output Folder ")
		
		# Get needed nodes
		allOrSelec = cp.value("Needed Nodes ")
		
		# Check if all or selected
		if allOrSelec == "All_Nodes":
			# Select all nodes
			nuke.selectAll()
			
			# Create all Reads list
			createAllReadList()
			
			# Count elements to copy
			countElements()
			
			# Copy sources files
			fileCopy(outDir, scriptName)
			
		else:
		### ERROR CHECK SELECTED NODES ###
			if nuke.selectedNodes() == []:
				nuke.message("Please select nodes that you want")
				# Exit tool
				return
			else:
				# Create selected reads list
				createSelectedReadList()
				
				# Count elements to copy
				countElements()

				# Copy sources files
				fileCopy(outDir, scriptName)
			
	else:
		# Exit tool
		return

# Count the number of frames to copy    
def countElements():
	if selectedRead != []:
		countElements.count = 0
		# Get the path for each reads
		for read in selectedRead:
			
			# Get the file path
			absPath = read.knob('file').getValue()
			
			if absPath != "":
				# Split the path
				splitPath = absPath.split('/')
				
				# Get the file name
				file = splitPath[-1].split('.')[:-1]
				file = '.'.join(file)
				print file
				
				# Check if it's a still file
				reSearch = re.search('\%\d+d|D', file)
				if reSearch == None:
					# Add count
					countElements.count += 1
					
				# If it's a sequence files
				else:
					# Get the padding for sequence files
					padd = int(file.replace('.','_').replace('-','_').split('_')[-1][1:-1])
					if padd < 10:
						fileName = file[:-4]
					else:
						fileName = file[:-5]
					
					# Get the frame rage to copy
					try:
						firstF = int(read.knob('first').getValue())
						lastF = int(read.knob('last').getValue())
					except:
						try:
							firstF = int(read.knob('range_first').getValue())
							lastF = int(read.knob('range_last').getValue())
						except:
							firstF = int(nuke.root().knob('first_frame').getValue())
							lastF = int(nuke.root().knob('last_frame').getValue())
							
					# Prevent still file | e.g. render files in write node don't have indicate frame range although that is a sequence
					if firstF == lastF:
						firstF = int(nuke.root().knob('first_frame').getValue())
						lastF = int(nuke.root().knob('last_frame').getValue())
					
					# Add count
					countElements.count += (lastF-firstF)

# Copy function
def fileCopy(outDir, scriptName):
	
	### ERROR CHECK IF NO SELECTED READ ###
	if selectedRead != []:
		# Create a Sources folder
		createSourcesDir(outDir)
		m = 0
		
		# Create a progress bar panel
		progTask = nuke.ProgressTask("Collecting...")
		
		# Get the path for each reads
		for read in selectedRead:
			
			# Get the file path
			absPath = read.knob('file').getValue()
			
			if absPath != "":
				# Split the path
				splitPath = absPath.split('/')
				
				# Get the file name
				file = splitPath[-1].split('.')[:-1]
				file = '.'.join(file)
				
				# Get new folder name based on the file name
				fileDir = file.replace(' ','_').replace('.','_').replace('-','_').split('_')
				if len(fileDir) != 1:
					fileDir = fileDir[:-1]
				fileDir = '_'.join(fileDir)
				
				# get the file extension
				fileExt = '.' + splitPath[-1].split('.')[-1]
				
				# complete path without the file name
				seqFolder = absPath[0:absPath.find(file)]
				
				# Creation of the path and folder destination
				# Change the current os path
				os.chdir(outDir + 'Sources')
				
				# Create a folder with file name if not exist yet
				if not os.path.exists(fileDir):
					os.mkdir(fileDir)
				else:pass
				
				# Change the os path for the destination copy path
				os.chdir(outDir + 'Sources' + '/' + fileDir)
				dstPath = os.getcwd() + '/'
				
				# Check if file is not already copy
				pathList = []
				inList = absPath in pathList
				if inList == False:
					pathList.append(absPath)
				else:continue
				
				# Check if it's a still file
				reSearch = re.search('\%\d+d|D', file)
				if reSearch == None:
					# Source path
					src = absPath
					
					# Copy the file
					shutil.copy2(src, dstPath)
					
				# If it's a sequence files
				else:
					# Get the padding for sequence files
					padd = int(file.replace('.','_').replace('-','_').split('_')[-1][1:-1])
					if padd < 10:
						fileName = file[:-4]
					else:
						fileName = file[:-5]
					
					# Get the frame rage to copy
					try:
						firstF = int(read.knob('first').getValue())
						lastF = int(read.knob('last').getValue())
					except:
						try:
							firstF = int(read.knob('range_first').getValue())
							lastF = int(read.knob('range_last').getValue())
						except:
							firstF = int(nuke.root().knob('first_frame').getValue())
							lastF = int(nuke.root().knob('last_frame').getValue())
							
					# Prevent still file | e.g. render files in write node don't have indicate frame range although that is a sequence
					if firstF == lastF:
						firstF = int(nuke.root().knob('first_frame').getValue())
						lastF = int(nuke.root().knob('last_frame').getValue())
					else:pass
					
					# Variable 
					
					for f in range(firstF, lastF + 1):
						
						### WARNING IF CANCELED DURING THE COPY ###
						if progTask.isCancelled():
							del progTask
							nuke.message("Copying is not completed")
							print "Copying is not completed"
							nuke.undo()
							for each in nuke.allNodes(): 
								each.knob("selected").setValue(False)
							# Return to the original os path
							os.chdir(outDir)
							return
							
						# Set progress
						percent = (float(m) / float(countElements.count)) * 100
						progTask.setProgress(int(percent))
						
						# Creation of the full sources path
						src = seqFolder + fileName + str(f).zfill(padd) + fileExt
						
						# Copy files
						try:
							shutil.copy2(src, dstPath)
						except:pass
						
						# Incrementation
						m += 1
						
						# Show the current sequence copy progress
						progTask.setMessage("Copying: " + fileName + str(f).zfill(padd)+fileExt )
									
			# If file knob is empty go next
			else:pass
		
		# Exit progTask after each read collect
		del progTask
		
	# If no selected read just pass
	else:pass
	
	# Replace absolute file path by a relative one
	for read in selectedRead:
		# Get the file path
		absPath = read.knob('file').getValue()
		
		if absPath != "":
			# Split the path
			splitPath = absPath.split('/')
			
			# Get the file name
			file = splitPath[-1].split('.')[:-1]
			file = '.'.join(file)
			
			# Get new folder name based on the file name
			fileDir = file.replace(' ','_').replace('.','_').replace('-','_').split('_')
			if len(fileDir) != 1:
				fileDir = fileDir[:-1]
			fileDir = '_'.join(fileDir)
			
			# complete path without the file name
			seqFolder = absPath[0:absPath.find(file)]
			
		relPath = absPath.replace(seqFolder, "[file dirname [value root.name]]" + "/Sources/" + fileDir + "/")
		relPath = read.knob('file').setValue(relPath)
		
	# Copy nodes in a new script    
	nuke.nodeCopy(outDir + scriptName + '.nk')
	
	# Deselect nodes in the new script
	badWords = ["selected true"]
	old = open(outDir + scriptName + '.nk', 'r')
	new = open(outDir + scriptName + "_temp" + '.nk', 'w')
	for line in old:
		if not any(badWord in line for badWord in badWords):
			new.write(line)
		else:pass
	old.close(), new.close()
	shutil.move(outDir + scriptName + "_temp" + '.nk', outDir + scriptName + '.nk')
	
	# Get same settings in the new script
	rootFrame = str(int(nuke.root().knob('frame').getValue()))
	rootFF = str(int(nuke.root().knob('first_frame').getValue()))
	rootLF = str(int(nuke.root().knob('last_frame').getValue()))
	rootFPS = str(int(nuke.root().knob('fps').getValue()))
	rootFormat = '"' + nuke.root().knob('format').toScript() + '"'
	rootViews = '"' + nuke.root().knob('views').toScript() + '"'
	logfile = open(outDir + scriptName + '.nk', 'a')
	logfile.write("\nRoot {\n frame " + rootFrame + "\n first_frame " + rootFF + "\n last_frame " + rootLF + "\n lock_range true\n fps " + rootFPS + "\n format " + rootFormat + "\n views " + rootViews + "\n}")
	logfile.close()
	
	# Undo the relative path for the current script and deselect nodes
	for each in nuke.allNodes(): 
		each.knob("selected").setValue(False)
	
	nuke.undo()
		
	# Return to the original os path
	os.chdir(outDir)
	
	# The End :)
	print "Everything went well !"
	print "Script saved here --> %s" % outDir
	nuke.message("Script saved here : \n\n" + outDir)

# Create a Sources folder function
def createSourcesDir(outDir):
	# Update the current directory
	os.chdir(outDir)

	### ERROR CHECK ALREADY SOURCES FOLDER ###
	if not os.path.exists('Sources'):
		# Create the Sources folder if not already exist yet
		os.mkdir('Sources')
		
	# Do nothing
	else:return
		
# Create a read list with All nodes function
def createAllReadList():
	# Get all reads nodes
	read = nuke.allNodes('Read')
	readGeo = nuke.allNodes('ReadGeo2')
	camera = nuke.allNodes('Camera2')
	axis = nuke.allNodes('Axis2')
	deepRead = nuke.allNodes('DeepRead')
	audioRead = nuke.allNodes('AudioRead')
	write = nuke.allNodes('Write')
	writeGeo = nuke.allNodes('WriteGeo')
	deepWrite = nuke.allNodes('DeepWrite')
	precomp = nuke.allNodes('DeepWrite')
	listedRead = [read, readGeo, camera, axis, deepRead, audioRead, write, writeGeo, deepWrite, precomp]
	
	# Create a read list
	for z in listedRead:
		if len(z) != 0:
			readList.append(z)
		else:pass

	# Put all reads nodes into a single list
	for x in readList:
		n = 0
		selectedReadList = x
		for node in selectedReadList:
			selectedRead.append(selectedReadList[0+n])
			n += 1
			
# Create a read list with Selected nodes function
def createSelectedReadList():
	# Get selected reads nodes
	read = nuke.selectedNodes('Read')
	readGeo = nuke.selectedNodes('ReadGeo2')
	camera = nuke.selectedNodes('Camera2')
	axis = nuke.selectedNodes('Axis2')
	deepRead = nuke.selectedNodes('DeepRead')
	audioRead = nuke.selectedNodes('AudioRead')
	write = nuke.selectedNodes('Write')
	writeGeo = nuke.selectedNodes('WriteGeo')
	deepWrite = nuke.selectedNodes('DeepWrite')
	precomp = nuke.selectedNodes('Precomp')
	listedRead = [read, readGeo, camera, axis, deepRead, audioRead, write, writeGeo, deepWrite, precomp]
	
	# Create a read list
	for z in listedRead:
		if len(z) != 0:
			readList.append(z)
		else:pass

	# Put selected reads nodes into a single list
	if readList != []:
		for x in readList:
			n = 0
			selectedReadList = x
			for node in selectedReadList:
				selectedRead.append(selectedReadList[0+n])
				n += 1
				
	else:return
## last line as described by author in http://www.nukepedia.com/python/import/export/script-collector-for-windows#comment-3238		
##mainFunction()