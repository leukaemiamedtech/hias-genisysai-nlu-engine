######################################################################################################
#
# Organization:  Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         TTS Class
# Description:   Text To Speech helper functions.
# License:       MIT License
# Last Modified: 2020-10-01
#
######################################################################################################

import os
import time

from gtts import gTTS
from random import randint

from Classes.Helpers import Helpers

class TTS():
	""" TTS Class

	Text To Speech helper functionse.
	"""

	def __init__(self):

		self.Helpers = Helpers("TTS")

		self.Helpers.logger.info("TTS class initialized.")

	def speak(self, toSpeak):

		ttsAPI = gTTS(toSpeak, lang = "en-us")
		ttsFile = str(randint(0, 100000)) + "_temp.mp3"
		ttsAPI.save(ttsFile)
		os.system(" mpg123 " + ttsFile)
		os.system("rm %s" % (ttsFile))
