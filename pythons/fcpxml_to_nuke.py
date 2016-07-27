'''
FCP XML to Nuke
v1.5 -
		Added render format selection, to allow the user to set what format the created write nodes are set to. Currently the choices are Prores4444, EXR, JPG (0.9 422), and DPX. 
		Rendering from Nuke in Prores 422HQ is not reccomended due to color shifts introduced by Nuke's YUV->RGB color transform. When Prores4444 is selected, the framerate is set to the clip framerate for the current clip.
v1.4 -
		Fixed a bug handling XMLs with multiple sequences.
v1.3 - 
	Made support for Premiere FCPXML format more robust. Premiere FCP XML stores all sequences in the project, whereas
Final Cut Pro's XML format stores only a single sequence. I added a box that lets you choose what sequence 
of the Premiere XML file to process, and it should work more reliably now.
	Added support for transfer of linear TimeRemaps, Translates, Scales, and Rotates into Nuke.
	Also transfers framerate for each clip, and many other improvements.
v1.0 - Initial release.

This script takes a Final Cut XML file with a single flattened video track, and builds Nuke scripts for each clip in the timeline.
It is intended as a simple way to automate workflows between FCP/Premiere and Nuke.
It creates a Nuke script with global first and last frame set, a frameRange node with the proper framerange, and a Write node
set to the output path and the render format that you specify.
There is an option for creating subdirectories for every Nuke script created. Handles are also an option.
It can parse reel number and clip number from Red and Alexa footage, or can use the clip filename as the base naming for the output files.

This script was somewhat inspired by compflows.blogspot.com, but has been written from scratch and is a bit more flexible (although it only goes from XML->NukeScripts and not from renders back to an XML at the moment).
This has only been tested on OSX, but in theory should be cross-platform compatible. Comments and suggestions are welcome!

# The menu.py example entry below adds this script in a folder called "Scripts" in your toolbar.
import fcpxml_to_nuke
nuke.toolbar('Nodes').addMenu('Scripts').addCommand('FCP XML to Nuke', 'fcpxml_to_nuke.process_xml()')

#####
This software is provided with no guarantee of functionality, no warranty, and no support. 
I am not responsible if it breaks your computer or deletes your files. 
However, you are free to use it for anything, share it with anyone, and modify it however you wish. Have fun!
'''

import nuke, os
from xml.dom.minidom import parse

