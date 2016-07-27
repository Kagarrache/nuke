def explore_path():
    mypath = nuke.selectedNode().knob("file").value()

    currentView = nuke.thisNode()

    if string.find(mypath, "%V") !=-1 and currentView=="left":
        searchStr="%V"
        replaceStr="left"
    elif string.find(mypath,"%V")!=-1 and currentView=="right":
        searchStr="%V"
        replaceStr="right"
    elif string.find(mypath, "%v")!=-1 and currentView=="left":
        searchStr="%v"
        replaceStr="l"
    elif string.find(mypath, "%v") !=-1 and currentView=="right":
        searchStr="%v"
        replaceStr="r"
    else:
        searchStr=""
        replaceStr=""
    newpath=string.replace(mypath, searchStr, replaceStr)
    (dirname, fileBaseName) = os.path.split(newpath)
    if string.find(newpath,"//")!=-1:
        newdirname = string.replace(newpath, "//", "\\\\")
        (dirnamess, fileBaseName) = os.path.split(newdirname)
        os.startfile(dirnamess)
    else:
        os.startfile(dirname)
    return

