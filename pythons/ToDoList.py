import os
import sys
import time
from xml.etree import ElementTree as ET
from PySide import QtGui, QtCore, QtNetwork
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

## written by Frank Rueter with (lots of) help from Aaron Richiger


class NukeError(Exception):

    def __str__(self):
        return '''This is the ol' "A PythonObject is not attached to a node" error that we need to work around for now'''

class Task(object):
    '''
    Model for a task. Task attributes are:
       name - short description of the task
       priority - integer
       status - float (0 > waiting to start, 1 > finished)
    '''

    def __init__(self, name='new task', priority=1, status=0):
        self.name = name
        self.priority = priority
        self.status = status
        self.index = 0
        
    def setName(self, name):
        self.name = name

    def setPriority(self, priority):
        self.priority = priority
        
    def setStatus(self, status):
        self.status = status
        
    def __repr__(self):
        return 'Task(name=%s, priority=%D, status=%d' % (self.index, self.name)
    
    def __str__(self):
        return '-' * 20 + '\np%s:\t\t%s\t\t (%s)' % (self.priority, self.name, ['waiting', 'in progress', 'finished'][self.status])

class TaskStore(QtCore.QObject):
    '''Stores, filters, sorts and delivers all tasks'''
    
    def __init__(self, tasksFile):
        super(TaskStore, self).__init__()
        self.initStore(tasksFile)
        
    def initStore(self, tasksFile):
        '''initialise the task store making sure all tasks are prepared the way we need them'''
        
        #print 'initialising store'
        self.setTasksFile(tasksFile)
        self.loadTasks()
        self.resetTasks()
        
    def setTasksFile(self, tasksFile):
        '''set the file that holds the task data'''
        
        self.tasksFile = tasksFile

    def addTask(self):
        '''Insert a new task into the task store'''

        newTask = Task()
        self.tasks.insert(0, newTask)
        return newTask

    def deleteTask(self):
        taskToDelete = self.sender().parent().task
        taskToDelete.index = -2
        self.tasks = [task for task in self.tasks if taskToDelete != task]
        self.resetTasks()

    def loadTasks(self):
        '''Try to load tasks from disk. If no tasks have been saved return default data'''
    
        if self.tasksFile and os.path.isfile(self.tasksFile):
            tree = ET.parse(self.tasksFile)
            root = tree.getroot()
            taskElements = root.findall('Task')
            if not taskElements:
                # NO TASKS WERE SAVED
                return [Task()]

            taskList = []
            for te in taskElements:
                task = Task(name=te.findtext('name'),
                            priority=int(te.findtext('priority')),
                            status=int(te.findtext('status')))
                taskList.append(task)
        else:
            # NO SETTINGS FILE FOUND
            taskList = [Task()]
        
        self.tasks = taskList

    def resetTasks(self):
        '''Assign an index from 1..n to all tasks in the store'''

        for i, task in enumerate(self.tasks):
            task.index = i
    def filterFinished(self, hideFinished):
        '''Hide finished tasks by assigning a negative index'''
        
        for task in self.tasks:
            if hideFinished and task.status == 2:
                task.index = -1
                
    def sortByPriority(self, active):
        '''Sort tasks by their priority by assigning a corresponding index'''
        sortedTasks = sorted([t for t in self.tasks if t.index >= 0], key=lambda task: task.priority)
        if active:
            # sort highest first
            sortedTasks.reverse()

        for i, task in enumerate([t for t in sortedTasks if t.index >= 0]):
            task.index = i


########## VIEW CLASSES ###########################################################################
class DragIndicator(QtGui.QWidget):
    def __init__(self, parent=None):
        '''mini widget to display on mouse over on PriorityWidget to indicate dragability'''
        super(DragIndicator, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def sizeHint(self):
        return QtCore.QSize(self.parentWidget().width(), self.parentWidget().height()/6)
   
    def paintEvent(self, event):
        '''Paint the button grey if not highlighted, else yellow'''

        painter = QtGui.QPainter(self)
        colour = QtGui.QColor(247, 147, 30, 150)
        gradient = QtGui.QLinearGradient(QtCore.QPoint(0,0), QtCore.QPoint(self.width()/2, 0))
        gradient.setColorAt(0, QtCore.Qt.transparent)
        gradient.setColorAt(1, colour)
        gradient.setSpread(QtGui.QGradient.ReflectSpread)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtCore.Qt.transparent)
        rect = QtCore.QRect(0,0,self.width(),self.height())
        painter.drawRect(rect)

 