def process_xml():
	'''
	Imports an FCP XML file, locates each clip in the timeline on Track 1, 
	and for each clip, builds a nuke script for that file and puts it in the output directory specified

	New Features that would be nice to have: 
	Customized naming patterns based on reel/clip number.
	Handle FCP XML from Premiere or FCP / FCPX ( Are there differences in the XML structure for these? )
	Choose additional output naming and directory formatting patterns
	'''

	# Build the Nuke Panel where locations and stuff is specified.
	p = nuke.Panel("FCP XML Import")
	xml_file = 'FCP XML To Import'
	output_dir = 'Directory to Output Nuke Scripts'
	subdirectories = 'Create subdirectories for each script?'
	render_dir = 'Render Directory for All Write Nodes'
	handle_length = "0 5 10 15 20 30 35 40"
	clip_name_format = "Bypass RED Alexa"
	render_format = 'Prores4444 exr jpg dpx'

	p.addFilenameSearch("FCP XML File", xml_file)
	p.addBooleanCheckBox("Create subdirectories for each script", subdirectories)
	p.addFilenameSearch("Output Directory", output_dir)
	p.addFilenameSearch("Render Directory", render_dir)
	p.addEnumerationPulldown("Handle Length", handle_length)
	p.addEnumerationPulldown("Clip Name Format", clip_name_format)
	p.addEnumerationPulldown("Render Format", render_format)
	p.setWidth(600)
	if not p.show():
		return

	# Assign vars from Nuke Panel user-entered data 
	xml_file 	= p.value("FCP XML File")
	output_dir	= p.value("Output Directory")
	subdirectories = p.value("Create subdirectories for each script")
	render_dir 	= p.value("Render Directory")
	handle_length = int( p.value("Handle Length") )
	clip_name_format = p.value("Clip Name Format")
	render_format = p.value('Render Format')

	# Create paths for render directory if it does not exist
	if not os.path.isdir(render_dir):
		os.mkdir(render_dir)
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)


	############################
	# Begin Parsing XML File
	############################
	dom = parse( xml_file )

	# Prompt user to choose which sequence to process, because Premiere's XML export includes all sequences.
	# Much of this complexity is to handle sequences with spaces in their names, because the nuke.panel
	# addEnumerationPulldown is space-demarcated. The logic below handles spaces in sequence names and allows the user 
	# to choose which sequence to process, and stores the sequence to process as a variable to access

	sequences = []
	sequence_objects = []
	i = 0
	# Makes a list of all sequence names
	for seq in dom.getElementsByTagName('sequence'):
		try:
			seq.getElementsByTagName('uuid')[0].firstChild.data #Catches all sequence objects with a uuid. These are edits.
			print "sequence name is:", seq.getElementsByTagName('name')[0].childNodes[0].data
			seqname = seq.getElementsByTagName('name')[0].firstChild.data
			sequences.append( [seqname] )
			sequence_objects.append( seq )
			# If a sequence name has space characters, replace them with underscores for the Nuke enumeration pulldown panel
			if seqname.find(' ') != -1:
				sequences[i].append( seqname.replace(' ', '_') )
		except:
			print i, " is not a sequence!"
			continue
		i += 1

	print "Sequences are: ", sequences
	# ??? Do all of the below messy work to prepare for deciding between multiple sequences, including dealing with spaces in sequence names
	# but only if there is more than one sequence in the XML file. If not, we'll just set the 'row' var to 0, and go forward with that.
	if len(sequences) > 1:
		# Makes a " " demarcated string with all sequence names for the nuke enumeration pulldown panel
		seq_enum = ''
		for i, seq in enumerate( sequences ):
			if len(sequences[i]) == 1:
				seq_enum += sequences[i][0] + ' '
			else:
				seq_enum += sequences[i][1] + ' '

		# Create a Nuke panel for the user to choose which sequence to process
		seq_panel = nuke.Panel("Choose Sequence To Process")
		seq_panel.addEnumerationPulldown("Choose Sequence", seq_enum)
		seq_panel.setWidth(400)
		if not seq_panel.show():
			return
		chosen_sequence = seq_panel.value("Choose Sequence")

		# Gets the index of the chosen sequence in the list of sequences, stores the sequence XML object as a variable
		for row, i in enumerate(sequences):
				try:
					column = i.index( chosen_sequence )
				except ValueError:
					continue
				break
	else:
		row = 0
	#chosen_seqobj = dom.getElementsByTagName('sequence')[row]
	chosen_seqobj = sequence_objects[row]
	print "Chosen sequence is number ", row, chosen_seqobj.getElementsByTagName('name')[0].firstChild.data

	seq_res_x = int( chosen_seqobj.getElementsByTagName('format')[0].getElementsByTagName('width')[0].firstChild.data )
	seq_res_y = int( chosen_seqobj.getElementsByTagName('format')[0].getElementsByTagName('height')[0].firstChild.data )
	print "Sequence resolution is ", seq_res_x,"x",seq_res_y

	sequence_fps = int( chosen_seqobj.getElementsByTagName('timebase')[0].firstChild.data )
	try:
		# This is a hack conditional: if the <ntsc> tag exists below the <timebase> tag, the framerate is set to its NTSC equivalent fractional framerate. 
		# For example, 24 becomes 23.976
		chosen_seqobj.getElementsByTagName('rate')[0].getElementsByTagName('ntsc')[0].firstChild.data
		sequence_fps = round(sequence_fps / 1.001, 3)
	except:
		pass
	print "Sequence framerate is: ", sequence_fps

	# Set optional effect parameters to False
	timeremap_value = False
	scale_value = False
	x_move = False
	y_move = False
	rotation_value = False
	clip_fps = 97 #This value gets set for each clip in the timeline

	seq_clip_number = 1
	track = chosen_seqobj.getElementsByTagName('track')[0]
	for clip in track.getElementsByTagName('clipitem'):
		# This loop performs the following for each clip on the first Track of the chosen Sequence.
		masterclipid 	= clip.getElementsByTagName('masterclipid')[0].firstChild.data
		clip_name 		= clip.getElementsByTagName("name")[0].firstChild.data
		in_point 		= int( clip.getElementsByTagName('in')[0].firstChild.data )
		out_point 		= int( clip.getElementsByTagName('out')[0].firstChild.data )
		clip_duration 	= int( clip.getElementsByTagName("duration")[0].firstChild.data )
		
		# Fetch the pathurl of the clip by cycling through all <pathurl> nodes and comparing the filename of the clip to the clip_name
		# This is necessary because in Premiere XMLs, the pathurl for a clip is not always stored in the clipitem node, but rather in a seperate node in the master-clip
		
		#??? Instead: Check for pathurl node in current clip node. If it doesn't exist, cycle through all 
		# clipitem nodes to find another that matches the name node with the current clip_name.
		# If it finds a matching named clipitem, search for a pathurl in that node.
		try:
			file_path = clip.getElementsByTagName('pathurl')[0].firstChild.data.split("file://localhost")[1].replace("%20", " ")
			clip_fps = float(clip.getElementsByTagName('timebase')[0].firstChild.data)
		except:
			print 'Failed to get pathurl in clipitem', clip_name, '. Searching other clipitems for matching name.'
			for pathurl_clip in dom.getElementsByTagName('clipitem'):
				if pathurl_clip.getElementsByTagName('name')[0].firstChild.data == clip_name:
					try:
						file_path = pathurl_clip.getElementsByTagName('pathurl')[0].firstChild.data.split("file://localhost")[1].replace("%20", " ")
						clip_fps = float(pathurl_clip.getElementsByTagName('timebase')[0].firstChild.data)
						break
					except:
						continue
		print clip_name, in_point, out_point, clip_duration, file_path, clip_fps

		# Get resolution of this clip in the clipitem node, 
		# Else, look for a masterclip with the same name and try to get the resolution from there, Else: fail?
		try:
			clip_width = int( clip.getElementsByTagName('width')[0].firstChild.data )
			clip_height = int( clip.getElementsByTagName('height')[0].firstChild.data )
			print "Clip resolution is: ", clip_width, "x", clip_height
		except:	
			for masterclip in dom.getElementsByTagName('clipitem'):
				if masterclip.getElementsByTagName('name')[0].firstChild.data == clip_name:
					#!!! This is triggered if a clip is used more than once in the sequence.
					try:
						#print "found master clip: ", masterclip.getElementsByTagName('name')[0].firstChild.data, " and "
						clip_width = int( masterclip.getElementsByTagName('width')[0].firstChild.data )
						clip_height = int( masterclip.getElementsByTagName('height')[0].firstChild.data )
						break
					except:
						continue
		# Get all effects applied to this clip
		for effect in clip.getElementsByTagName('effect'):
			effect_name = effect.childNodes[1].firstChild.data
			if effect_name == 'Time Remap':
				# Loop through all parameters of the effect
				for param in effect.getElementsByTagName('parameter'):
					param_id = param.childNodes[1].firstChild.data
					if param_id == 'speed':
						timeremap_value = float( param.getElementsByTagName('value')[0].firstChild.data )
						print effect_name, param_id, timeremap_value

			if effect_name == 'Basic Motion':
				for param in effect.getElementsByTagName('parameter'):
					param_id = param.childNodes[1].firstChild.data
					if param_id == 'scale':
						scale_value = float( param.getElementsByTagName('value')[0].firstChild.data )
						print effect_name, param_id, scale_value
					if param_id == 'rotation':
						rotation_value = float( param.getElementsByTagName('value')[0].firstChild.data )
						print effect_name, param_id, rotation_value
					if param_id == 'center':
						x_move = float( param.getElementsByTagName('value')[0].childNodes[1].firstChild.data )
						y_move = float( param.getElementsByTagName('value')[0].childNodes[3].firstChild.data )
						print effect_name, param_id, x_move, y_move
						'''
						So.... Figuring out how Premiere handles position values:
						Prem 0-0 clip is centered upper left: value = .5,.5
						prem 1920-1080, clip is centered lower right: value = .5 .5??
						prem 1060-640, value: 0.052083 0.092593
						prem center bottom: 960-1080, value: 0.0 0.5
						prem center top: 960 0, value: 0.0 -0.5
						prem UR 1919 0, value: 0.499479 -0.5
						
						location 	x, y
						center 		0, 0
						UL			-0.5, -0.5
						UR 			0.5, -0.5
						LR 			0.5, 0.5
						LL 			0, 0.5
						y-up is negative
						x-right is positive
						The range from edge to edge of sequence space is 1. 
						-.5 is left, .5 is right. 
						-.5 is up, .5 is down.
						.125, 0 would be 1200x540 = (seq_res_x * x_move) = how many pixels to move from center) = 1920*.125 + 1920/2 = 1200
						for x: seq_res_x * x_move
						for y: seq_res_y * -y_move
						'''
		
		# Gets the shot name, which is the formatted clip_name with clip# and reel#, with the sequence clipnumber.
		# uses camera type (Red, Alexa, etc), and the clip_name string (the filename of the clip used in FCP) 
		# Also takes the seq_clip_number for returning the correct shot_name (the name that will be used to name the nuke script)
		if clip_name_format == 'RED':
			# This works for Red footage of format: A###_C###_RANDOMDATA
			reel_number = clip_name.split('_')[0][1:]
			clip_number = clip_name.split('_')[1][1:]

		if clip_name_format == 'Alexa':
			# Alexa footage is A###C###_######_R####
			reel_number = int(clip_name.split('C')[0][1:])
			clip_number = int( clip_name.split('C')[1].split('_')[0] )

		if clip_name_format == 'Bypass':
			shot_name = "%02d0_%s" %(seq_clip_number, os.path.splitext(clip_name)[0])
		else:
			# shot_name is the string that defines the name that the nuke script is saved to. seq_clip_number+0_A{reelnumber}_C{clipnumber}
			shot_name = "%02d0_A%sC%s" %(seq_clip_number, reel_number, clip_number)


		############################
		# Build Nuke Script
		############################
		
		# if the subdirectories checkbox is checked, set the output_shotdir to be a subdirectory named with the shot_name
		if subdirectories:
			output_shotdir = output_dir
			output_shotdir = os.path.join(output_dir, shot_name)
		else:
			output_shotdir = output_dir
		# If the output_shotdir does not exist, create it (auto-creates subdirectories)
		if not os.path.isdir(output_shotdir):
				os.mkdir(output_shotdir)

		
		###########################
		# Compute values to plug into the Nuke Script

		# Compute Handles and set first_frame and last_frame
		first_frame = in_point - handle_length
		last_frame = out_point-1 + handle_length

		if timeremap_value:
			'''
			The XML gives us the duration of the original clip, and the in and out points of the retimed clip 
			originalIn = newIn * retime
			originalOut = newOut * retime
			new duration = lastFrame - first_frame
			'''
			timeremap_value 	= timeremap_value/100
			new_clip_duration 	= last_frame - first_frame
			clip_duration 		= clip_duration * timeremap_value
			first_frame 		= first_frame * timeremap_value
			last_frame 			= first_frame + new_clip_duration
			
			
		# Set Format 
		if seq_res_x == 1920 and seq_res_y == 1080:
			fcp_xml_resolution = 'HD'
		else:
			fcp_xml_resolution = 'from_xml'


		#!!! This creates a nuke script by appending text to the .nk file instead of using nuke.nodeCopy(), which is slow and messy, and so that root node settings can be added.
		# The strings that are written are triple-quoted. newlines are created with '\n'. {} chars in the string have to be doubled so as not to throw a KeyError
		nuke_file = os.path.join(output_shotdir, "%s_v001.nk"%(shot_name))
		nuke_script = open(nuke_file, 'a+')
		# Create Root node
		nuke_script.write('''Root {{\n inputs 0\n name \"{0}\"\n project_directory \"\[python \{{nuke.script_directory()\}}]\"\n first_frame {1}\n last_frame {2}\n fps {6}\n format \"{3} {4} 0 0 {3} {4} 1 {5}\"\n proxy_type scale\n}}\n'''.format(nuke_file, first_frame, last_frame, seq_res_x, seq_res_y, fcp_xml_resolution, clip_fps))
		# Create Read node
		nuke_script.write('''Read {{\n inputs 0\n file \"{0}\"\n first 0\n last {1}\n frame_mode offset\n frame 1\n origlast {1}\n origset true\n name Read1\n selected true\n xpos -425\n ypos -40\n}}\n'''.format(file_path, clip_duration))
		# Create TimeRemap if there is retiming on the clip
		if timeremap_value:
			nuke_script.write('''
Text {
 message "\[frame]"
 font /Library/Fonts/Arial.ttf
 yjustify center
 box {480 270 1440 810}
 translate {1314 -498}
 center {960 540}
 name FrameNumber
 selected true
 xpos -425
 ypos 42
}
''')
			nuke_script.write('''Group {{
 name RetimeFromFrame
 selected true
 addUserKnob {{20 Retime t "Retime From Frame Parameters"}}
 addUserKnob {{41 StartFrame l "SourceStart Frame" t "The source frame from which retiming starts. For example, if you have a clip that you are using a range from frames 200-300 in, and you want to retime that clip to be 50\% speed, you would set this to be 200. \\n\\nThis gizmo references the root.first_frame value to determine the \\\"in-point\\\" of the clip." T RetimeControls.StartFrame}}
 addUserKnob {{41 PlaybackSpeed l "Playback Speed" t "Retime speed as a fraction of one. That is, 0.5 = 50\% speed, 2 = 200\% speed." T RetimeControls.PlaybackSpeed}}
}}
 Input {{
  inputs 0
  name Input1
  xpos 0
 }}
 TimeOffset {{
  time_offset {{{{-RetimeControls.StartFrame/RetimeScreen.timingSpeed}}}}
  name Retime_TimeOffset
  tile_color 0xff0000ff
  xpos 0
  ypos 132
 }}
 OFXuk.co.thefoundry.time.oflow_v100 {{
  method Motion
  timing Speed
  timingFrame 1
  timingSpeed {{{{RetimeControls.PlaybackSpeed}}}}
  filtering Normal
  warpMode Normal
  correctLuminance false
  automaticShutterTime false
  shutterTime 0
  shutterSamples 1
  vectorDetail 0.2
  smoothness 0.5
  blockSize 6
  Tolerances 0
  weightRed 0.3
  weightGreen 0.6
  weightBlue 0.1
  showVectors false
  cacheBreaker false
  name RetimeScreen
  tile_color 0xff0000ff
  selected true
  xpos 0
  ypos 156
 }}
 TimeOffset {{
  time_offset {{{{root.first_frame}}}}
  name GlobalStart_Offset
  tile_color 0xff0000ff
  xpos 0
  ypos 180
 }}
 Output {{
  name Output1
  xpos 0
  ypos 393
 }}
 NoOp {{
  inputs 0
  name RetimeControls
  xpos -174
  ypos 126
  addUserKnob {{20 User}}
  addUserKnob {{7 PlaybackSpeed l "Playback Speed" R 0 100}}
  PlaybackSpeed {0}
  addUserKnob {{3 StartFrame l "Start Frame" t "Offset video start frame"}}
  StartFrame {1}
 }}
end_group\n'''.format( timeremap_value, first_frame ))
		
		# Create FrameRange node 
		nuke_script.write('''FrameRange {{\n first_frame {0}\n last_frame {1}\n name FrameRange1\n label "\\[knob first_frame]-\\[knob last_frame]"\n selected true\n}}\n'''.format(first_frame, last_frame))
		
		# Create a Transform node with pans and scales, if they exist
		if 	scale_value or x_move or y_move or rotation_value:
			if not scale_value:
				scale_value = 100
			if not x_move:
				x_move = 0
			if not y_move:
				y_move = 0
			if not rotation_value:
				rotation_value = 0
			# Create a reformat node if there are pans or scales
			nuke_script.write('''Reformat {{
 resize none
 black_outside true
 name Reformat1
 selected true
}}
'''.format())
			nuke_script.write( '''Transform {{
 translate {{{0} {1}}}
 rotate {2}
 scale {3}
 center {{{4} {5}}}
 name Transform1
 selected true
 }}
'''.format( (seq_res_x * x_move), (seq_res_y * -y_move), -rotation_value, scale_value/100, seq_res_x/2, seq_res_y/2 ) )

		# Create Write node
		render_shot_dir = os.path.join(render_dir, shot_name)
		if render_format == 'Prores4444':
			nuke_script.write('''Write {{\n file \"{0}\"\n file_type mov\n codec ap4h\n fps {1}\n checkHashOnRead false\n name Write1\n selected true\n}}\n'''.format(render_shot_dir+'_v001.mov', clip_fps))
		elif render_format == 'exr':
			nuke_script.write('''Write {{\n file \"{0}\"\n file_type exr\n "Standard layer name format" true\n name Write1\n selected true\n}}\n'''.format(render_shot_dir+'/'+shot_name+'_v001.####.exr'))
		elif render_format == 'jpg':
			nuke_script.write('''Write {{\n file \"{0}\"\n file_type jpg\n _jpeg_quality 0.9\n _jpeg_sub_sampling 4:2:2\n checkHashOnRead false\n name Write1\n selected true\n}}\n'''.format(render_shot_dir+'/'+shot_name+'_v001.####.jpg'))
		elif render_format == 'dpx':
			nuke_script.write('''Write {{\n file \"{0}\"\n file_type dpx\n checkHashOnRead false\n name Write1\n selected true\n}}\n'''.format(render_shot_dir+'/'+shot_name+'_v001.####.dpx'))

		# Create Viewer node
		nuke_script.write('''Viewer {\n name Viewer1\n selected true\n}\n''')
		# Create Backdrop node
		nuke_script.write('''BackdropNode {{\n inputs 0\n name BackdropNode1\n tile_color 0x26434dff\n label \"<img src=\\\"Read.png\\\"> Read Plate <br/><font size=1> {0} <br/> {1}-{2}<br/>{3} frame handles\"\n note_font_size 30\n selected true\n xpos -500\n ypos -150\n bdwidth 234\n bdheight 254\n}}\n'''.format(shot_name, in_point, out_point, handle_length))

		seq_clip_number += 1
		# Reset option effect parameters to false for next clip iteration
		timeremap_value = False
		scale_value = False
		x_move = False
		y_move = False
		rotation_value = False
		### End of for loop which processes each clip in timeline.


	nuke.message('All clips processed successfully!')
	return



