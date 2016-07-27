def createWriteDir():
  import nuke, os, errno
  file = nuke.filename(nuke.thisNode())
  dir = os.path.dirname( file )
  osdir = nuke.callbacks.filenameFilter( dir )
  # cope with the directory existing already by ignoring that exception
  try:
    os.makedirs( osdir )
  except OSError, e:
    if e.errno != errno.EEXIST:
      raise
nuke.addBeforeRender(createWriteDir)




# To use this file, copy it as 'init.py' to a directory on your plugin path.
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
# If there is already a 'init.py' at that location, open it in your favorite
# text editor, and add the contents of this file to the end of it.
#
# Once installed, this script will add to the plugin path subfolders of the
# folder it resides in (or of directories pointed at by the NUKE_GIZMO_PATH
# environment variable, if it is defined... or you may provide a custom
# directory by editing the CUSTOM_GIZMO_LOCATION, below), and have gizmos within
# those subfolders automatically available in nuke
# 
# If in GUI mode, menu items for these subfolders may also be automatically
# created - see 'menu.py' for details.
NUKE_GIZMO_PATH = 'C:\Users\yo\.nuke\Gizmos'

# Example custom gizmo locations:

# Linux:
# CUSTOM_GIZMO_LOCATION = r'/users/<login name>/.nuke/Gizmos'

# Mac OS X:
# CUSTOM_GIZMO_LOCATION = r'/Users/<login name>/.nuke/Gizmos'

# Windows:
# CUSTOM_GIZMO_LOCATION = r'C:\Users\<login name>\.nuke\Gizmos'

# WARNING: on windows, do NOT end with a trailing slash... ie this is BAD:
# CUSTOM_GIZMO_LOCATION = r'C:\Users\<login name>\.nuke\Gizmos\'

CUSTOM_GIZMO_LOCATION = r'C:\Users\yo\.nuke'

import os
import re

import nuke

class GizmoPathManager(object):
    def __init__(self, exclude=r'^\.', searchPaths=None):
        '''Used to add folders within the gizmo folder(s) to the gizmo path
        
        exclude: a regular expression for folders / gizmos which should NOT be
            added; by default, excludes files / folders that begin with a '.'
            
        searchPaths: a list of paths to recursively search; if not given, it
            will use the NUKE_GIZMO_PATH environment variable; if that is
            not defined, it will use the directory in which this file resides;
            and if it cannot detect that, it will use the pluginPath 
        '''
        if isinstance(exclude, basestring):
            exclude = re.compile(exclude)
        self.exclude = exclude
        if searchPaths is None:
            searchPaths = os.environ.get('NUKE_GIZMO_PATH', '').split(os.pathsep)
            if not searchPaths:
                import inspect
                thisFile = inspect.getsourcefile(lambda: None)
                if thisFile:
                    searchPaths = [os.path.dirname(os.path.abspath(thisFile))]
                else:
                    searchPaths = list(nuke.pluginPath())
        self.searchPaths = searchPaths
        self.reset()
        
    @classmethod
    def canonical_path(cls, path):
        return os.path.normcase(os.path.normpath(os.path.realpath(os.path.abspath(path))))
        
    def reset(self):
        self._crawlData = {}
        
    def addGizmoPaths(self):
        '''Recursively search searchPaths for folders to add to the nuke
        pluginPath.
        '''
        self.reset()
        self._visited = set()
        for gizPath in self.searchPaths:
            self._recursiveAddGizmoPaths(gizPath, self._crawlData,
                                         foldersOnly=True)
            
    def _recursiveAddGizmoPaths(self, folder, crawlData, foldersOnly=False):
        # If we're in GUI mode, also store away data in _crawlDatato to be used
        # later by addGizmoMenuItems
        if not os.path.isdir(folder):
            return
        
        if nuke.GUI:
            if 'files' not in crawlData:
                crawlData['gizmos'] = []
            if 'dirs' not in crawlData:
                crawlData['dirs'] = {}

        # avoid an infinite loop due to symlinks...
        canonical_path = self.canonical_path(folder)
        if canonical_path in self._visited:
            return
        self._visited.add(canonical_path)
        
        for subItem in sorted(os.listdir(canonical_path)):
            if self.exclude and self.exclude.search(subItem):
                continue
            subPath = os.path.join(canonical_path, subItem)
            if os.path.isdir(subPath):
                nuke.pluginAppendPath(subPath)
                subData = {}
                if nuke.GUI:
                    crawlData['dirs'][subItem] = subData
                self._recursiveAddGizmoPaths(subPath, subData)
            elif nuke.GUI and (not foldersOnly) and os.path.isfile(subPath):
                name, ext = os.path.splitext(subItem)
                if ext == '.gizmo':
                    crawlData['gizmos'].append(name)
                    
    def addGizmoMenuItems(self, toolbar=None, defaultTopMenu=None):
        '''Recursively create menu items for gizmos found on the searchPaths. Only call this if you're in nuke GUI mode! (ie, from inside menu.py)
        
        toolbar - the toolbar to which to add the menus; defaults to 'Nodes'
        defaultTopMenu - if you do not wish to create new 'top level' menu items,
            then top-level directories for which there is not already a top-level
            menu will be added to this menu instead (which must already exist)
        '''        
        if not self._crawlData:
            self.addGizmoPaths()
            
        if toolbar is None:
            toolbar = nuke.menu("Nodes")
        elif isinstance(toolbar, basestring):
            toolbar = nuke.menu(toolbar)
        self._recursiveAddGizmoMenuItems(toolbar, self._crawlData, CUSTOM_GIZMO_LOCATION, defaultSubMenu=defaultTopMenu, topLevel=True)
    
    def _recursiveAddGizmoMenuItems(self, toolbar, crawlData, currentDir, defaultSubMenu=None, topLevel=False):
        for name in crawlData.get('gizmos', ()):
            niceName = name
            if niceName.find('_v')==len(name) - 4:
                niceName = name[:-4]
            toolbar.addCommand(niceName,"nuke.createNode('%s')" % name, icon=name+".png")
            
        for folder, data in crawlData.get('dirs', {}).iteritems():
            import sys
            subMenu = toolbar.findItem(folder)
            if subMenu is None:
                if defaultSubMenu:
                    subMenu = toolbar.findItem(defaultSubMenu)
                else:
                    if topLevel:
                    	subMenu = toolbar.addMenu (folder, folder + '.png')
                    else:
                    	subMenu = toolbar.addMenu(folder, icon= folder + '.png')
            self._recursiveAddGizmoMenuItems(subMenu, data, currentDir + '' + subMenu.name())
                    
