############################################################################################
#
# Repository:    GeniSysAI
# Project:       Natural Language Understanding Engine
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
#
# Title:         iotJumpWay Class
# Description:   iotJumpWay connectivity class.
# License:       MIT License
# Last Modified: 2020-09-01
#
############################################################################################

import inspect, json, os

import paho.mqtt.client as mqtt

from Classes.Helpers import Helpers

class Device():
	""" iotJumpWay Class

	iotJumpWay connectivity class.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("iotJumpWay")

		self.Helpers.logger.info("Initiating Local iotJumpWay Device.")

		self.mqttClient = None
		self.mqttTLS = "/etc/ssl/certs/DST_Root_CA_X3.pem"
		self.mqttHost = self.Helpers.confs["iotJumpWay"]['host']
		self.mqttPort = self.Helpers.confs["iotJumpWay"]['port']

		self.commandsCallback = None

		self.Helpers.logger.info("JumpWayMQTT Device Initiated.")

	def connect(self):
		""" Connects to the iotJumpWay. """

		self.Helpers.logger.info("Initiating Local iotJumpWay Device Connection.")

		self.mqttClient = mqtt.Client(client_id = self.Helpers.confs["iotJumpWay"]['dn'], clean_session = True)
		deviceStatusTopic = '%s/Device/%s/%s/Status' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'])
		self.mqttClient.will_set(deviceStatusTopic, "OFFLINE", 0, False)
		self.mqttClient.tls_set(self.mqttTLS, certfile=None, keyfile=None)
		self.mqttClient.on_connect = self.on_connect
		self.mqttClient.on_message = self.on_message
		self.mqttClient.on_publish = self.on_publish
		self.mqttClient.on_subscribe = self.on_subscribe
		self.mqttClient.username_pw_set(str(self.Helpers.confs["iotJumpWay"]['un']), str(self.Helpers.confs["iotJumpWay"]['pw']))
		self.mqttClient.connect(self.mqttHost, self.mqttPort, 10)
		self.mqttClient.loop_start()

		self.Helpers.logger.info("Local iotJumpWay Device Connection Initiated.")

	def on_connect(self, client, obj, flags, rc):
		""" Manages on connection event. """

		self.Helpers.logger.info("Local iotJumpWay Device Connection Successful.")
		self.Helpers.logger.info("rc: " + str(rc))

		self.statusPub("ONLINE")

	def on_subscribe(self, client, obj, mid, granted_qos):
		""" Manages on subscription event. """

		self.Helpers.logger.info("JumpWayMQTT Subscription: "+str(mid))

	def on_message(self, client, obj, msg):
		""" Manages on message event. """

		print("JumpWayMQTT Message Received")
		splitTopic=msg.topic.split("/")

		if splitTopic[1]=='Devices':
			if splitTopic[4]=='Commands':
				if self.commandsCallback == None:
					print("** Device Commands Callback Required (commandsCallback)")
				else:
					self.commandsCallback(msg.topic, msg.payload)
			elif splitTopic[4]=='Triggers':
				if self.triggersCallback == None:
					print("** Device Notifications Callback Required (deviceNotificationsCallback)")
				else:
					self.triggersCallback(msg.topic, msg.payload)

	def statusPub(self, data):
		""" Publishes a status. """

		deviceStatusTopic = '%s/Devices/%s/%s/Status' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'])
		self.mqttClient.publish(deviceStatusTopic, data)
		self.Helpers.logger.info("Published to Device Status " + deviceStatusTopic)

	def channelPub(self, channel, data):
		""" Publishes to a device channel. """

		deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'], channel)
		self.mqttClient.publish(deviceChannel, json.dumps(data))

	def channelSub(self, channel, qos=0):
		""" Subscribes to a device channel. """

		if channel == None:
			self.Helpers.logger.info("** Channel (channel) is required!")
			return False
		else:
			deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'], channel)
			self.mqttClient.subscribe(deviceChannel, qos=qos)
			self.Helpers.logger.info("-- Subscribed to Device "+channel+" Channel")

	def on_publish(self, client, obj, mid):
		""" Manages on publish event. """

		self.Helpers.logger.info("-- Published to Device channel")

	def on_log(self, client, obj, level, string):
		""" Manages on log event. """

		print(string)

	def disconnect(self):
		""" Disconnects from iotJumpWay. """

		self.statusPub("OFFLINE")
		self.mqttClient.disconnect()
		self.mqttClient.loop_stop()