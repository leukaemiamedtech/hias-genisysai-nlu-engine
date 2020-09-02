############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         Trainer Class
# Description:   Trains the Natural Language Understanding Engine.
# License:       MIT License
# Last Modified: 2020-08-19
#
############################################################################################

import sys
import os
import json
import re
import time
import warnings

from Classes.Helpers import Helpers
from Classes.Data import Data
from Classes.Model import Model
from Classes.Mitie import Entities

if not sys.warnoptions:
	warnings.simplefilter("ignore")

class Trainer():
	""" Trainer Class

	Trains the Natural Language Understanding Engine.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("Train")

		self.intentMap = {}
		self.words = []
		self.classes = []
		self.dataCorpus = []

		self.Model = Model()
		self.Data = Data()

		self.Helpers.logger.info("Trainer class initialized.")

	def setupData(self):
		""" Prepares the data. """

		self.trainingData = self.Data.loadTrainingData()

		self.words, self.classes, self.dataCorpus, self.intentMap = self.Data.prepareData(self.trainingData)
		self.x, self.y = self.Data.finaliseData(self.classes, self.dataCorpus, self.words)

		self.Helpers.logger.info("NLU Training Data Ready")

	def setupEntities(self):
		""" Prepares the entities. """

		if self.Helpers.confs["NLU"]["Entities"] == "Mitie":
			self.entityController = Entities()
			self.entityController.trainEntities(
				self.Helpers.confs["NLU"]["Mitie"]["ModelLocation"],
				self.trainingData)

			self.Helpers.logger.info("NLU Trainer Entities Ready")

	def trainModel(self):
		""" Trains the model. """

		while True:
			self.Helpers.logger.info("Ready To Begin Training ? (Yes/No)")
			userInput = input(">")

			if userInput == 'Yes': break
			if userInput == 'No':  exit()

		self.setupData()
		self.setupEntities()

		self.Model.trainDNN(self.x, self.y, self.words,
					  self.classes, self.intentMap)

		self.Helpers.logger.info("NLU Model Trained")