if __name__ == '__main__':
    if CUSTOM_GIZMO_LOCATION and os.path.isdir(CUSTOM_GIZMO_LOCATION):
        gizManager = GizmoPathManager(searchPaths=[CUSTOM_GIZMO_LOCATION])
    else:
        gizManager = GizmoPathManager()
    gizManager.addGizmoPaths()
    if not nuke.GUI:
        # We're not gonna need it anymore, cleanup...
        del gizManager












'''
wavePanel v1.4 by falk Hofmann 2013
Falk@Kombinat-13b.de
www.kombinat-13b.de

import wavePanel
menu=nuke.menu("Nuke")
mb=menu.addMenu( "Custom Menu" )
mb.addCommand ( "wavePanel v1.4", 'wavePanel.go()', icon="wavePanel.png" )
'''

import nuke 
import nukescripts
import os

class wavePanel ( nukescripts.PythonPanel ):

    nukePath = os.path.normpath(os.path.expanduser('~/.nuke/_icons/_wavePanel/'))      

    def __init__  ( self ):
     
        newPanel = nukescripts.PythonPanel.__init__ ( self , 'wavePanel' , 'wavePanel' )
        self.setMinimumSize(700, 700)
        
        self.cb = nuke.Boolean_Knob
        self.tab = nuke.Tab_Knob
        button = nuke.PyScript_Knob
        self.txt = nuke.Text_Knob
        self.pos = nuke.XY_Knob
        self.scale = nuke.WH_Knob
        self.slider = nuke.Double_Knob
        self.integer = nuke.Int_Knob
        add = self.addKnob

        
        
### build Wave Tab ### 

        curves = self.tab ('waves')
        self.waveList = ['sine' , 
                   'square' ,
                   'triangle' ,
                   'random' , 
                   'noise' , 
                   'bounce' , 
                   'sawtooth' ,  
                   'sawtoothParabolic' ,
                   'sawtoothParabolicReversed' , 
                   'sawtoothExponential'  ]
        add(curves)
        
        for i in self.waveList:
            path = self.nukePath + '\\' + 'w_' + i
            iconPath =  '<img src="%s">' % path
            temp = button (i,  iconPath  )
            descr = self.txt (i, 'add %s tab' % i)
            sep = self.txt ('')
            add (descr)
            add (temp)
            add (sep) 
            

            
