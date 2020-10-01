############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         Engine Class
# Description:   Core functions for the NLU Engine.
# License:       MIT License
# Last Modified: 2020-08-20
#
############################################################################################

import sys
import os
import random
import json

from Classes.Helpers import Helpers
from Classes.Bluetooth import BluetoothConnect
from Classes.Context import Context
from Classes.Data import Data
from Classes.Mitie import Entities
from Classes.Extensions import Extensions
from Classes.Mitie import Entities
from Classes.Model import Model
from Classes.TTS import TTS


class Engine():
	""" Engine Class

	Core functions for the NLU Engine.
	"""

	def __init__(self, isAudio):
		""" Initializes the class. """

		self.Helpers = Helpers("Engine")

		self.ner = None
		self.user = {}

		#self.bluetoothCon()
		self.data()
		self.entities()
		#self.iotJumpWayCon()
		self.model()
		self.session()
		self.thresholds()

		if isAudio:
			self.speech()

		self.Helpers.logger.info("Engine class initialized.")

	def bluetoothCon(self):
		""" Initializes the Bluetooth connection. """

		self.Bluetooth = BluetoothConnect()
		self.Bluetooth.connect()

	def data(self):
		""" Initializes the data. """

		self.Data = Data()
		self.trainingData = self.Data.loadTrainingData()
		self.trainedData = self.Data.loadTrainedData()

		self.trainedWords = self.trainedData["words"]
		self.trainedClasses = self.trainedData["classes"]
		self.x = self.trainedData["x"]
		self.y = self.trainedData["y"]
		self.intentMap = self.trainedData["intentMap"][0]

	def doExtension(self, extension, entities, exEntities, extensionResponses):
		""" Executes an extension. """

		classParts = extension.split(".")
		classFolder = classParts[0]
		className = classParts[1]
		theEntities = None

		if exEntities != False:
			theEntities = entities

		module = __import__(
			classParts[0]+"."+classParts[1], globals(), locals(), [className])
		extensionClass = getattr(module, className)()
		response = getattr(extensionClass, classParts[2])(
			extensionResponses, theEntities)

		return response

	def entities(self):
		""" Initializes the entities. """

		self.entityController = Entities()
		self.ner = self.entityController.restoreNER()

	def entitiesCheck(self, entityHolder, theIntent, clearEntities):
		""" Checks entities. """

		if not len(entityHolder) and len(theIntent["entities"]):
			response, entities = self.entityController.replaceResponseEntities(
				random.choice(theIntent["fallbacks"]), entityHolder)
			extension, extensionResponses, exEntities = self.Extensions.setExtension(
				theIntent)
		elif clearEntities:
			entities = []
			response = random.choice(theIntent["responses"])
			extension, extensionResponses, exEntities = self.Extensions.setExtension(
				theIntent)
		else:
			response, entities = self.entityController.replaceResponseEntities(
				random.choice(theIntent["responses"]), entityHolder)
			extension, extensionResponses, exEntities = self.Extensions.setExtension(
				theIntent)

		return response, entities, extension, extensionResponses, exEntities

	def fallbackCheck(self, fallback, theIntent, entityHolder):
		""" Checks if fallback. """

		if fallback and fallback in theIntent and len(theIntent["fallbacks"]):
			response, entities = self.entityController.replaceResponseEntities(
				random.choice(theIntent["fallbacks"]), entityHolder)
			extension, extensionResponses, exEntities = None, [], None
		else:
			response, entities = self.entityController.replaceResponseEntities(
				random.choice(theIntent["responses"]), entityHolder)
			extension, extensionResponses, exEntities = self.Extensions.setExtension(
				theIntent)

		return response, entities, extension, extensionResponses, exEntities

	def model(self):
		""" Initializes the model. """

		self.Model = Model()
		self.Context = Context()
		self.Extensions = Extensions()

		self.tmodel = self.Model.buildDNN(self.x, self.y)

	def session(self):
		""" Initializes a NLU sesiion.

		Initiates empty guest user session, GeniSys will ask the user
		verify their GeniSys user by speaking or typing if it does
		not know who it is speaking to.
		"""

		self.userID = 0
		if not self.userID in self.user:
			self.user[self.userID] = {}
			self.user[self.userID]["history"] = {}

	def respond(self, status, sentence, intent, confidence,
			 response, cIn, cOut, cCurrent, extension, entities):
		""" Forms the response. """

		return {
			"Response": status,
			"ResponseData": [{
				"Received": sentence,
				"Intent": intent,
				"Confidence": confidence,
				"Response": response,
				"Context":  [{
					"In": cIn,
					"Out": cOut,
					"Current": cCurrent
				}],
				"Extension": extension,
				"Entities": entities
			}]
		}

	def speech(self):
		""" Initializes the TTS feature. """

		self.TTS = TTS()

	def thresholds(self):
		""" Sets thresholds

		Sets the threshold for the NLU engine, this can be changed
		using arguments to commandline programs or paramters for
		API calls.
		"""

		self.threshold = self.Helpers.confs["NLU"]["Threshold"]
		self.entityThrshld = self.Helpers.confs["NLU"]["Mitie"]["Threshold"]
