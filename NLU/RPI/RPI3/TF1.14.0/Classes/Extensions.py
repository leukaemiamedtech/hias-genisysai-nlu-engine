############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         Extensions Class
# Description:   Handles response extensions.
# License:       MIT License
# Last Modified: 2020-10-01
#
############################################################################################

from Classes.Helpers import Helpers

class Extensions():
	""" Extensions Class

	Handles response extensions.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("Extensions")

		self.Helpers.logger.info("Extensions class initialized.")

	def setExtension(self, intent):
		""" Sets and returns the extension path and responses. """

		extensionResponses = []
		extension = None
		entities  = False

		extension = intent["extension"]["function"] if intent["extension"]["function"] !="" else None

		if extension != None:
			extensionResponses = intent["extension"]["responses"]
			entities = intent["extension"]["entities"]

		return extension, extensionResponses, entities