### build Blip Tab ###

        blip = self.tab ('blip')
        add(blip)
        self.blipList = [
                        'singlePulse'
                         ]

        for i in self.blipList:
            path = self.nukePath + '\\' + 'b_' + i
            iconPath =  '<img src="%s">' % path
            temp = button (i,  iconPath  )
            descr = self.txt (i, 'add %s tab' % i)
            sep = self.txt ('')
            add (descr)
            add (temp)
            add (sep) 
            
            
### build Graphics Tab ###
            
        graphics = self.tab ('graphics')
        add(graphics)
        self.graphList = ['Circle' ,
                            'Hypocycloid' ,
                            'Lemniscate' ,
                            'Lissajous' ,
                            'Rose' , 
                            'Spiral' ]

        for i in self.graphList:
        
            path = self.nukePath + '\\' + 'g_' + i
            iconPath =  '<img src="%s">' % path
            temp = button (i,  iconPath  )
            descr = self.txt (i, 'add %s tab' % i)
            sep = self.txt ('')
            add (descr)
            add (temp)
            add (sep) 
            

### build Info Tab ###
           
        info = self.tab ('info')
        add ( info )
        
        info = self.txt ( '@b;wave Panel v1.4' )
        infoA = self.txt ( 'suggestions,  critique or similar are very welcome.')
        infoA.setFlag(nuke.STARTLINE)
        infoB = self.txt ( 'Falk Hofmann  05_2013' )
        infoB.setFlag(nuke.STARTLINE)
        infoC = self.txt ( 'Falk@Kombinat-13b.de')
        infoC.setFlag(nuke.STARTLINE)
        
        add ( info )
        add ( infoA )
        add ( infoB )
        add ( infoC )
                        


    def knobChanged ( self,  k ):

        if k.name() in self.waveList:
            self.createWaveTab (k.name())
            
        if k.name() in self.blipList:
            self.createBlipTab (k.name())
            
        if k.name() == 'Circle':
            self.createCircleTab ()

        if k.name() == 'Spiral':
            self.createSpiralTab ()

        elif k.name() == 'Rose':
            self.createRoseTab ()        

        elif k.name() == 'Hypocycloid':
            self.createhypoTab ()
        
        elif k.name() == 'Lemniscate':
            self.createLemniTab ()

        elif k.name() == 'Lissajous':
            self.createLissaTab ()

            

    def createWaveTab ( self, wave):

        math = {'sine' : '(((sin(((frame*(pi*2/(this.frequency_%s)/2))/2)+this.offset_%s))+1)/2) * (this.max_%s-this.min_%s)  + this.min_%s' %(wave, wave, wave, wave, wave),
                      'square' : '((((sin(((frame*(pi*2/(this.frequency_%s/2))/2)+this.offset_%s))+1)/2) *(this.max_%s-this.min_%s) ) + this.min_%s) > ((this.max_%s/2)+(this.min_%s/2)) ? this.max_%s : this.min_%s' %(wave, wave, wave, wave, wave, wave, wave, wave, wave),
                      'triangle' : '(((((2*asin(sin(2*pi*(frame/this.frequency_%s)+this.offset_%s)))/pi) / 2)+0.5) * (this.max_%s-this.min_%s) ) + this.min_%s' %(wave, wave, wave, wave, wave),
                      'random' : '((random(((frame)/this.frequency_%s)+this.offset_%s)) * (this.max_%s-this.min_%s) ) + this.min_%s' %(wave, wave, wave, wave, wave),
                      'noise' : '(((1*(noise((frame/this.frequency_%s)+this.offset_%s))+1 ) /2 ) * (this.max_%s-this.min_%s) ) + this.min_%s' %(wave, wave, wave, wave, wave),
                      'bounce' :  '((sin(((frame/this.frequency_%s)*pi)+this.offset_%s)>0?sin(((frame/this.frequency_%s)*pi)+this.offset_%s):cos((((frame/this.frequency_%s)*pi)+this.offset_%s)+(pi/2))) * (this.max_%s-this.min_%s) ) + this.min_%s' %(wave, wave, wave, wave, wave, wave, wave, wave, wave),
                      'sawtooth' : '((1/this.frequency_'+wave+')*(((frame-1)+this.offset_' + wave + ') % this.frequency_' + wave + ') *(this.max_' + wave + '-this.min_' + wave + ') ) + this.min_' + wave,
                      'sawtoothParabolic' : '((sin((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/2.46666666)) % (pi/2)))>0.99999? 1 : (sin((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/2.46666666)) % (pi/2))) * (this.max_' + wave + '-this.min_' + wave + ') ) + this.min_' + wave,
                      'sawtoothParabolicReversed' : '((cos((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/2.46666666)) % (pi/2)))>0.99999? 1 : (cos((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/2.46666666)) % (pi/2))) * (this.max_' + wave + '-this.min_' + wave + ') ) + this.min_' + wave,
                      'sawtoothExponential' :'((((((exp((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/4.934802)) % pi*2)))/534.5)) - 0.00186741)>0.999987? 1 : (((((exp((1/(pi/2))*(((frame-1)+this.offset_' + wave + ')/(this.frequency_' + wave + '/4.934802)) % pi*2)))/534.5)) - 0.00186741) * (this.max_' + wave + '-this.min_' + wave + ') ) + this.min_' + wave
                      }

        n = nuke.selectedNode()

        sep = self.txt('')
        tabName = wave +'_wave'
        waveTab = self.tab (tabName, tabName)

        waveEx = math [str(wave)]

        min = self.slider ( 'min_' + wave, 'min' ) 
        max = self.slider ( 'max_' + wave , 'max' ) 
        max.setValue ( 1 )

        frequency = self.slider ( 'frequency_' + wave , 'frequency' )
        frequency.setRange(1,100)
        frequency.setValue ( 5 )

        offset = self.slider ( 'offset_' + wave , 'Horizontal offset')
        offset.setRange(1,100)

        result = self.slider (str(wave)+ 'Wave', str(wave) + 'Wave')
        result.setExpression (waveEx)
             
        n.addKnob(waveTab)
        n.addKnob(min)
        n.addKnob(max)
        n.addKnob(frequency)
        n.addKnob(offset)
        n.addKnob(sep)
        n.addKnob(result)
        n['label'].setValue(wave)

    
    def createBlipTab ( self, blip ):
        math = { 'singlePulse' : 'frame % (abs(every_' + blip + ')) ==  blipAt_' + blip + '? on_' + blip + ':off_' + blip 
                }
        n = nuke.selectedNode()
        
        sep = self.txt('')
        tabName = blip + '_blip'
        blipTab = self.tab (tabName, tabName)

        blipEx = math [str(blip)]

        blink = self.integer ( 'blipAt_' + blip , 'blip at frame' )
        blink.setValue ( 1 )
        
        every = self.integer ( 'every_' + blip , 'every...frames' )
        every.setValue( 10 )
 
        off = self.slider ( 'off_' + blip, 'off value' )
        on = self.slider ( 'on_' + blip , 'on value' )
        off.setValue ( 0 )        
        on.setValue ( 1 )
        
        result = self.slider (str(blip)+ 'blip', str(blip) + 'blip')
        result.setExpression (blipEx)
             
        n.addKnob(blipTab)
        n.addKnob(blink)
        n.addKnob(every)      
        n.addKnob(off)
        n.addKnob(on)
        n.addKnob(sep)
        n.addKnob(result)
        n['label'].setValue(blip)   
        
        
    def createCircleTab ( self ):
    
        n = nuke.selectedNode()
        CircleTab = self.tab ( 'CircleTab' , 'Circle Tab' )
        scale = self.scale ( 'scale_circle' , 'scale' )
        offset = self.pos ( 'offset_circle' , 'Offset') 
        fc = self.slider ( 'fc_circle' , 'Frame Cycle' )
        velo = self.slider ( 'velo_circle' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'circle' , 'circle' )

        n.addKnob( CircleTab )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( fc )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )

        scale.setValue ( 300 )
        offset.setValue ( 800 )
        fc.setValue ( 90 )
        velo.setValue ( 2 )
        result.setExpression ( 'offset_circle.x+scale_circle.h*sin((frame*velo_circle*acos(-1))/fc_circle)' , 0 )
        result.setExpression ( 'offset_circle.y+scale_circle.w*cos((frame*velo_circle*acos(-1))/fc_circle)' , 1 )
        n['label'].setValue('CircleTab')



    def createSpiralTab ( self ) :

        n = nuke.selectedNode()
        SpiralTab = self.tab ( 'SpiralTab' , 'Spiral Tab' )
        scale = self.scale ( 'scale_spiral' , 'scale' )
        offset = self.pos ( 'offset_spiral' , 'Offset') 
        spiral = self.slider ( 'spiral_spiral' , 'Spiral' )
        velo = self.slider ( 'velo_spiral' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'spiral' , 'spiral' )

        n.addKnob( SpiralTab )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( spiral )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )

        scale.setValue ( 3 )
        offset.setValue ( 800 )
        spiral.setValue ( 60 )
        velo.setValue ( 10 )
        result.setExpression ( '(scale_spiral.w*frame*cos(frame*acos(-1)*velo_spiral/spiral_spiral))+offset_spiral.x' , 0 )
        result.setExpression ( '(scale_spiral.h*frame*sin(frame*acos(-1)*velo_spiral/spiral_spiral))+offset_spiral.y' , 1 )
        n['label'].setValue('SpiralTab')
            
            
            
    def createRoseTab ( self ) :

        n = nuke.selectedNode()
        RoseTab = self.tab ( 'RoseTab' , 'Rose Tab' )
        loops = self.slider ( 'loops_rose' , 'Loops' )
        scale = self.scale ( 'scale_rose' , 'scale' )
        offset = self.pos ( 'offset_rose' , 'Offset') 
        fc = self.slider ( 'fc_rose' , 'Frame Cycle' )
        velo = self.slider ( 'velo_rose' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'rose' , 'rose' )

        n.addKnob( RoseTab )
        n.addKnob ( loops )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( fc )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )

        loops.setValue ( 5 )
        scale.setValue ( 300 )
        offset.setValue ( 800 )
        fc.setValue ( 90 )
        velo.setValue ( 2 )
        result.setExpression ( '(cos((frame*velo_rose*acos(-1)/fc_rose))-cos((loops_rose-1)*(frame*velo_rose*acos(-1)/fc_rose)))*scale_rose.w+offset_rose.x' , 0 )
        result.setExpression ( '(sin((frame*velo_rose*acos(-1)/fc_rose))+sin((loops_rose-1)*(frame*velo_rose*acos(-1)/fc_rose)))*scale_rose.h+offset_rose.y' , 1 )
        n['label'].setValue('RoseTab')

            
    def createLissaTab ( self ):

        n = nuke.selectedNode()
        LissaTab = self.tab ( 'LissaTab' , 'Lissajous Tab' )
        freq = self.pos ( 'freq_lissa' , 'Frequency' )
        scale = self.scale ( 'scale_lissa' , 'scale' )
        offset = self.pos ( 'offset_lissa' , 'Offset') 
        fc = self.slider ( 'fc_lissa' , 'Frame Cycle' )
        velo = self.slider ( 'velo_lissa' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'lissa' , 'lissa' )

        n.addKnob( LissaTab )
        n.addKnob ( freq )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( fc )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )

        freq.setValue ( 7 , 0 )
        freq.setValue ( 5 , 1 )
        scale.setValue ( 300 )
        offset.setValue ( 800 )
        fc.setValue ( 90 )
        velo.setValue ( 2 )
        result.setExpression ( 'scale_lissa.w*cos(freq_lissa.x*frame*velo_lissa*acos(-1)/fc_lissa)+offset_lissa.x' , 0 )
        result.setExpression ( 'scale_lissa.h*sin(freq_lissa.y*frame*velo_lissa*acos(-1)/fc_lissa)+offset_lissa.y' , 1 )
        n['label'].setValue('LissaTab')



    def createhypoTab ( self ):
    
        n = nuke.selectedNode()
        hypoTab = self.tab ( 'HypoTab' , 'Hypocycloid Tab' )
        points = self.slider ( 'points_hypo' , 'Points' )
        scale = self.scale ( 'scale_hypo' , 'scale' )
        offset = self.pos ( 'offset_hypo' , 'Offset') 
        fc = self.slider ( 'fc_hypo' , 'Frame Cycle' )
        velo = self.slider ( 'velo_hypo' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'hypo' , 'hypo' )  

        n.addKnob( hypoTab )
        n.addKnob ( points )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( fc )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )

        points.setValue ( 10 )
        scale.setValue ( 300 )
        offset.setValue ( 800 )
        fc.setValue ( 90 )
        velo.setValue ( 2 )
        result.setExpression ( '((scale_hypo.w/points_hypo)*((points_hypo -1)*cos((frame*velo_hypo*acos(-1)/fc_hypo))+cos((points_hypo-1)*(frame*velo_hypo*acos(-1)/fc_hypo)))+offset_hypo.x)' , 0 )
        result.setExpression ( '((scale_hypo.h/points_hypo)*((points_hypo-1)*sin((frame*velo_hypo*acos(-1)/fc_hypo))+sin((points_hypo-1)*(frame*velo_hypo*acos(-1)/fc_hypo)))+offset_hypo.y)' , 1 )      
        n['label'].setValue('hypoTab')


    def createLemniTab ( self ):
    
        n = nuke.selectedNode()
        LemniTab = self.tab ( 'LemniTab' , 'Lemniscate Tab' )
        scale = self.scale ( 'scale_lemni' , 'scale' )
        offset = self.pos ( 'offset_lemni' , 'Offset')    
        fc = self.slider ( 'fc_lemni' , 'Frame Cycle' )
        velo = self.slider ( 'velo_lemni' , 'Velocity' )
        sep = self.txt ('' )
        result = self.pos ( 'lemni' , 'lemni' )  

        n.addKnob( LemniTab )
        n.addKnob ( scale )
        n.addKnob ( offset )
        n.addKnob ( fc )
        n.addKnob ( velo )
        n.addKnob ( sep )
        n.addKnob ( result )  

        scale.setValue ( 300 )
        offset.setValue ( 800 )
        fc.setValue ( 60 )
        velo.setValue ( 1.2 )
        result.setExpression ('scale_lemni.w*cos((frame*velo_lemni*acos(-1)/fc_lemni))/(1+sin((frame*velo_lemni*acos(-1)/fc_lemni))*sin((frame*velo_lemni*acos(-1)/fc_lemni)))+offset_lemni.x' , 0 )
        result.setExpression ( '(scale_lemni.h*sin((frame*velo_lemni*acos(-1)/fc_lemni))*2*cos((frame*velo_lemni*acos(-1)/fc_lemni)))/(1+sin((frame*velo_lemni*acos(-1)/fc_lemni))*sin((frame*velo_lemni*acos(-1)/fc_lemni)))+offset_lemni.y ' , 1 )        
        n['label'].setValue('LemniTab')
		
		
