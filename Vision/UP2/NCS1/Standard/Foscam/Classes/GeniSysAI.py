############################################################################################
#
# Repository:    HIAS GeniSysAI
# Project:       HIAS NCS1 Foscam Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)

# Title:         GeniSysAI Class
# Description:   GeniSysAI HIAS NCS1 Foscam Security System class.
# License:       MIT License
# Last Modified: 2020-08-27
#
############################################################################################

import cv2

from Classes.Helpers import Helpers
from Classes.OpenCV import OpenCV
from Classes.NCS1 import NCS1

class GeniSysAI():
	""" GeniSysAI Class

	GeniSysAI HIAS NCS1 Foscam Security System class.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("GeniSysAI")

		self.Helpers.logger.info("GeniSysAI class initialized.")

	def cv(self):
		""" Configures OpenCV. """

		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.color = (255,255,255)
		self.fontScale  = 1
		self.lineType = 1

	def connect(self):
		""" Connects to the Foscam IP camera. """

		self.camera = OpenCV("rtsp://"+self.Helpers.confs["Foscam"]["RTSPuser"] + ":" + self.Helpers.confs["Foscam"]["RTSPpass"] + "@" + self.Helpers.confs["Foscam"]["RTSPip"] + ":" + self.Helpers.confs["Foscam"]["RTSPport"] + "/" + self.Helpers.confs["Foscam"]["RTSPendpoint"])

		self.Helpers.logger.info("Connected To Camera")

	def ncs(self):
		""" Configures NCS1. """

		self.NCS1 = NCS1()

		self.known = self.Helpers.confs["Classifier"]["Known"]
		self.test = self.Helpers.confs["Classifier"]["Test"]

		self.detector = self.NCS1.Detector
		self.predictor = self.NCS1.Predictor

		self.Helpers.logger.info("NCS1 configured.")