class TaskWidget(QtGui.QWidget):
    '''Widget to show a single task'''
    TASKWIDGETWIDTH = 400
    TASKWIDGETHEIGHT = 40
    TASKWIDGETSPACING = 1.05
    newTaskSignal = QtCore.Signal()

    def __init__(self, task, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.task = task
        self.setupUi()

    def setupUi(self):
        self.setAutoFillBackground(True)
        hLayout = QtGui.QHBoxLayout(self)
        self.setLayout(hLayout)
        self.taskNameWidget = QtGui.QLineEdit(self.task.name)
        self.priorityWidget = PriorityWidget()
        self.priorityWidget.setValue(self.task.priority)
        self.statusWidget = StatusWidgetBar()
        self.statusWidget.setCurrentIndex(self.task.status)
        self.deleteWidget = DeleteWidget('delete')

        hLayout.addWidget(self.taskNameWidget)
        hLayout.addWidget(self.priorityWidget)
        hLayout.addWidget(self.statusWidget)
        hLayout.addWidget(self.deleteWidget)

    def update(self):
        '''Resize this widget to use full width'''
        super(TaskWidget, self).update()
        self.resize(self.parent().width(), TaskWidget.TASKWIDGETHEIGHT)

    def getNewPosition(self):
        '''Return the position of this task widget according to the index of its task'''

        x = 0        
        if self.task.index >= 0:
            # VISIBLE WIDGETS MOVE UP TO FILL SPACE
            y = self.task.index * TaskWidget.TASKWIDGETHEIGHT * TaskWidget.TASKWIDGETSPACING 
        elif self.task.index == -1:
            # HIDDEN WIDGETS MOVE UP
            y = self.task.index * self.height()
            self.raise_()
        elif self.task.index == -2:
            # DELETED WIDGETS DROP DOWN
            y = self.parentWidget().height()
            self.raise_()

        return QtCore.QPoint(x, y)
    def keyPressEvent(self, event):
        '''send newTaskSignal if shit+return is pressed'''
        
        if event.key() == QtCore.Qt.Key_Return and (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.newTaskSignal.emit()
        else:
            super(TaskWidget, self).keyPressEvent(event)

class PriorityWidget(QtGui.QLabel):
    valueChanged = QtCore.Signal(int)
    allowSorting = QtCore.Signal()

    def __init__(self, parent=None):
        super(PriorityWidget, self).__init__(parent)
        self.color = QtGui.QColor(247, 147, 30, 255)
        self.font = QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold)
        self.setToolTip('<b>priority</b><br>use either:<ul><li>LMB to increase  -  RMB to decrease</li><li>alt+LMB drag to change value</li><li>MMB drag to change value</li></ul><i>move mouse away after changing value<br>to trigger re-sorting</i>')
        self.active = False
        self.mouseOver = False
        self.value = 0
        self.allowDrag = False
        self.setFocusPolicy(QtCore.Qt.TabFocus)
        self.indicator = DragIndicator(self)
        self.indicator.setVisible(False)
        self.indicator.move(0, 15)

    def minimumSizeHint(self):
        return (QtCore.QSize(50,25))

    def setValue(self, value):
        self.value = value
        self.valueChanged.emit(self.value)
        self.update()

    def paintEvent(self, event):
        '''Paint the custom look'''

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.HighQualityAntialiasing)
        painter.setFont(self.font)
        
        if self.mouseOver:
            self.indicator.setVisible(True)
        else:
            self.indicator.setVisible(False)

        if (self.active or self.hasFocus()) and not self.mouseOver:
            # when keyboard has shifted focus onto this widget
            painter.setPen(self.color.lighter())

        else:
            painter.setPen(self.color)

        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, str(self.value))

    def keyPressEvent(self, event):
        '''add arrow keys as means to change value'''
        if event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Down):
            self.setValue(self.value - 1)
        elif event.key() in (QtCore.Qt.Key_Right, QtCore.Qt.Key_Up):
            self.setValue(self.value + 1)
        else:
            super(PriorityWidget, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if ((event.modifiers() == QtCore.Qt.AltModifier) and (event.button() == QtCore.Qt.MouseButton.LeftButton)) or\
           (event.button() == QtCore.Qt.MouseButton.MiddleButton):
            self.allowDrag = True
            self.clickPosition = event.pos()
            self.oldValue = self.value
        elif event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.setValue(self.value + 1)
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.setValue(self.value - 1)
        
    def mouseReleaseEvent(self, event):
        self.allowDrag = False

    def mouseMoveEvent(self, event):
        if self.allowDrag:
            newValue = self.oldValue + (event.pos().x() - self.clickPosition.x()) / 50
            self.setValue(newValue)
            self.valueChanged.emit(newValue)

    def wheelEvent(self, event):
        '''this seems to be eaten by nuke's parent widget'''
        #print event
        pass
        
    def enterEvent(self, event):
        self.active = True
        self.mouseOver = True
        self.update()

    def leaveEvent(self, event):
        self.active = False
        self.mouseOver = False
        self.clearFocus()
        self.allowSorting.emit()
    
    def focusOutEvent(self, event):
        self.allowSorting.emit()

class StatusWidgetPie(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(StatusWidgetPie, self).__init__(parent)
        self.setToolTip('status (click to edit)')
        self.addItems(['waiting', 'in progress', 'finished'])
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.size = QtCore.QSize(20, 20)

    def sizeHint(self):
        return self.size

    def minimumSizeHint(self):
        return self.size
    
    def maximumSizeHint(self):
        return self.size 

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        parent = self.parentWidget()

        pieRect = QtCore.QRect(1, 1, self.width()-2, self.height()-2)
        startAngle = 0 * 16

        if self.currentIndex() == 0:
            # STATUS = WAITING
            painter.drawEllipse(pieRect)
        elif self.currentIndex() == 1:
            # STATUS = IN PROGGRESS
            painter.setPen(QtGui.QColor(0,0,0,0))
            painter.setBrush(QtGui.QColor(255, 140, 30))
            startAngle = 90 * 16
            spanAngle = self.currentIndex() * 270 * 16
            painter.drawPie(pieRect, startAngle, spanAngle)
        elif self.currentIndex() == 2:
            # STATUS = FINISHED
            painter.setPen(QtGui.QColor(0,0,0,0))
            painter.setBrush(QtGui.QColor('darkGreen'))
            spanAngle = self.currentIndex() * 360 * 16
            painter.drawPie(pieRect, startAngle, spanAngle)

class StatusWidgetBar(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(StatusWidgetBar, self).__init__(parent)
        self.setToolTip('<b>status</b><br>click to edit')
        self.addItems(['waiting', 'in progress', 'finished'])
        self.active = False
        self.colWaiting = QtGui.QColor(180, 100, 10)
        self.colInProgress = QtGui.QColor(255, 140, 30)
        self.colFinished = QtGui.QColor('darkGreen')
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        currentIndex = self.currentIndex()
        painter.setPen(QtGui.QColor(0,0,0,0))

        if currentIndex == 0:
            progress =  .1
            if self.active or self.hasFocus():
                painter.setBrush(self.colWaiting.lighter())
            else:
                painter.setBrush(self.colWaiting)
        elif currentIndex == 1:
            progress = .6
            if self.active or self.hasFocus():
                painter.setBrush(self.colInProgress.lighter())
            else:
                painter.setBrush(self.colInProgress)
        elif currentIndex == 2:
            progress = 1
            if self.active or self.hasFocus():
                painter.setBrush(self.colFinished.lighter())
            else:
                painter.setBrush(self.colFinished)
        barRect = QtCore.QRect(0, self.height() * .25, (self.width()) * progress, self.height() * .5)
        painter.drawRect(barRect)
        
        outline = QtCore.QRect(1, self.height() * .25, (self.width())-2, self.height() * .5)
        painter.setBrush(QtGui.QColor(0,0,0,0))
        painter.setPen(QtGui.QColor(0,0,0,255))
        painter.drawRect(outline)

    def enterEvent(self, event):
        self.active = True
        
    def leaveEvent(self, event):
        self.active = False
        self.clearFocus()
    
    def mouseReleaseEvent(self, event):
        self.active = False
        super(StatusWidgetBar, self).mouseReleaseEvent(event)
        self.update()
        

class DeleteWidget(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(DeleteWidget, self).__init__(parent)
        self.size = QtCore.QSize(20, 20)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setToolTip('permanently delete this task')
        self.padding = 7
        self.active = False
        self.inactiveColor = QtGui.QColor(180, 50, 0)
        self.activeColor = self.inactiveColor.lighter()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = painter.pen()
        if self.active or self.hasFocus():
            pen.setColor(self.activeColor)
        else:
            pen.setColor(self.inactiveColor)
        pen.setWidth(3)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)        
        polygon1 = QtGui.QPolygon()
        polygon1 << QtCore.QPoint(self.padding, self.padding) << QtCore.QPoint(self.width() - self.padding, self.height() - self.padding)
        polygon2 = QtGui.QPolygon()
        polygon2 << QtCore.QPoint(self.padding,self.height() - self.padding) << QtCore.QPoint(self.width() - self.padding, self.padding)

        polygon1.translate(0,1)
        polygon2.translate(0,1)
        painter.drawPolyline(polygon1)
        painter.drawPolyline(polygon2)

    def enterEvent(self, event):
        self.active = True
        
    def leaveEvent(self, event):
        self.active = False
        self.clearFocus()

    def sizeHint(self):
        return self.size

    def minimumSizeHint(self):
        return self.size
    
    def maximumSizeHint(self):
        return self.size 


class MainWindow(QtGui.QWidget):
    '''GUI to show and edit multiple tasks'''
    appName = 'com.ohufx.ToDoList'
    def __init__(self, parent=None):
        self._closeRunningInstances()
        super(MainWindow, self).__init__(parent)

        self.setObjectName(self.appName)
        self.setWindowTitle('To Do List')
        self.inNuke = inNuke()
        self.inHiero = inHiero()
        self.animGroupsDeleted = [] # HOLD ANIMATIONS FOR DELETED WIDGETS - REQUIRED FOR OVERLAPPING DELETE ACTIONS
        self.settingsFile = ''
        self.warningText = ''
        self.setSettingsFile()
        self.taskStore = TaskStore(self.settingsFile)
        self.setupUI()
        self.loadSettings()
        self.controller()

    def __str__(self):
        return 'OHUfx ToDoList Widget'



    def setupUI(self):
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.msg = QtGui.QLabel()

        self.addTaskButton = QtGui.QPushButton('Add Task')
        self.addTaskButton.setToolTip('Add a new task to the list')
        self.sortButton = QtGui.QPushButton('Reverse Sorting')
        self.sortButton.setCheckable(True)
        self.sortButton.setToolTip('Push to sort so highest priorities are at the top,\notherwise lowest will be at the top.')
        self.helpButton = QtGui.QPushButton('?')
        self.helpButton.setMaximumWidth(30)
        self.helpButton.setFlat(True)
        self.helpButton.setToolTip(self.__helpText())
        self.hideButton = QtGui.QPushButton('Hide Finished Tasks')
        self.hideButton.setCheckable(True)
        self.hideButton.setToolTip('Hide finished tasks to keep the list tidy')      
        self.clipboardButton = QtGui.QPushButton('Copy To Clipboard')
        self.clipboardButton.setToolTip('Push to copy current task info to cliboard for pasting into emails or other text documents.\nHandy to keep those coordinators happy.')
        
        self.buttonLayout.addWidget(self.addTaskButton)
        self.buttonLayout.addWidget(self.sortButton)
        self.buttonLayout.addWidget(self.hideButton)
        self.buttonLayout.addWidget(self.clipboardButton)
        self.buttonLayout.addSpacing(20)
        self.buttonLayout.addWidget(self.helpButton)
        
        self.layout().addWidget(self.msg)
        self.layout().addLayout(self.buttonLayout)
       
        self.taskContainer = QtGui.QWidget()
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.taskContainer)
        self.layout().addWidget(self.scrollArea)
        self.createTaskWidgets()
        self.update()

    def createTaskWidgets(self):
        '''Create one task widget for every task found in current task store'''

        ## START OF NAUGHTY CODE
        # DELETE TASK CONTAINER AND SCROLL AREA SO WE CAN RE-CREATE THEM
        # FOR SOME REASON RE-USING THE EXISTING ONES DOES NOT SHOW THE TASK WIDGETS
        self.taskContainer.deleteLater()
        self.scrollArea.deleteLater()
        
        self.taskContainer = QtGui.QWidget()
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.taskContainer)
        self.layout().addWidget(self.scrollArea)
        ## END OF NAUGHTY CODE

        self.taskWidgets = [TaskWidget(t, self.taskContainer) for t in self.taskStore.tasks]
        self.update()

    def rebuildTaskWidgets(self):
        '''Reset all task data, get settings file and re-build task widgets accordingly'''

        # DELETE OLD TASK WIDGETS AND CLEAR INTERNAL LIST
        for oldWidget in self.taskWidgets:
            oldWidget.deleteLater()
        self.taskWidgets = []
        
        # GET NEW SETTINGS FILE
        self.setSettingsFile()
        
        # RE-INIT TASK STORE WITH NEW TASK SETTINGS
        self.taskStore.initStore(self.settingsFile)

        # LOAD PANEL SETTINGS
        self.loadSettings()

        # CREATE NEW TASK WIDGETS AND CONNECT THEIR SIGNALS
        self.createTaskWidgets()

        for tw in self.taskWidgets:
            self.connectTaskWidgetSignals(tw)
        
        self.setEnabledState()
        self.applyFilterAndSorting()
        self.update()

    def setSettingsFile(self):
        '''get the path to the xml file to read/write settings'''
        if self.inNuke:
            import nuke
            try:
                if nukeSetup():
                    # got nuke root successfully and script has been saved, so I can build path for settings file
                    self.settingsFile =  nuke.root()['todoSettingsFile'].value()
                else:
                    # do nothing. with no settings file set, the widget will deactivate themselve and display a warning that script needs to be saved first
                    pass
            except NukeError:
                # something went wrong, mostlikely NUke's bloody "ValueError: A PythonObject is not attached to a node"
                # this shouldn't be needed if it weren't for the above bug
                self.warningText = '<b>Oops, you have run into a little Nuke bug. Please close this panel and re-open it and everythign will be groovy'
                
        elif self.inHiero:
            # HIERO SUPPORT IS NOT FINISHED DUE TO LACK OF REQUIERED EVENT TYPES IN HIERO
            raise NotImplementedError
            import hiero.core
            if hieroSetup():
                self.settingsFile = [tag.metadata().value('tag.settingsFile') for tag in hiero.core.findProjectTags() if tag.name() == 'ohufx.ToDoList'][0]
        else:
            self.settingsFile = None

    def addTaskWidget(self, task):
        '''Add a new widget for task'''

        newTaskWidget = TaskWidget(task, parent=self.taskContainer)
        newTaskWidget.show()
        self.taskWidgets.append(newTaskWidget)
        return newTaskWidget

    def deleteTask(self):
        '''Delete a task'''
        self.taskWidgetToDelete = self.sender().parent()
        self.taskWidgets = [taskWidget for taskWidget in self.taskWidgets if self.taskWidgetToDelete != taskWidget]

    def deleteTaskWidget(self):
        '''remove deleted widgets to avoid surprises when rescaling the parent window'''
        sender = self.sender()
        deletedWidget = sender.animationAt(0).targetObject()
        deletedWidget.setParent(None)
        self.animGroupsDeleted.remove(sender) # JUST CLEANING UP, SHUOLDNT BE NECESSARY

    def loadSettings(self):
        '''Try to load sorting and filtering settings from disk. If nothing has been saved do nothing'''

        if self.settingsFile and os.path.isfile(self.settingsFile):
            logger.info('loading settings from %s' % self.settingsFile)
            tree = ET.parse(self.settingsFile)
            root = tree.getroot()
            settings = root.find('Settings')
            self.hideButton.setChecked(eval(settings.findtext('hideFinished')))
            self.sortButton.setChecked(eval(settings.findtext('sortState')))
        else:
            pass

    def saveSettingsAndTasks(self):
        '''Dump current sorting and filtering choices to disk for reloading'''
        if not self.settingsFile:
            logger.warning('no settings file found, nothing will be saved')
            return
        logger.info('saving task panel\'s settings to disk: %s' % self.settingsFile)
        settingsToBeSaved = {}
        settingsToBeSaved['hideFinished'] = str(self.hideButton.isChecked())
        settingsToBeSaved['sortState'] = str(self.sortButton.isChecked())

        root = ET.Element('ToDoPanel')
        settingsEle = ET.SubElement(root, 'Settings')
        for k, v in settingsToBeSaved.iteritems():
            settingEle = ET.SubElement(settingsEle, k)
            settingEle.text = v
        
        for task in self.taskStore.tasks:
            taskDict = task.__dict__
            tasksEle = ET.SubElement(root, 'Task')
            for k, v in taskDict.iteritems():
                taskEle = ET.SubElement(tasksEle, k)
                taskEle.text = str(v)

        tree = ET.ElementTree(root)
        tree.write(self.settingsFile)
              
    def copyToClipboard(self):
        sortedTasks = sorted([t for t in self.taskStore.tasks if t.index >= 0], key=lambda task: task.priority)
        if self.sortButton.isChecked():
            sortedTasks.reverse()

        clipboard = QtGui.QApplication.clipboard() 
        text = '\n'.join([str(t) for t in sortedTasks])
        clipboard.setText(text)
        
    def controller(self):
        '''Need this to be able to register the widget as panl inside of nuke (this won't work with the Controller class)'''

        self.connectSignalsWithSlots()
        self.applyFilterAndSorting()

    def onAddTask(self):
        '''Add a new task'''
        
        newTask = self.taskStore.addTask()
        newTaskWidget = self.addTaskWidget(newTask)
        newTaskWidget.taskNameWidget.setSelection(0, len(newTaskWidget.taskNameWidget.text()))
        newTaskWidget.taskNameWidget.setFocus(QtCore.Qt.FocusReason.ActiveWindowFocusReason)
        self.connectTaskWidgetSignals(newTaskWidget)
        self.applyFilterAndSorting()

    def applyFilterAndSorting(self):
        '''Filter and sort all tasks according to their settings, the update the view accordingly'''

        self.taskStore.resetTasks()
        self.taskStore.filterFinished(self.hideButton.isChecked())
        self.taskStore.sortByPriority(self.sortButton.isChecked())
        self.update()       

    def connectSignalsWithSlots(self):
        '''Connect the main window's widgets with their slots'''
        
        self.addTaskButton.clicked.connect(self.onAddTask)
        self.sortButton.clicked.connect(self.applyFilterAndSorting)
        self.sortButton.clicked.connect(self.saveSettingsAndTasks)
        self.hideButton.clicked.connect(self.applyFilterAndSorting)
        self.hideButton.clicked.connect(self.saveSettingsAndTasks)
        self.helpButton.clicked.connect(launchWebsite)
        self.clipboardButton.clicked.connect(self.copyToClipboard)
        for tw in self.taskWidgets:
            self.connectTaskWidgetSignals(tw)

    def connectTaskWidgetSignals(self, taskWidget):
        '''Connect task widgets' signals with their slots'''

        taskWidget.taskNameWidget.textChanged.connect(taskWidget.task.setName)
        taskWidget.taskNameWidget.editingFinished.connect(self.saveSettingsAndTasks)
        taskWidget.priorityWidget.valueChanged.connect(taskWidget.task.setPriority)
        taskWidget.priorityWidget.valueChanged.connect(self.saveSettingsAndTasks)
        taskWidget.priorityWidget.allowSorting.connect(self.applyFilterAndSorting)
        taskWidget.statusWidget.currentIndexChanged.connect(taskWidget.task.setStatus)
        taskWidget.statusWidget.currentIndexChanged.connect(self.applyFilterAndSorting)
        taskWidget.statusWidget.currentIndexChanged.connect(self.saveSettingsAndTasks)
        taskWidget.deleteWidget.clicked.connect(self.taskStore.deleteTask)
        taskWidget.deleteWidget.clicked.connect(self.update)
        taskWidget.deleteWidget.clicked.connect(self.deleteTask)
        taskWidget.deleteWidget.clicked.connect(self.saveSettingsAndTasks)
        taskWidget.newTaskSignal.connect(self.onAddTask)

    def resizeEvent(self, event):
        self.update()
        
    def showEvent(self, event):
        self.setEnabledState()
    def showEvent(self, event):
        '''Get rid of that unnecessary space around the widget when registering this widget as a nuke panel'''
        p = self
        while True:
            parentWidget = p.parentWidget()
            #print parentWidget
            #print parentWidget.layout()
            try:
                parentWidget.layout().setContentsMargins(0,0,0,0)
            except:
                break
            p = parentWidget
        super(MainWindow, self).showEvent(event)


    def setEnabledState(self):
        '''disable or enable the UI depending on whether settings file was found'''
        if self.inNuke or self.inHiero:
            # IF NO SETTINGS FILE HAS BEEN SET BY NOW, DISABLE ALL WIDGETS AND DISPLAY A MESSAGE IN THE PANEL
            if not self.settingsFile:
                self.disableWidget(True)
                if not self.warningText:
                    # this should only happen when the nuke script has not been saved yet
                    self.warningText = '<b>The project file has not been saved yet. Please save first before using this panel.</b>'
                else:
                    # this should only happen when a script is loaded with it's layout containing the widget,
                    # in which case self.setSettingsFile() will already have set the warning message.
                    # once that bug is fixed we should be able to get rid of this bit
                    pass
                self.msg.setText(self.warningText) 
                self.msg.setHidden(False)
            else:
                self.msg.setHidden(True)
                self.disableWidget(False)
        else:
            # STANDALONE FOR DEBUGGING- NOTHING WILL BE SAVED - FOR DEBUG ONLY
            pass

    def disableWidget(self, disable=True):
        '''
        If disable=True, disable all child widgets and display a message to ask user to save script/project.
        If disable=False, enable all child widgets and hide the warning message
        '''
        for w in self.children():
            try:
                if w is not self.msg:
                    w.setDisabled(disable)

            except AttributeError:
                # widget is layout and has no setDiabled method
                pass


    def update(self):
        '''Animate the view to match sorting and filtering requests'''
        logger.debug('updating view')

        self.deletedTaskWidgets = [tw for tw in self.taskWidgets if tw.task.index == -2]
        taskWidgetsHeight = len(self.taskWidgets) * (TaskWidget.TASKWIDGETHEIGHT * TaskWidget.TASKWIDGETSPACING)
        self.taskContainer.resize(self.scrollArea.width() - 20, max(taskWidgetsHeight, self.scrollArea.height()))

        self.animGroup = QtCore.QParallelAnimationGroup()
        animGroupForDeletedWidget = QtCore.QParallelAnimationGroup()
        animGroupForDeletedWidget.finished.connect(self.deleteTaskWidget)

        for taskWidget in self.taskWidgets:
            moveAnimation = QtCore.QPropertyAnimation(taskWidget, 'pos')
            moveAnimation.setDuration(1000)
            moveAnimation.setStartValue(taskWidget.pos())
            moveAnimation.setEndValue(taskWidget.getNewPosition())           

            if taskWidget.task.index == -2:
                # DELETED WIDGET
                moveAnimation.setEasingCurve(QtCore.QEasingCurve.InCubic)
                animGroupForDeletedWidget.addAnimation(moveAnimation)
            else:
                moveAnimation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
                self.animGroup.addAnimation(moveAnimation)
            taskWidget.update()
        # GO
        self.animGroup.start()
        
        # OVERLAP ANIMNATION FOR DELETED WIDGETS IN CASE OF RAPID TASK DELETION
        if animGroupForDeletedWidget.animationCount():
            self.animGroupsDeleted.append(animGroupForDeletedWidget)
            animGroupForDeletedWidget.start()


        logger.debug('finished updating view')

    def __helpText(self):
        return '''
        <b>Written by Frank Rueter|OHUfx</b>
        <p>
        This is a simple to-do list that saves itself with the Nuke script or Hiero project to help organise
        your own work as well as help others who might pick up a shot/project from you.
        </p>
        <p>
        Use LMB and RMB to change priorities to sort the list accordingly.
        You can also use MMB+drag or alt+LMB drag to change a task's priority.
        </p>
        Change the status and hide finished tasks to keep an overview over your work load.
        <p>
        The "Copy To Clipboard" button puts a neatly formatted version of the current tasks into the clipboard for use in email or other text documents.
        </p>
        <b>Click the help button to open the respective nukepedia page.</b>
        '''

    def _closeRunningInstances(self):
        '''Check if other instances are already runnign and close them before proceding.'''

        for widget in QtGui.QApplication.allWidgets():
            name = widget.objectName()
            if type(widget) == type(self):
                p = widget.parentWidget()
                while p:
                    if p.parent() and isinstance(p.parent(), QtGui.QStackedWidget):
                        p.parent().removeWidget(p) # THIS ASSUMES NUKE'S QSTACKEDWIDGET HOLDING THIS WIDGET
                        p = None
                    else:
                        p = p.parentWidget()


def launchWebsite():
    import webbrowser
    webbrowser.open('http://www.nukepedia.com/python/ui/todolist')

def settingsPathFromProject(projectFile):
    '''return the path for the settings file based on projectFile'''
    return os.path.splitext(projectFile)[0] + '_toDoSettings.xml'

def inNuke():
    '''Return True if this is run from inside of Nuke, else return False'''
    return 'nuke' in os.path.split(sys.executable)[0].lower()

def inHiero():
    '''Return True if this is run from inside of Hiero, else return False'''
    return 'Hiero' in QtGui.QApplication.applicationName()

def findAndReload():
    '''
    find MainWindow amongst all Nuke widgets and reload unless widget already has a settings file
    This is for nuke's onScriptSaveCallback for cases where the widget was first called in a deactivated state (from an unsaved nuke script)
    and is then saved while the widget is visible.
    This is also triggered via onScriptLoad to guarntee refresh when a script is loaded.
    '''
    for widget in QtGui.QApplication.allWidgets():
        if str(widget) == 'OHUfx ToDoList Widget':
            if not widget.settingsFile:
                widget.rebuildTaskWidgets()

def registerNukePanel():
    '''Register widget as a Nuke panel and add callback for saveing scripts'''
    import nuke
    import nukescripts
    nukescripts.registerWidgetAsPanel('ToDoList.MainWindow', 'To Do List', MainWindow.appName)
    nuke.addOnScriptSave(findAndReload)
    nuke.addOnScriptLoad(findAndReload)

def registerHieroPanel():
    '''Register widget as a Hiero panel'''
    import hiero
    toDoListWidget = MainWindow()
    wm = hiero.ui.windowManager()
    wm.addWindow(toDoListWidget)

def nukeSetup():
    '''
    Set up Nuke knobs to keep track of the settings file.
    Aborts and returns False if Nuke script hasn't been saved.
    '''
    import nuke
    try:
        root = nuke.root()
        rootKnobs = root.knobs()
        rootName = root.name()
    except ValueError as e:
        if str(e) == 'A PythonObject is not attached to a node':
            raise NukeError
        # we should never get this far so let's raise an error in case we do
        raise e

    if 'To Do List' not in rootKnobs:
        scriptPath = rootName
        if scriptPath == 'Root':
            return False
        logger.info('adding user knobs in script settings')
        tab = nuke.Tab_Knob('To Do List')
        settingsKnob = nuke.File_Knob('todoSettingsFile', 'Settings file')
        root.addKnob(tab)
        root.addKnob(settingsKnob)
        settingsKnob.setValue(settingsPathFromProject(scriptPath))
        return True
    else:
        return True

def hieroSetup():
    '''
    NOT YET SUPPORTED - NEED TO RE-IMLPEMENT AFTER RECTIFYING SOME CONFUSION/BUGS
    Set up Hiero tags in the current project to keep track of the settings file.
    Aborts and returns False if Hiero project hasn't been saved.
    '''
    raise NotImplementedError
    tagName = 'ohufx.ToDoList'
    import hiero

    def findSettingsTag(tagName):
        projectTags = hiero.core.findProjectTags()
        for tag in projectTags:
            if tag.name() == tagName:
                return tag
    
    activeProject = hiero.core.projects()[-1]
    projectPath = activeProject.path()

    if not findSettingsTag(tagName):
        print 'no tag found'
        if not projectPath:
            print "project hasn't been saved"
            # DO SOMETHING USEFUL WHEN SCRIPT HASN'T BEEN SAVED YET
            #msg = QtGui.QMessageBox()
            #msg.setText('Please save the Hiero project before using the To Do List\n(so the list\'s settings can be saved accordingly)')
            #msg.exec_()
            return False
        print 'adding tag to project'
        tagsBin = activeProject.tagsBin()
        toDoListSettingsTag = hiero.core.Tag(tagName)
        metaData = toDoListSettingsTag.metadata()
        metaData.setValue('tag.settingsFile', settingsPathFromProject(projectPath))
        tagsBin.addItem(toDoListSettingsTag)
        return True
    else:
        return True

###### RUN THIS UPON IMPORT ########################################################################
#if inNuke():
    #print 'Registering ToDoList for Nuke'
    #registerNukePanel()

#elif inHiero():
    #print 'Registering ToDoList for Hiero'
    #registerHieroPanel()


if __name__ == '__main__':
    #### STANDALONE FOR DEBUGGING
    import sys
    app = QtGui.QApplication([])
    p = MainWindow()
    p.show()
    sys.exit(app.exec_())
    