def go():
    wP = wavePanel()
    wP.showModalDialog()

nuke.pluginAddPath("breakdown")

nuke.pluginAddPath('capture')


nuke.pluginAddPath('pixelfudger')






## init.py
## loaded by nuke before menu.py

nuke.pluginAddPath("./Gizmos")
nuke.pluginAddPath("./icons")
nuke.pluginAddPath("./pythons")







def exrCam():  
	def getMetadataMatrix(meta_list):
	  m = nuke.math.Matrix4()
	  try: 
		  for i in range(0,16):
			  m[i] = meta_list[i]   
	  except:
		  m.makeIdentity()
	  return m
 
	n=nuke.thisNode()
 
	hold=int(n['frameHold'].value())
 
	camMatrix = getMetadataMatrix(n.metadata('exr/worldToCamera',hold))
 
	flipZ=nuke.math.Matrix4()
	flipZ.makeIdentity()
	flipZ.scale(1,1,-1)
 
	transposedMatrix = nuke.math.Matrix4(camMatrix)
	transposedMatrix.transpose()
	transposedMatrix=transposedMatrix*flipZ
	invMatrix=transposedMatrix.inverse()	
 
	n['matrix'].setValue(invMatrix[0],0)
	n['matrix'].setValue(invMatrix[1],1)
	n['matrix'].setValue(invMatrix[2],2)
	n['matrix'].setValue(invMatrix[3],3)
	n['matrix'].setValue(invMatrix[4],4)
	n['matrix'].setValue(invMatrix[5],5)
	n['matrix'].setValue(invMatrix[6],6)
	n['matrix'].setValue(invMatrix[7],7)
	n['matrix'].setValue(invMatrix[8],8)
	n['matrix'].setValue(invMatrix[9],9)
	n['matrix'].setValue(invMatrix[10],10)
	n['matrix'].setValue(invMatrix[11],11)
	n['matrix'].setValue(invMatrix[12],12)
	n['matrix'].setValue(invMatrix[13],13)
	n['matrix'].setValue(invMatrix[14],14)
	n['matrix'].setValue(invMatrix[15],15)
	return

