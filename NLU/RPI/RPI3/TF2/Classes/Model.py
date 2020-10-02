######################################################################################################
#
# Organization:  Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         Model Class
# Description:   Model helper functions.
# License:       MIT License
# Last Modified: 2020-10-01
#
######################################################################################################

import json
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf

from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from Classes.Helpers import Helpers
from Classes.Data import Data


class Model():
	""" Model Class

	Model helper functions.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("Model")
		self.Data = Data()

		self.Helpers.logger.info("Model class initialized.")

	def createDNN(self, x, y):
		""" Sets up the DNN layers """

		tf_model = tf.keras.models.Sequential([
                    tf.keras.layers.Dense(
                    	self.Helpers.confs["NLU"]['FcUnits'], activation='relu', input_shape=[len(x[0])]),
                    tf.keras.layers.Dense(
                    	self.Helpers.confs["NLU"]['FcUnits'], activation='relu'),
                    tf.keras.layers.Dense(
                    	self.Helpers.confs["NLU"]['FcUnits'], activation='relu'),
                    tf.keras.layers.Dense(
                    	self.Helpers.confs["NLU"]['FcUnits'], activation='relu'),
                    tf.keras.layers.Dense(
                    	len(y[0]), activation=self.Helpers.confs["NLU"]['Activation'])
                ],
			"GeniSysAI")
		tf_model.summary()
		self.Helpers.logger.info("Network initialization complete.")

		return tf_model

	def trainDNN(self, x, y, words, classes, intentMap):
		""" Trains the DNN """

		tf_model = self.createDNN(x, y)

		optimizer = tf.keras.optimizers.Adam(lr=self.Helpers.confs["NLU"]["LR"],
                                       decay=self.Helpers.confs["NLU"]["Decay"])

		tf_model.compile(optimizer=optimizer,
                   loss='binary_crossentropy',
                   metrics=[tf.keras.metrics.BinaryAccuracy(name='acc'),
                            tf.keras.metrics.Precision(name='precision'),
                            tf.keras.metrics.Recall(name='recall'),
                            tf.keras.metrics.AUC(name='auc')])

		tf_model.fit(x, y, epochs=self.Helpers.confs["NLU"]['Epochs'],
                    batch_size=self.Helpers.confs["NLU"]['BatchSize'])

		self.saveModelData(
			self.Helpers.confs["NLU"]['Model']['Data'],
			{
				'words': words,
				'classes': classes,
				'x': x,
				'y': y,
				'intentMap': [intentMap]
			},
			tf_model)

	def saveModelData(self, path, data, tmodel):
		""" Saves the model data """

		with open(self.Helpers.confs["NLU"]['Model']['Model'], "w") as file:
			file.write(tmodel.to_json())

		self.Helpers.logger.info(
			"Model JSON saved " + self.Helpers.confs["NLU"]['Model']['Model'])

		with open(self.Helpers.confs["NLU"]['Model']['Data'], "w") as outfile:
			json.dump(data, outfile)

		tmodel.save_weights(self.Helpers.confs["NLU"]['Model']['Weights'])
		self.Helpers.logger.info(
			"Weights saved " + self.Helpers.confs["NLU"]['Model']['Weights'])

	def buildDNN(self, x, y):
		""" Loads the DNN model """

		with open(self.Helpers.confs["NLU"]['Model']['Model']) as file:
			m_json = file.read()

		tmodel = tf.keras.models.model_from_json(m_json)
		tmodel.load_weights(self.Helpers.confs["NLU"]['Model']['Weights'])

		self.Helpers.logger.info("Model loaded ")
		return tmodel

	def predict(self, tmodel, parsedSentence, trainedWords, trainedClasses):
		""" Makes a prediction """

		predictions = [[index, confidence] for index, confidence in enumerate(
			tmodel.predict([[
				self.Data.makeBagOfWords(
					parsedSentence,
					trainedWords)]])[0])]
		predictions.sort(key=lambda x: x[1], reverse=True)

		classification = []
		for prediction in predictions:
			classification.append((trainedClasses[prediction[0]], prediction[1]))

		return classification
