#!/usr/bin/env python3
############################################################################################
#
# Repository:    GeniSysAI
# Project:       UP2 NCS1 Foscam Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)

# Title:         FoscamRead Class
# Description:   Reads frames from a Foscam IP camera and streams them to a socket stream.
# License:       MIT License
# Last Modified: 2020-08-20
#
############################################################################################

import base64
import cv2
import dlib
import geocoder
import json
import psutil
import os
import sys
import threading
import time

from datetime import datetime
from flask import Flask, request
from imutils import face_utils

from Classes.Helpers import Helpers
from Classes.iotJumpWay import Device as iot
from Classes.NCS1 import NCS1
from Classes.Sockets import Sockets

class FoscamRead():
	""" FoscamRead Class

	Reads frames from a Foscam IP camera and streams them
	to a socket stream.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("FoscamRead")

		self.identified = 0

		self.sockets()
		self.cv()
		self.iotJumpWay()
		self.foscam()
		self.ncs()
		self.threading()

		self.Helpers.logger.info("FoscamRead class initialized.")

	def cv(self):
		""" Configures OpenCV. """

		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.color = (255,255,255)
		self.fontScale  = 1
		self.lineType = 1

	def commands(self, topic, payload):
		"""
		iotJumpWay Commands Callback

		The callback function that is triggerend in the event of a
		command communication from the iotJumpWay.
		"""

		self.Helpers.logger.info("Recieved iotJumpWay Command Data : " + payload.decode())
		command = json.loads(payload.decode("utf-8"))

	def iotJumpWay(self):

		# Starts the iotJumpWay
		self.iot = iot()
		self.iot.connect()

		# Subscribes to the commands topic
		self.iot.channelSub("Commands")

		# Sets the commands callback function
		self.iot.commandsCallback = self.commands

	def foscam(self):
		""" Connects to the Foscam IP camera. """

		self.camera = cv2.VideoCapture("rtsp://"+self.Helpers.confs["Foscam"]["RTSPuser"] + ":" + self.Helpers.confs["Foscam"]["RTSPpass"] + "@" + self.Helpers.confs["Foscam"]["RTSPip"] + ":" + self.Helpers.confs["Foscam"]["RTSPport"] + "/" + self.Helpers.confs["Foscam"]["RTSPendpoint"])

		self.Helpers.logger.info("Connected To Camera")

	def life(self):
		""" Sends vital statistics to HIAS """

		# Gets vitals
		cpu = psutil.cpu_percent()
		mem = psutil.virtual_memory()[2]
		hdd = psutil.disk_usage('/').percent
		tmp = psutil.sensors_temperatures()['coretemp'][0].current
		g = geocoder.ip('me')

		self.Helpers.logger.info("GeniSysAI Foscam Life (TEMPERATURE): " + str(tmp) + "\u00b0")
		self.Helpers.logger.info("GeniSysAI Foscam Life (CPU): " + str(cpu) + "%")
		self.Helpers.logger.info("GeniSysAI Foscam Life (Memory): " + str(mem) + "%")
		self.Helpers.logger.info("GeniSysAI Foscam Life (HDD): " + str(hdd) + "%")
		self.Helpers.logger.info("GeniSysAI Foscam Life (LAT): " + str(g.latlng[0]))
		self.Helpers.logger.info("GeniSysAI Foscam Life (LNG): " + str(g.latlng[1]))

		# Send iotJumpWay notification
		self.iot.channelPub("Life", {
			"CPU": cpu,
			"Memory": mem,
			"Diskspace": hdd,
			"Temperature": tmp,
			"Latitude": g.latlng[0],
			"Longitude": g.latlng[1]
		})

		# Life thread
		threading.Timer(60.0, self.life).start()

	def ncs(self):
		""" Configures NCS1. """

		self.NCS1 = NCS1()

		self.known = self.Helpers.confs["Classifier"]["Known"]
		self.test = self.Helpers.confs["Classifier"]["Test"]

		self.detector = self.NCS1.Detector
		self.predictor = self.NCS1.Predictor

		self.Helpers.logger.info("NCS configured.")

	def sockets(self):
		""" Starts the socket stream. """

		self.Sockets = Sockets()
		self.Sockets.stream()

	def threading(self):
		""" Starts the GeniSysAI Foscam software threads. """

		# Life thread
		threading.Timer(60.0, self.life).start()

FoscamRead = FoscamRead()

fps = ""
framecount = 0
count = 0
time1 = 0
time2 = 0

while True:
	try:
		t1 = time.perf_counter()
		# Reads the current frame
		isOk, frame = FoscamRead.camera.read()

		if isOk:
			# Processes the frame
			raw, frame = FoscamRead.NCS1.prepareImg(frame)
			width = frame.shape[1]

			# Gets faces and coordinates
			faces, coords = FoscamRead.NCS1.faces(frame)

			# Writes header to frame
			cv2.putText(frame, "GeniSysAI", (10, 30), FoscamRead.font,
						0.7, FoscamRead.color, 2, cv2.LINE_AA)

			# Writes date to frame
			cv2.putText(frame, str(datetime.now()), (10, 50),
			FoscamRead.font, 0.5, FoscamRead.color, 2, cv2.LINE_AA)

			if len(coords):
				i = 0
				mesg = ""
				# Loops through coordinates
				for (i, face) in enumerate(coords):
					# Gets facial landmarks coordinates
					coordsi = face_utils.shape_to_np(face)
					# Looks for matches/intruders
					known, distance = FoscamRead.NCS1.match(raw, faces[i])

					if known:
						mesg = "GeniSysAI identified User #" + str(known)
					else:
						mesg = "GeniSysAI identified intruder"

					# Send iotJumpWay notification
					FoscamRead.iot.channelPub("Sensors", {
						"Type": "GeniSysAI",
						"Sensor": "Foscam Camera",
						"Value": known,
						"Message": mesg
					})

					# Draws facial landmarks
					for (x, y) in coordsi:
						cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
					# Adds user name to frame
					i += 1

			cv2.putText(frame, fps, (width-170, 30), cv2.FONT_HERSHEY_SIMPLEX,
								0.5, FoscamRead.color, 1, cv2.LINE_AA)

			# Streams the modified frame to the socket server
			encoded, buffer = cv2.imencode('.jpg', frame)
			FoscamRead.Sockets.sockStream.send(base64.b64encode(buffer))

			# FPS calculation
			framecount += 1
			if framecount >= 15:
				fps = "Stream: {:.1f} FPS".format(time1/15)
				framecount = 0
				time1 = 0
				time2 = 0
			t2 = time.perf_counter()
			elapsedTime = t2-t1
			time1 += 1/elapsedTime
			time2 += elapsedTime

	except KeyboardInterrupt:
		FoscamRead.camera.release()
		break

FoscamRead.camera.release()
