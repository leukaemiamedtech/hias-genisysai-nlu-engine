############################################################################################
#
# Repository:    GeniSysAI
# Project:       UP2 NCS1 USB Camera Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
# Contributors:
# Title:         Sockets Class
# Description:   Sockets helper functions.
# License:       MIT License
# Last Modified: 2020-08-21
#
############################################################################################

import zmq

import numpy as np

from Classes.Helpers import Helpers

class Sockets():
	""" Sockets Class

	Sockets helper functions.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("Sockets")
		self.Helpers.logger.info("Sockets Class initialized.")

	def stream(self):
		""" Configures the socket we will stream the frames to. """

		self.sockStream = zmq.Context().socket(zmq.PUB)
		self.sockStream.connect(
			"tcp://"+self.Helpers.confs["Socket"]["host"] + ":" + str(self.Helpers.confs["Socket"]["port"]))

		self.Helpers.logger.info("Connected To Socket: tcp://" +
								 self.Helpers.confs["Socket"]["host"] + ":" + str(self.Helpers.confs["Socket"]["port"]))

	def receive(self):
		""" Configures the socket that will receive the frames. """

		context = zmq.Context()
		self.socReceiver = context.socket(zmq.SUB)
		self.socReceiver.setsockopt(zmq.CONFLATE, 1)
		self.socReceiver.bind(
			"tcp://*:"+str(self.Helpers.confs["Socket"]["port"]))
		self.socReceiver.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

		self.Helpers.logger.info("Connected To Socket: tcp://" +
								 self.Helpers.confs["Socket"]["host"] + ":" + str(self.Helpers.confs["Socket"]["port"]))
