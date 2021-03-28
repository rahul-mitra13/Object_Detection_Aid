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

# Open display to show results  
display = jetson.utils.videoOutput("display://0")

# Returns a list of the ClassIDs of the identified objects (0 - 90)
def detected_ids(detections):
	ids = []
	for i in range(len(detections)):
		ids.append(detections[i].ClassID)
	return ids
	
ids = []

results = []

def get_ids():
	return ids

# Returns true if display window is still open
while display.IsStreaming():
 	print("wrong file")
	ids = []
	results = []
	
	#return img - blocks until next frame is available
	#converts raw format of the camera to floating point RGBA on the GPU
	img = camera.Capture()
	
	#detectNet object to identify objects
	detections = net.Detect(img)
	
	ids = detected_ids(detections)

	#render overlayed img to the OpenGL window
	display.Render(img)
	
	#update title of window to reflect current performance - uses internal profiling mechanism
	display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	
if '_name_' == '_main_':
	print("IDs = ", get_ids())


"""
	#gets the associated class label for each ClassID. Also, adding some test code here
	for id in ids:
		print(net.GetClassDesc(id))
		results.append(net.GetClassDesc(id))
	print(results)
"""

