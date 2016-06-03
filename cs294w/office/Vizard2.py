import viz, vizact
import steamvr
import math
import vizmat
import json
from io import BytesIO
from contextlib import closing
import wave
import pyaudio
import sys
sys.path.append('houndipy')
from houndipy import Client
import thread

hmd=steamvr.HMD()
viz.link(hmd.getSensor(),viz.MainView)

viz.go()

viz.setOption('viz.model.apply_collada_scale',1)
#room = viz.add('conference_Room.dae')
room = viz.add('conference_room_1.dae');


elapsed_time = [0]


# Code imported for Houndify

class SendStream:

    def __init__(self, stream, rate, chunk_size, seconds):
        self.chunk_size = chunk_size
        self.seconds = seconds
        self.stream = stream
        self.rate = rate

    def __iter__(self):
        return iter(self.gen())

    def gen(self):
        print('starting')
        for i in range(0, int(self.rate / self.chunk_size * self.seconds)):
            yield self.stream.read(self.chunk_size)
        print('stopping')


def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD


def get_recording(seconds):
    CHUNK = 1024
    WIDTH = 2
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    FORMAT = p.get_format_from_width(WIDTH)

    with closing(p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)) as stream:

        print("* recording")

        frames = [
            stream.read(CHUNK)
            for _ in range(0, int(RATE / CHUNK * seconds))
        ]
        print("* done recording")

    p.terminate()

    file = BytesIO()
    wf = wave.open(file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

    return file.getvalue()


def save_hound():
    with open('auth.json') as fh:
        auth = json.load(fh)
    client = Client(
        auth['client_id'],
        auth['client_key']
    )

    #r = client.text('how old is chad reed')
    data = get_recording(seconds=10)
    print('sending')
    r = client.speech(data)
    print('sent')

    if not r.ok:
        print(r.text)

    r.raise_for_status()

    res = r.json()

    try:
        for sres in res['AllResults']:
            print(sres['NativeData']['LongResult'])
    except KeyError:
        with open('hound_data.txt', 'w') as outfile:
          json.dump(res, outfile)


# Fitbit API Code
import requests
import datetime
API_URL = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1sec/time/%s/%s.json"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTYxMzY0OTYsInNjb3BlcyI6InJ3ZWkgcnBybyByaHIgcmxvYyBybnV0IHJzbGUgcnNldCByYWN0IHJzb2MiLCJzdWIiOiIzUEZTNzciLCJhdWQiOiIyMjdNTVQiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJpYXQiOjE0NjQ2MDA0OTZ9.rOF5ve3FyOryrMhe_2ezfidLy7XM4ViwG3qGOIEXfdY"


def get_hour_min(time):
    tt = time.timetuple()
    hour = tt[3]
    min = tt[4]
    if hour < 10:
        hour = "0" + str(hour)
    else:
        hour = str(hour)
    if min < 10:
        min = "0" + str(min)
    else:
        min = str(min)
    return hour + ":" + min

def sendHeartRequest(start_time, end_time):
    start_time = get_hour_min(start_time)
    end_time = get_hour_min(end_time)
    headers = {"Authorization": "Bearer " + TOKEN}
    
    r = requests.get(API_URL %(start_time, end_time), headers=headers)
    with open('fitbit_data.txt', 'w') as outfile:
       json.dump(r.json(), outfile)

'''
text = viz.addText3D('', pos=[0, 1, 0])
#textScreen.message('Min')
def dostuff(text):
	sensor = hmd.getSensor()
	angle = sensor.getAxisAngle()[0]
	if angle > 0:
		print "looking down"
		#viz.addTexture('notepad.png')
		text = viz.addText3D('Spy', pos=[0, 1, 0])
		text.alignment(viz.ALIGN_CENTER_BOTTOM)
	else:
		print "removing"
		text.message("")
		print text.getMessage()
	
vizact.ontimer(0.5,dostuff, text)
'''
import vizinfo
info = vizinfo.InfoPanel('Hound and Fitbit') 
houndcheckbox = info.addLabelItem('Start Hound Recoding',viz.addCheckbox())
fitbitcheckbox = info.addLabelItem('Download Fitbit Data',viz.addCheckbox())
#Start time for fitbit tracking
start_time = datetime.datetime.now()

def onButton(obj,state): 
	if obj == houndcheckbox: 
		if state == viz.DOWN: 
			print "Saving Hound Data"
			thread.start_new_thread(save_hound, ())
	if obj == fitbitcheckbox: 
		if state == viz.DOWN: 
			print "Saving Fitbit Data"
			sendHeartRequest(start_time, datetime.datetime.now())
			sys.exit(0)
			

viz.callback(viz.BUTTON_EVENT,onButton) 

lines = list(open("dream.txt"))
text = lines[0].split(".")

prev = 0
prev_prev = 0
list = [prev, prev_prev]
index = [0]

power_point_prev = 0
power_point_prev_prev = 0
power_point_list = [power_point_prev, power_point_prev_prev]
power_point_index = [1]
power_point_changed = [False]

def counter(list, index, power_point_list, power_point_index, power_point_changed):
	curr = steamvr.getControllerList()[0].getTrigger()
	if list[0] == 0 and curr == 1 and list[1] == 0:
		index[0] = index[0] + 1
	list[1] = prev
	list[0] = curr
	
	curr = steamvr.getControllerList()[1].getTrigger()
	if power_point_list[0] == 0 and curr == 1 and power_point_list[1] == 0:
		power_point_index[0] = power_point_index[0] + 1
		power_point_changed[0] = True
	else: power_point_changed[0] = False
	power_point_list[1] = prev
	power_point_list[0] = curr
	
vizact.ontimer(0.1, counter, list, index, power_point_list, power_point_index, power_point_changed)
timerScreen = viz.addText3D('0', pos=[-3, 6, 3])
timerScreen.setEuler([180, 0, 0])
timerScreen.setPosition([5,3,-10])  #x,y,z  larger x, left / z<0 out towards the audience
timerScreen.fontSize(2)
timerScreen.setScale(1.0/8,1.0/5,1.0/5)
timerScreen.color(viz.RED)

def timer(elapsed_time):
	current_time = elapsed_time[0] + 1
	elapsed_time[0] = current_time
	timerScreen.message(str(current_time))

vizact.ontimer(1, timer, elapsed_time)

def processString(text):
	words = text.split(" ")
	len_text = len(words)
	new_text = ""
	cnt = 0
	for i in range(0, len_text):
		new_text += (words[i] + " ")
		if cnt == 8:
			new_text += "\n"
			cnt = 0
		cnt += 1
	return new_text


textScreen = viz.addText3D('', pos=[-3, 6, 3])
textScreen.setEuler([180, 0, 0])
textScreen.setPosition([5,2.5,-10])  #x,y,z  larger x, left / z<0 out towards the audience
textScreen.fontSize(2)
textScreen.setScale(1.0/8,1.0/5,1.0/5)

#textScreen.message('')
prevX = [None]


def updateScreenText(index, text, prevX):
	curr_text_index = index[0]
	if curr_text_index >= len(text): curr_text_index = len(text) - 1
	object = viz.MainWindow.pick(info=True)
	if object.valid:
		sensor = hmd.getSensor()
		positions = sensor.getPosition()
		#print positions
		if prevX[0] is None:
			prevX[0] = positions[0]
		else:
			if math.fabs(prevX[0] - positions[0]) > 0.3:
				#textScreen.setPosition(positions[0] + 0.3, 1.3, 0)
				prevX[0] = positions[0]
		angle = sensor.getAxisAngle()[0]
		textScreen.message(processString(text[curr_text_index].strip()))
		
		'''
		if angle > 0:
			print "Loooking down"
			sizet = len(text[curr_text_index].strip())
			#textScreen.setScale(1.0/10,1.0/10,1.0/10)
			#textScreen.message(text[curr_text_index].strip())
			#textScreen.setPosition(positions[0], positions[1], positions[2])
			textScreen.message(processString(text[curr_text_index].strip()))
		else:
			print "Looking up"
			#textScreen.message('')
		'''


# PPT overlay 
def updatePowerpoint(index, prev_quad, changed):
	if changed[0] == True:
		#print "changing"
		file_name = 'test_folder/Slide' 
		if index[0] <= 9:
			file_name += ("0" + str(index[0]))
		else:
			file_name += str(index[0])
		file_name += ".png"
		print file_name
		pic = viz.addTexture(file_name) 
		prev_quad[0].texture(pic)

quad = viz.addTexQuad() 


quad.setPosition([2, 2, 0.7]) #put quad in view 
quad.setEuler( [ 0, 0, 0 ] ) # set
quad.setScale(3,2,2)
prev_quad = [quad]

vizact.ontimer(0.1,updateScreenText, index, text, prevX)
vizact.ontimer(0.1, updatePowerpoint, power_point_index, prev_quad, power_point_changed)



# Create surface to wrap the texture on 
#quad = viz.addTexQuad()
#matrix = vizmat.Transform() 
# Scale down texture by scaling up the texquad's texture coordinates 
#matrix.setScale([1.5,1.5,1]) 
# Move the (0,0) texture coordinate up and to the right by subtracting 
#matrix.setTrans([-1.25,-0.25,1]) 
#quad.texmat(matrix) 
#quad.setPosition([-3,1.3, 0]) #put quad in view 

# Wrap texture on quad 
#quad.texture(pic)

