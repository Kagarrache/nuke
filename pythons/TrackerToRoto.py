def TrackerToRoto() :
#CREATES NEW LAYER ON ROTO OR ROTOPAINT WITH TRACKING DATA
    import nuke.rotopaint as rp
    n = nuke.selectedNodes()

    try: 
        nuke.selectedNode()
    except:
        print nuke.message("Select a Tracker and a Roto or Rotopaint!")

    for nodes in n:
        if nodes.Class() != 'RotoPaint' and nodes.Class() != 'Roto' and nodes.Class() != 'Tracker4':
            nuke.message("Select a Tracker and a Roto or Rotopaint!")
            break
        elif len(n) == 1:
			if nodes.Class() == 'Tracker4' :
				p = nuke.createNode('Roto')
			else:
				nuke.message("Select a Tracker and a Roto or Rotopaint!")

    for nodes in n:
        if nodes.Class() == 'RotoPaint' or nodes.Class() == 'Roto':
            p = nodes
        elif nodes.Class() == 'Tracker4':
            track = nodes
            if track['label'].value() :
                tName = track['label'].value()
            else:
                tName = track['name'].value()
                
#CREATE NEW LAYER
    pCurves = p['curves']
    Layer = rp.Layer(pCurves)
    Layer.name = "%s_%s" %( tName, Layer.name)
    pLayer = pCurves.rootLayer.append(Layer)
    LayerName = Layer.name
    NewLayer = pCurves.toElement(LayerName)
    transform = NewLayer.getTransform()

    first = nuke.Root().knob('first_frame').getValue()
    first = int(first)
    last = nuke.Root().knob('last_frame').getValue()
    last = int(last)+1
    frame = first

#COPY TRACKER'S TRANSFORM TO NEW LAYER
    while frame<last:
        r = track['rotate'].getValueAt(frame,0)
        rr = transform.getRotationAnimCurve(2)
        rr.addKey(frame,r)
        tx = track['translate'].getValueAt(frame,0)
        translx = transform.getTranslationAnimCurve(0)
        translx.addKey(frame,tx)
        ty = track['translate'].getValueAt(frame,1)
        transly = transform.getTranslationAnimCurve(1)
        transly.addKey(frame,ty)
        sx = track['scale'].getValueAt(frame,0)
        ssx = transform.getScaleAnimCurve(0)
        ssx.addKey(frame,sx)
        sy = track['scale'].getValueAt(frame,1)
        ssy = transform.getScaleAnimCurve(1)
        ssy.addKey(frame,sy)
        cx = track['center'].getValueAt(frame,0)
        ccx = transform.getPivotPointAnimCurve(0)
        ccx.addKey(frame,cx)
        cy = track['center'].getValueAt(frame,1)
        ccy = transform.getPivotPointAnimCurve(1)
        ccy.addKey(frame,cy)
        frame = frame+1

TrackerToRoto()
