### GIZMOs MENU by Luma Pictures (http://www.lumapictures.com/), with some modifications 
### by Piotr Borowski (http://www.nukepedia.com/python/ui/auto-creation-of-menu-items-for-gizmos-menupy#comment-2636)
### and me (kagarrache@gmail.com)

# *****************************************************************************
# NOTE: in order for this to work, you must ALSO install the included init.py;
# the installation instructions for it are essentially identical...
# *****************************************************************************
#
# To use this file, copy it as 'menu.py' to a directory on your plugin path.
# By default, the plugin path is (taken from the nuke manual):
#
# Linux:
#  /users/login name/.nuke
#  /usr/local/Nuke6.0v6/plugins
# Mac OS X:
#  /Users/login name/.nuke
#  /Applications/Nuke6.0v6/Nuke6.0v6.app/Contents/MacOS/plugins
# Windows:
#  In the .nuke directory, which can be found under the directory pointed to
#  by the HOME environment variable. If this variable is not set (which is
#  common), the .nuke directory will be under the folder specified by the
#  USERPROFILE environment variable - which is generally of the form:
#    drive letter:\Documents and Settings\login name\      (Windows XP)
#        or
#    drive letter:\Users\login name\                       (Windows Vista)
#
# If there is already a 'menu.py' at that location, open it in your favorite
# text editor, and add the contents of this file to the end of it.
#
# Once installed, this script will allow you to create subfolders within the
# same directory it resides in (or in the directory pointed at by the
# NUKE_GIZMO_PATH environment variable, if it is defined, or you may provide
# a custom directory by editing the CUSTOM_GIZMO_LOCATION, below), and have gizmos
# within those subfolders automatically available in nuke from the menu (or submenu)
# of the same name.
#
# Ie, if your directory structure looks like this:
#
# /basePluginDir
#     menu.py
#     /Images
#         Rainbow.gizmo
#     /MyCustomMenu
#         /SubMenu
#             MakeAwesome.gizmo
#
# ...then when you clicked on the 'Image' menu, there would be an additional
# item at the end to create a 'Rainbow' node.  Additionally, there would
# be a new top-level menu, 'MyCustomMenu', which would have a 'SubMenu', which
# would have an entry to create a 'MakeAwesome' node.


if __name__ == '__main__':
  # Just in case they didn't use the supplied init.py
  gizManager = globals().get('gizManager', None)
  if gizManager is None:
      print 'Problem finding GizmoPathManager - check that init.py was setup correctly'
  else:
      gizManager.addGizmoMenuItems()
      # Don't need it no more...
      del gizManager

## EXTRA PANELS

## TO-DO list
import ToDoList
ToDoList.registerNukePanel()

## FOV calculator
import FovCalculator
def addFovCalc():
    fovCalc = FovCalculator.FovCalculator()
    return fovCalc.addToPane()
nuke.menu('Pane').addCommand( 'Fov Calculator', addFovCalc )
nukescripts.registerPanel( 'com.ohufx.FovCalculator', addFovCalc )




# ANIMATION ITEMS----------------------------------------#
m=nuke.menu('Animation').findItem('Predefined')
m.addCommand('Reverse curve', 'nuke.load("animation_curve_reverse"), animation_curve_reverse()')


##Ym_AlignNode
import Ym_AlignNode
YmAlign = toolbar.addMenu("Ym AlignNode", icon = "AlignNode.png")
YmAlign.addCommand("Left X", "Ym_AlignNode.F_AlignLX()", "Ctrl+F1", icon = "leftX.png")
YmAlign.addCommand("Center X", "Ym_AlignNode.F_AlignCX()", "Ctrl+F2", icon = "centerX.png")
YmAlign.addCommand("Right X", "Ym_AlignNode.F_AlignRX()", "Ctrl+F3", icon = "rightX.png")
YmAlign.addCommand("Interval X", "Ym_AlignNode.F_Align_intX()", "Ctrl+F4", icon = "intervalX.png")
YmAlign.addCommand("Top Y", "Ym_AlignNode.F_AlignTY()", "Ctrl+F5", icon = "topY.png")
YmAlign.addCommand("Center Y", "Ym_AlignNode.F_AlignCY()", "Ctrl+F6", icon = "centerY.png")
YmAlign.addCommand("Under Y", "Ym_AlignNode.F_AlignUY()", "Ctrl+F7", icon = "underY.png")
YmAlign.addCommand("Interval Y", "Ym_AlignNode.F_Align_intY()", "Ctrl+F8", icon = "intervalY.png")
YmAlign.addCommand("Interval XX", "Ym_AlignNode.F_Align_intXX()", "Ctrl+F9", icon = "intervalXX.png")
YmAlign.addCommand("Interval YY", "Ym_AlignNode.F_Align_intYY()", "Ctrl+F10", icon = "intervalYY.png")






### Python Scripts Menus

## import part
import projectionist
import autoComper

import RotoShapes_to_trackers

import Locometry
import imagePlane
import ztools_exrMerge_v1_1
import collectScript
import makeShotDirPick
import batchrenamer
import wavePanel


## extra commands
locoGui = Locometry.LocoWidget()


## Menu itself
PyTools = toolbar.addMenu ("Python Tools", icon = "Jose_Icon.png")

## Menu items (manually sorted)

## autocomper is incomplete
PyTools.addCommand('autocomper', 'autoComper.autoComper()', icon='autoComper.png' )
PyTools.addCommand('Batch Rename', 'import batchrenamer; batchrenamer.main()')
PyTools.addCommand("collectScript", "collectScript.mainFunction()") 

PyTools.addCommand("ExrMerge","ztools_exrMerge_v1_1.executeScript()", icon="exr_merge.png")
PyTools.addCommand('Image_Plane', 'imagePlane.imagePlane()')

PyTools.addCommand('Locometry-GUI', lambda: locoGui.show())
PyTools.addCommand('Make Shot Directories', 'makeShotDirPick.makeShotDir()')

PyTools.addCommand("Roto Shapes to tracker", "RotoShapes_to_trackers.RotoShape_to_Trackers()")
PyTools.addCommand('TrackerToRoto', 'nuke.load("C:/Users/Yo/.nuke/pythons/TrackerToRoto.py")')

PyTools.addCommand ( "wavePanel v1.4", 'wavePanel.go()', icon="wavePanel.png" )