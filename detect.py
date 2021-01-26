import jetson.inference
import jetson.utils
import sys

#this is the neural net
#0.5 baseline
net = jetson.inference.detectNet("ssd-inception-v2", threshold=0.5)#threshold influences number of objects detected

#this is the camera object
#parameters - width, height, device file
#a good resolution might be 1280*780
camera = jetson.utils.videoSource("csi://0")

#open display to show results  
display = jetson.utils.videoOutput("display://0")

ids = []
#returns true if display window is still open

results = []

while display.IsStreaming():
	
	#return img - blocks until next frame is available
	#converts raw format of the camera to floating point RGBA on the GPU
	img = camera.Capture()
	
	#detectNet object to identify objects
	detections = net.Detect(img)
	
	#gets the ClassID of the identified object (0 - 90)
	for i in range(len(detections)):
		ids.append(detections[i].ClassID)

	#gets the associated class label for each ClassID. Also, adding some test code here
	for id in ids:
		print(net.GetClassDesc(id))
		results.append(net.GetClassDesc(id))
	print(results)

	#render overlayed img to the OpenGL window
	display.Render(img)
	
	#update title of window to reflect current performance - uses internal profiling mechanism
	display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	


