############################################################################################
#
# Repository:    GeniSysAI
# Project:       UP2 NCS1 Foscam Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)

# Title:         FoscamStream Class
# Description:   Streams the processed frames to a local video server.
# License:       MIT License
# Last Modified: 2020-08-20
#
############################################################################################

import cv2
import base64
import time
import zmq
import errno

import numpy as np

from flask import Flask, request
from PIL import Image
from io import BytesIO

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread

from Classes.Helpers import Helpers
from Classes.Sockets import Sockets

app = Flask(__name__)

class FoscamStream():
	""" FoscamStream Class

	Streams the processed frames to a local video server.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("FoscamStream")

		self.Sockets = Sockets()
		self.Sockets.receive()

		self.Helpers.logger.info("FoscamStream class initialized.")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith('.mjpg'):
					self.send_response(200)
					self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
					self.end_headers()
					count = 0

					while True:
						frame = FoscamStream.Sockets.socReceiver.recv_string()
						frame = cv2.imdecode(np.fromstring(base64.b64decode(frame),
														dtype=np.uint8), 1)

						imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
						jpg = Image.fromarray(imgRGB)
						tmpFile = BytesIO()
						jpg.save(tmpFile,'JPEG')
						self.wfile.write("--jpgboundary".encode())
						self.send_header('Content-type','image/jpeg')
						self.send_header('Content-length',str(tmpFile.getbuffer().nbytes))
						self.end_headers()
						self.wfile.write(tmpFile.getvalue())
					return
		except IOError as e:
			print("Broken Pipe")

def main():

	global FoscamStream

	FoscamStream = FoscamStream()

	try:
		server = ThreadedHTTPServer(
			(FoscamStream.Helpers.confs["Foscam"]["IP"], FoscamStream.Helpers.confs["Foscam"]["Port"]), CamHandler)
		FoscamStream.Helpers.logger.info(
			"Foscam server started on " + FoscamStream.Helpers.confs["Foscam"]["IP"]+":"+str(FoscamStream.Helpers.confs["Foscam"]["Port"]))
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()
		FoscamStream.Sockets.socReceiver.close()

if __name__ == '__main__':
	main()
