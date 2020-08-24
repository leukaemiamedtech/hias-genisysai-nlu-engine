############################################################################################
#
# Repository:    GeniSysAI
# Project:       NCS1 USB Camera Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)

# Title:         CamStream Class
# Description:   Streams the processed frames to a local video server.
# License:       MIT License
# Last Modified: 2020-08-21
#
############################################################################################

import cv2
import base64
import time

import numpy as np

from PIL import Image
from io import BytesIO

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread

from Classes.Helpers import Helpers
from Classes.Sockets import Sockets

class CamStream():
	""" CamStream Class

	Streams the processed frames to a local video server.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("CamStream")

		self.Sockets = Sockets()
		self.Sockets.receive()

		self.Helpers.logger.info("CamStream class initialized.")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			count = 0

			while True:

				frame = CamStream.Sockets.socReceiver.recv_string()
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

		if self.path.endswith('.html'):
			src = '<img src="http://'+CamStream.Helpers.confs["Camera"]["IP"]+':'+str(CamStream.Helpers.confs["Camera"]["Port"])+'/cam.mjpg" />'
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>'.encode())
			self.wfile.write(src.encode())
			self.wfile.write('</body></html>'.encode())
			return

def main():

	global CamStream

	CamStream = CamStream()

	try:
		server = ThreadedHTTPServer(
			(CamStream.Helpers.confs["Camera"]["IP"], CamStream.Helpers.confs["Camera"]["Port"]), CamHandler)
		CamStream.Helpers.logger.info(
			"Camera server started on " + CamStream.Helpers.confs["Camera"]["IP"]+":"+str(CamStream.Helpers.confs["Camera"]["Port"]))
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()
		CamStream.Sockets.socReceiver.close()

if __name__ == '__main__':
	main()
