
############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         gTime Extension Class
# Description:   Responds to time requests.
# License:       MIT License
# Last Modified: 2020-08-19
#
############################################################################################

import os
import time
import json
import random

from datetime import datetime

class gTime():
	""" gTime Extension Class

	Responds to time requests.
	"""

	def __init__(self):
		""" Initializes the class. """
		pass

	def getTime(self, responses, entities):
		""" Updates current time in random response. """

		return random.choice(responses).replace("%%TIME%%", time.strftime("%c"))