'''
		### ??? ALTERNATIVE METHOD FOR CREATING THE SCRIPT FILES
		### This approach uses the script that import_xml is executed from as a base for creating nodes, and then using nuke.nodeCopy() to 'paste' the data into each script file.
		### The approach I ended up using instead just uses python to format .nk scripts as text, inputting the variables where relevant. It is much faster and more efficient.
		for node in nuke.allNodes():
			node.setSelected(True)
		nuke.nodeDelete()

		# Create Read node
		read = nuke.createNode("Read")
		read.knob("file").setValue(file_path)
		read.knob("frame_mode").setValue('offset')
		read.knob("frame").setValue('1')
		read.knob("first").setValue(0)
		read.knob("last").setValue(clip_duration)

		# Create a NoOp node to hold shot info
		#!!! This is not needed
		#shotInfo = nuke.createNode('NoOp')
		#shotInfo.knob('name').setValue(shot_name+"_info")
		#shotInfo.addKnob( nuke.String_Knob("The original name of the clip", "clip_name", clip_name) )
		#shotInfo.addKnob( nuke.String_Knob("Base name of the nuke script", "shot_name", shot_name) )

		# Create FrameRange node
		frame_range = nuke.createNode("FrameRange")
		frame_range.knob('label').setValue('[knob first_frame]-[knob last_frame]')
		frame_range.knob('first_frame').setValue( in_point - handle_length ) 
		frame_range.knob('last_frame').setValue( out_point-1 + handle_length )
		
		# Create Write node
		write = nuke.createNode("Write")
		write.knob('file').setValue('{0}{1}_v001.mov'.format(render_dir, shot_name))
		#write.knob("file_type").setValue("mov")
		#write.knob("mov.codec").setValue("apch")
		#write.knob("mov.fps").setValue("23.976")

		# Create Viewer Node
		nuke.createNode('Viewer')

		# Informational Backdrop Node
		bd_node = nuke.createNode("BackdropNode")
		bd_node.knob("tile_color").setValue(0x26434dff)
		bd_node.knob("note_font_size").setValue(30)
		bd_node.knob("bdwidth").setValue(234)
		bd_node.knob("bdheight").setValue(254)
		bd_node.knob("label").setValue('<img src=\"Read.png\"> Read Plate <br/><font size=1> %s <br/> %s-%s'%(shot_name,int(in_point),int(out_point)))

		# Set root script values
		#nuke.toNode('root').knob('project_directory').setValue('[python {nuke.script_directory()}]')
		#nuke.toNode('root').knob('first_frame').setValue( in_point-handle_length)
		#nuke.toNode('root').knob('first_frame').setValue( (out_point-1) + handle_length)
		#nuke.toNode('root').knob('format').setValue('HD')

		# Select all created nodes and copy them into a new script
		for node in nuke.allNodes():
			node.setSelected(True)
		nuke.nodeCopy(nuke_file)
		'''