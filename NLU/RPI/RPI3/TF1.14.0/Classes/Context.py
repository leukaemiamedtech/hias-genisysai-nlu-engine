############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         Context Class
# Description:   Handles conversation context.
# License:       MIT License
# Last Modified: 2020-09-01
#
############################################################################################

from Classes.Helpers import Helpers

class Context():
	""" Context Class

	Handles conversation context..
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("Context")

		self.Helpers.logger.info("Context class initialized.")

	def setContexts(self, theIntent, session):
		""" Sets all contexts. """

		contextIn  = self.setContextIn(theIntent)
		contextOut = self.setContextOut(theIntent)
		context	= self.getCurrentContext(session)

		return contextIn, contextOut, context

	def setContextIn(self, intent):
		""" Sets the current context in. """

		return intent["context"]["in"] if intent["context"]["in"] != "" else ""

	def setContextOut(self, intent):
		""" Sets the current context out. """

		return intent["context"]["out"] if intent["context"]["out"] != "" else ""

	def checkSessionContext(self, session, intent):
		""" Checks the current context session. """

		if("context" in session and intent["context"]["in"] == session["context"]):
			return True
		else:
			return False

	def checkClearContext(self, intent, override=0):
		""" Checks if we are to clear the current context. """

		return True if intent["context"]["clear"] == True or override == 1 else False

	def getCurrentContext(self, session):
		""" Gets the current context. """

		return session["context"] if "context" in session else "NA"