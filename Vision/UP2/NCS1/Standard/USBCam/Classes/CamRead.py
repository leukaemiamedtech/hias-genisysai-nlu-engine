############################################################################################
#
# Repository:    GeniSysAI
# Project:       NCS1 USB Camera Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         CamRead Class
# Description:   Reads frames from a USB camera and streams them to a socket stream.
# License:       MIT License
# Last Modified: 2020-08-27
#
############################################################################################

import base64
import cv2
import dlib
import os
import sys
import time

from datetime import datetime
from imutils import face_utils
from threading import Thread

from Classes.Helpers import Helpers
from Classes.iotJumpWay import Device as iot
from Classes.GeniSysAI import GeniSysAI

class CamRead(Thread):
	""" CamRead Class

	Reads frames from a USB camera and streams them
	to a socket stream.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("CamRead")
		super(CamRead, self).__init__()

		self.Helpers.logger.info("CamRead class initialized.")

	def run(self):
		""" Runs the module. """

		self.identified = 0

		# Starts the GeniSysAI module
		self.GeniSysAI = GeniSysAI()
		self.GeniSysAI.cv()
		self.GeniSysAI.connect()
		self.GeniSysAI.ncs()

		# Starts the socket server
		soc = self.Sockets.connect(self.Helpers.confs["Socket"]["host"], self.Helpers.confs["Socket"]["port"])

		fps = ""
		framecount = 0
		count = 0
		time1 = 0
		time2 = 0

		while True:
			try:
				t1 = time.perf_counter()
				# Reads the current frame

				frame = self.GeniSysAI.camera.get(0.65)

				# Processes the frame
				raw, frame = self.GeniSysAI.NCS1.prepareImg(frame)
				width = frame.shape[1]

				# Gets faces and coordinates
				faces, coords = self.GeniSysAI.NCS1.faces(frame)

				# Writes header to frame
				cv2.putText(frame, "GeniSysAI", (10, 30), self.GeniSysAI.font,
							0.7, self.GeniSysAI.color, 2, cv2.LINE_AA)

				# Writes date to frame
				cv2.putText(frame, str(datetime.now()), (10, 50),
					self.GeniSysAI.font, 0.5, self.GeniSysAI.color, 2, cv2.LINE_AA)

				if len(coords):
					i = 0
					mesg = ""
					# Loops through coordinates
					for (i, face) in enumerate(coords):
						# Gets facial landmarks coordinates
						coordsi = face_utils.shape_to_np(face)
						# Looks for matches/intruders
						known, distance = self.GeniSysAI.NCS1.match(raw, faces[i])

						if known:
							mesg = "GeniSysAI identified User #" + str(known)
						else:
							mesg = "GeniSysAI identified intruder"

						# Send iotJumpWay notification
						self.iot.channelPub("Sensors", {
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
									0.5, self.GeniSysAI.color, 1, cv2.LINE_AA)

				# Streams the modified frame to the socket server
				encoded, buffer = cv2.imencode('.jpg', frame)
				soc.send(base64.b64encode(buffer))

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
				self.GeniSysAI.camera.release()
				break