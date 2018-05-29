#!/usr/bin/env python
import rospy
import traceback
import socket
import json
import thread
from geometry_msgs.msg import Vector3

def splitpublish(json_raw):
	if len(json_raw) != 0:
		#Converting a JSON object into a Python dictionary
		decoded = json.loads(json_raw)
		print decoded
		
		#3-D vector that will temporarily contain all 3-D data
		#before it is published
		msg = Vector3()

		#Let's publish from all the desired sensors
		#the list comprehension allows us to sift through the JSON packet
		#and find the desired HyperIMU data
		#because we stored the data stream names in sensorPub in the main
		for sensor_topic in [key for key,val in sensorPub.items()]:
			if sensor_topic in decoded:
				msg.x = float(decoded[sensor_topic][0])
				msg.y = float(decoded[sensor_topic][1])
				msg.z = float(decoded[sensor_topic][2])
				sensorPub[sensor_topic].publish(msg)
				print(msg)

#This function is run on multiple threads. 
#t accepts HyperIMU information and calls splitpublish
def clientrun(clientsocket, address):
	while True:
		try:
			message = clientsocket.recv(8192)
			splitpublish(message)
		except Exception as e:
			traceback.print_exc()
			print e
	clientsocket.close()

def tcp_receive():
	host = ''
	port = 5555

	#TCP connection! HyperIMU can only send JSON over TCP, not UDP
	#put this block into a loop so that any disconnection will shut everything down
	#and then resume listening
	s = socket.socket()
	s.bind((host, port))
	print('Waiting for connection...')
	s.listen(1)

	while not rospy.is_shutdown():
		try:
			c, addr = s.accept()
			print("Connection received!")
			thread.start_new_thread(clientrun,(c,addr))
		except Exception as e:
			traceback.print_exc()
			print e
	print("Rospy is shut down.")

if __name__ == '__main__':
	rospy.init_node('phoneJSON', anonymous=True)
	#The keys in the sensorPub dictionary MUST by the names given to the data streams by HyperIMU.
	#This allows it to be navigated using the same keys as decoded, which is the dictionary obtained from the JSON packet by json.loads in splitpublish(json_raw).
	sensorPub = {}
	sensorPub["3-axis Accelerometer"] = rospy.Publisher("Sensor/Accelerometer", Vector3, queue_size = 1)
	sensorPub["GPS"] = rospy.Publisher("Sensor/GPS", Vector3, queue_size = 1)

	tcp_receive()
