######################################################################################################
#
# Organization:  Asociacion De Investigacion En Inteligencia Artificial Para La Leucemia Peter Moss
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         NLU Client Class
# Description:   Sends requests to the NLU Engine server.
# License:       MIT License
# Last Modified: 2020-10-01
#
######################################################################################################

import sys, time, string, requests, json

from Classes.Helpers  import Helpers


class Client():
	""" NLU Client Class

	Sends requests to the NLU Engine server.
	"""

	def __init__(self, apath):
		""" Initializes the class. """

		self.Helpers = Helpers("Client")
		self.path = apath

		self.apiUrl = "http://" + self.Helpers.confs["System"]["IP"] + ":" + str(
			self.Helpers.confs["System"]["Port"]) + "/" + self.path
		self.headers = {"content-type": 'application/json'}

		self.Helpers.logger.info("Client ready")

if __name__ == "__main__":

	Client = Client(sys.argv[1])

	data   = {"query": str(sys.argv[2])}

	Client.Helpers.logger.info("Sending string for classification...")

	response = requests.post(Client.apiUrl, data=json.dumps(data),
								headers=Client.headers)

	Client.Helpers.logger.info("Response: "+str(response.text))
