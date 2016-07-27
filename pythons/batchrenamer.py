"""
batchrenamer.py

Created by Tyler Lockard [lockardvfx@gmail.com] 11/7/14.

Works as-is. I can't be held responsible if this renamer chews up all your file
names. Be careful with it.

"Batch Renamer" removes all the hassle from jumping out of nuke, launching a
batch rename program, probably messing up a few times, jumping back into Nuke
and updating your read node... That takes like, a whole minute. That's just too
long. With a simple UI, we can do all that in Nuke.

# To install, move this to your .nuke folder and
# add these lines in your menu.py:

menubar = nuke.menu("Nodes")
m = menubar.addMenu("Tyler Lockard")
m.addCommand('Batch Rename', 'import batchrenamer; batchrenamer.main()')
"""


import os
from glob import glob
import nuke
import nukescripts



class BatchRenamePanel(nukescripts.PythonPanel):
    '''
    The dialog panel where we're going to grab all of our information.
    Automatically tries to scale itself based on the contents provided. Some
    panel knobs are  dynamically created based on your selected nodes if they
    contain a "file" knob. These include the text find and replace previews as
    well as the list of source filepaths at the top.
    '''
    def __init__(self, sequences):
        nukescripts.PythonPanel.__init__(self, 'Batch Renamer')

        self.seqs = sequences.values()

        # Try to set our window size based on our contents
        self.height = 270 + (len(self.seqs) * 40)
        self.length = 400
        for s in self.seqs:
            if 130 + len(s) * 7 > self.length:
                self.length = 130 + len(s) * 7
        self.setMinimumSize(self.length, self.height)

        # Create our header
        self.addKnob(nuke.Text_Knob('break', ''))
        self.addKnob(nuke.Text_Knob('header', 'Files to be modified:', ' '))

        # Dynamically add our source filepath text
        c = 1
        for s in self.seqs:
            self.addKnob(nuke.Text_Knob(str(c), '', s))
            c += 1

        # Create a string knob for our "Find" field
        self.addKnob(nuke.Text_Knob('break', ''))
        self.addKnob(nuke.String_Knob('find', 'Find this:', ''))

        # Dynamically add our preview "Find" text
        c = 1
        self.original_finds = {}
        for s in self.seqs:
            self.addKnob(nuke.Text_Knob('previewFind%s' % c, '', os.path.basename(s)))
            self.original_finds['previewFind%s' % c] = os.path.basename(s)
            c += 1

        # Create a string knob for our "Replace" field
        self.addKnob(nuke.Text_Knob('break', '', ' '))
        self.addKnob(nuke.String_Knob('replace', 'Replace with:', ''))

        # Dynamically add our preview "Replace" text
        c = 1
        self.original_replaces = {}
        for s in self.seqs:
            self.addKnob(nuke.Text_Knob('previewReplace%s' % c, '', os.path.basename(s)))
            self.original_replaces['previewReplace%s' % c] = os.path.basename(s)
            c += 1

        # Finally, create some dividers for the footer
        self.addKnob(nuke.Text_Knob('break', ''))
        self.addKnob(nuke.Text_Knob('break', '', ' '))


    def knobChanged(self, knob):
        '''
        Refreshes the preview text whenever the find and replace fields are
        changed.
        '''
        try:  # "Try" because it may error out if nothing's provided yet
            color_start = '<span style="color:orange">'
            color_end = '</span>'
            find = self.knobs()['find'].value()
            rep = self.knobs()['replace'].value()

            for i in self.knobs():
                # Update the find preview text
                if "previewFind" in i:
                    # Set it back to the default value first
                    self.knobs()[i].setValue(self.original_finds[i])

                    # Build our new text
                    update = self.knobs()[i].value().replace(color_start, '')
                    update = update.replace(color_end, '')
                    update = update.split(find)
                    highlight = color_start + find + color_end
                    update = highlight.join(update)

                    # Apply the new text
                    self.knobs()[i].setValue(update)

                # Update the replace preview text
                elif "previewReplace" in i:
                    # Set it back to the default value first
                    self.knobs()[i].setValue(self.original_replaces[i])

                    # Build our new text
                    update = self.knobs()[i].value().replace(color_start, '')
                    update = update.replace(color_end, '')
                    update = update.split(find)
                    highlight = color_start + rep + color_end
                    update = highlight.join(update)

                    # Apply the new text
                    self.knobs()[i].setValue(update)
        except:
            pass


def batchRename(sequences, find, replace):
    '''
    Takes a node and image sequence dictionary and runs a mass-rename based on
    the feedback from the dialog panel.
    '''
    for node in sequences:
        filepath = os.path.realpath(sequences[node])

        # Extract both our filename and directory path
        dir = os.path.dirname(filepath)
        basename = os.path.basename(filepath).split('.')

        # Split our file name into relevant bits
        filename = basename[0]
        if "#" in filename:
            filename = filename.split('#')[0]
        if "%0" in filename:
            filename = filename.split('%0')[0]
        ext = "." + basename[-1]

        # Find all matching frames based on this criteria
        frames = glob(dir + "/" + filename + "*" + ext)
        for f in frames:
            r = dir + '/' + os.path.basename(f).replace(find, replace)
            os.rename(f, r)

        # We're done! Now let's punch in the new value on the respective node
        updated_path = dir + '/'
        updated_path += os.path.basename(filepath).replace(find, replace)
        nuke.toNode(node)['file'].setValue(updated_path)

    # Feedback!
    nuke.message("Batch rename finished! \n\nI updated the for you.")


def main():
    '''
    This is the main bit
    '''
    # Make a list of files from our selection
    sequences = {}
    for i in nuke.selectedNodes():
        try:
            sequences[i.name()] = i['file'].value()
        except:
            nuke.message("I can't seem to add \"%s\" to our list of files. \
                         \nThis'll only work on nodes with a \"file\" knob.\
                         \n\nSkipping..." % i.name())

    # Make sure we have something selected
    if len(sequences) == 0:
        nuke.message("Select a read node first!")
        return

    # Good to go, display our dialog
    p = BatchRenamePanel(sequences)
    result = p.showModalDialog()

    # Run the batch rename with what we've collected
    if result == True:
        find = p.knobs()['find'].value()
        replace = p.knobs()['replace'].value()
        batchRename(sequences, find, replace)
