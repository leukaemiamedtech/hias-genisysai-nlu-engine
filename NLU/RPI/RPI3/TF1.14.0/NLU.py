######################################################################################################
#
# Organization:  Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         NLU Class
# Description:   The core Natural Language Understanding Engine.
# License:       MIT License
# Last Modified: 2020-10-01
#
######################################################################################################

import os
import json
import psutil
import random
import requests
import signal
import sys
import threading
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, Response, request
from threading import Thread

from Classes.Engine import Engine
from Classes.Helpers import Helpers
from Classes.iotJumpWay import Device as iot

from Train import Trainer

app = Flask(__name__)

class NLU():
	""" NLU Class

	The core Natural Language Understanding Engine class.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.isTraining  = False

		self.Helpers = Helpers("NLU")

		# Initiates the iotJumpWay connection class
		self.iot = iot()
		self.iot.connect()
		# Sets the commands callback function
		self.iot.commandsCallback = self.commands
		self.iot.channelSub("Commands")

		self.Helpers.logger.info("NLU class initialized.")

	def commands(self, topic, payload):
		""" iotJumpWay callback function.

		The callback function that is triggerend in the event of a
		command communication from the iotJumpWay.
		"""

		self.Helpers.logger.info("Recieved iotJumpWay Command Data : " + str(payload))
		commandData = json.loads(payload.decode("utf-8"))

		if commandData["Command"] == "Welcome":
			speak = "Hi " + commandData["Value"] + ", how are you?"
			self.Helpers.logger.info(speak)
			self.Engine.TTS.speak(speak)

	def life(self):
		""" Sends vital statistics to HIAS """

		cpu = psutil.cpu_percent()
		mem = psutil.virtual_memory()[2]
		hdd = psutil.disk_usage('/').percent
		tmp = psutil.sensors_temperatures()['cpu_thermal'][0].current
		r = requests.get('http://ipinfo.io/json?token=' + self.Helpers.confs["System"]["IPInfo"])
		data = r.json()
		location = data["loc"].split(',')

		self.Helpers.logger.info(
			"GeniSysAI Life (TEMPERATURE): " + str(tmp) + "\u00b0")
		self.Helpers.logger.info("GeniSysAI Life (CPU): " + str(cpu) + "%")
		self.Helpers.logger.info("GeniSysAI Life (Memory): " + str(mem) + "%")
		self.Helpers.logger.info("GeniSysAI Life (HDD): " + str(hdd) + "%")
		self.Helpers.logger.info("GeniSysAI Life (LAT): " + str(location[0]))
		self.Helpers.logger.info("GeniSysAI Life (LNG): " + str(location[1]))

		# Send iotJumpWay notification
		self.iot.channelPub("Life", {
			"CPU": cpu,
			"Memory": mem,
			"Diskspace": hdd,
			"Temperature": tmp,
			"Latitude": location[0],
			"Longitude": location[1]
		})

		threading.Timer(60.0, self.life).start()

	def engine(self, audio):
		""" Loads the NLU Engine. """

		self.Engine = Engine(audio)

	def communicate(self, sentence):
		""" Responds to the user

		First checks to ensure that the program is not training,
		then parses any entities that may be in the intent, then
		checks context and extensions before providing a response.
		"""

		if self.isTraining == False:

			parsed, fallback, entityHolder, parsedSentence = self.Engine.entityController.parseEntities(
				sentence,
				self.Engine.ner,
				self.Engine.trainingData
			)

			classification = self.Engine.Model.predict(self.Engine.tmodel, parsedSentence,
											 			self.Engine.trainedWords, self.Engine.trainedClasses)

			if len(classification) > 0:

				clearEntities = False
				theIntent = self.Engine.trainingData["intents"][self.Engine.intentMap[classification[0][0]]]

				if len(entityHolder) and not len(theIntent["entities"]):
					clearEntities = True

				if(self.Engine.Context.checkSessionContext(self.Engine.user[self.Engine.userID], theIntent)):

					if self.Engine.Context.checkClearContext(theIntent, 0):
						self.Engine.user[self.Engine.userID]["context"] = ""

					contextIn, contextOut, contextCurrent = self.Engine.Context.setContexts(
						theIntent, self.Engine.user[self.Engine.userID])

					response, entities, extension, extensionResponses, exEntities = self.Engine.entitiesCheck(
						entityHolder, theIntent, clearEntities)

					if extension != None:
						response = self.Engine.doExtension(
							extension, entities, exEntities, extensionResponses)

					return self.Engine.respond("OK", sentence, classification[0][0], str(classification[0][1]),
						response, contextIn, contextOut, contextCurrent, extension, entityHolder)

				else:

					self.Engine.user[self.Engine.userID]["context"] = ""
					contextIn, contextOut, contextCurrent = self.Engine.Context.setContexts(
						theIntent, self.Engine.user[self.Engine.userID])

					response, entities, extension, extensionResponses, exEntities = self.Engine.fallbackCheck(
						fallback, theIntent, entityHolder)

					if extension != None:
						response = self.Engine.doExtension(
							extension, entities, exEntities, extensionResponses)
					else:
						response = self.Engine.entityController.replaceResponseEntities(
							random.choice(theIntent["responses"]), entityHolder)
						if(type(response)==tuple):
							response = response[0]

					return self.Engine.respond("OK", sentence, classification[0][0], str(classification[0][1]),
						response, contextIn, contextOut, contextCurrent, extension, entityHolder)

			else:

				contextCurrent = self.Engine.Context.getCurrentContext(
					self.Engine.user[self.Engine.userID])
				response = random.choice(self.Helpers.confs["NLU"]["defaultResponses"])

				return self.Engine.respond("FAILED", sentence, "UNKNOWN", "NA", response,
									"NA", "NA", contextCurrent, "NA", entityHolder)
		else:

			return {
				"Response": "FAILED",
				"ResponseData": [{
					"Status": "Training",
					"Message": "NLU Engine is currently training"
				}]
			}

	def threading(self):
		""" Creates required module threads. """

		# Life thread
		Thread(target=self.life, args=(), daemon=True).start()
		threading.Timer(60.0, self.life).start()

	def signal_handler(self, signal, frame):
		self.Helpers.logger.info("Disconnecting")
		self.iot.disconnect()
		sys.exit(1)

NLU = NLU()

@app.route("/Api", methods = ["POST"])
def Api():
	""" API Inference endpoint

	Is triggered when an authorized request is made to the Api
	endpoint.
	"""

	NLU.Engine.session()

	if request.headers["Content-Type"] == "application/json":
		query = request.json
		response = NLU.communicate(query["query"])

		return Response(response=json.dumps(response, indent=4, sort_keys=True),
						status=200, mimetype="application/json")

@app.route("/Audio", methods = ["POST"])
def Audio():
	""" Inference endpoint

	Is triggered when an authorized request is made to the Audio
	endpoint.
	"""

	if request.headers["Content-Type"] == "application/json":
		query = request.json
		NLU.Engine.session()
		response = NLU.communicate(query["query"])
		NLU.Helpers.logger.info("Received: " + query["query"])
		speak = str(response["ResponseData"][0]["Response"])

		NLU.Helpers.logger.info("Response: " + speak)

		Thread(target=NLU.Engine.TTS.speak, args=(speak,), daemon=True).start()

		return Response(response=json.dumps(response, indent=4, sort_keys=True),
						status=200, mimetype="application/json")

if __name__ == "__main__":

	signal.signal(signal.SIGINT, NLU.signal_handler)
	signal.signal(signal.SIGTERM, NLU.signal_handler)
	NLU.threading()

	isAudio = False

	if(len(sys.argv) == 3):
		isAudio = True
		NLU.Helpers.logger.info("Audio mode")

	if sys.argv[1] == "Train":
		""" Training mode

		Trains GeniSys.
		"""

		NLU.Helpers.logger.info("Training mode")

		Train = Trainer()
		Train.trainModel()

	elif sys.argv[1] == "Server":
		""" Server mode

		Allows communication with GeniSys via HTTP requests.
		"""

		NLU.Helpers.logger.info("Server mode")

		NLU.engine(isAudio)

		NLU.Helpers.logger.info("Inference Started In SERVER Mode")

		app.run(host=NLU.Helpers.confs["System"]["IP"], port=NLU.Helpers.confs["System"]["Port"])

	elif sys.argv[1] == "Input":
		""" Input mode

		Allows communication with GeniSys through commandline.
		"""

		NLU.Helpers.logger.info("Input mode")

		NLU.engine(isAudio)

		while True:

			intent = input(">")

			NLU.Helpers.logger.info(intent)

			response = NLU.communicate(intent)
			response = str(response["ResponseData"][0]["Response"])

			NLU.Helpers.logger.info(response)

			if isAudio:
				NLU.Engine.TTS.speak(response)

