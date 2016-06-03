import viz
import vizshape
import steamvr

hmd=steamvr.HMD()
viz.link(hmd.getSensor(),viz.MainView)

viz.go()

video = viz.addVideo('cs161.mp4')
#video = viz.addVideo('videoplayback.mp4')
sphere = vizshape.addSphere(flipFaces=True)
sphere.texture(video)

#Play and loop the video
video.play() 
video.loop() 

#Make sure sphere appears at infinite distance
#This allows other objects to be rendered in front
sphere.disable(viz.DEPTH_TEST)
sphere.drawOrder(-100)

#Keep sphere centered around main view
viz.link(viz.MainView,sphere,mask=viz.LINK_POS)

#Setup a panorama camera navigation
import vizcam
vizcam.PanoramaNavigate()