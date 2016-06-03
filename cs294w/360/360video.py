import viz
import steamvr

hmd=steamvr.HMD()
viz.link(hmd.getSensor(),viz.MainView)

viz.go()
'''
#Add models to scene
platform = viz.add('platform.osg')
viz.add('mini.osgx',parent=platform)

#Spin platform
platform.addAction(vizact.spin(0,1,0,10,viz.FOREVER))

#Add pivot camera
import vizcam
cam = vizcam.PivotNavigate(distance=20)
cam.rotateUp(15)
'''
def addBackgroundQuad(scene=viz.MainScene):
    """Returns a quad that will display in the background of the scene"""

    #Create group node containing render nodes for left/right eye quads
    group = viz.addGroup(scene=scene)
    group.leftQuad = viz.addRenderNode()
    group.leftQuad.disable(viz.RENDER_RIGHT)
    group.rightQuad = viz.addRenderNode()
    group.rightQuad.disable(viz.RENDER_LEFT)
    
    #Setup render nodes to display behind scene
    nodes = viz.ObjectGroup([group.leftQuad,group.rightQuad])
    nodes.setHUD(-1,1,-1,1,True)
    nodes.setOrder(viz.MAIN_RENDER)
    nodes.parent(group)
    group.drawOrder(-10000)
    group.polyMode(viz.POLY_FILL)
    
    return group

#Create background quad and apply a texture
background = addBackgroundQuad()
texture = viz.addVideo('cs161.mp4')
texture.setRate(1)
background.texture(texture)
texture.play()