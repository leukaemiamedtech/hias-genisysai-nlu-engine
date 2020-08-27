############################################################################################
#
# Repository:    GeniSysAI
# Project:       NCS1 USB Camera Security System
#
# Author:        Adam Milton-Barker (AdamMiltonBarker.com)
# Contributors:
# Title:         iotJumpWay Class
# Description:   iotJumpWay helper functions.
# License:       MIT License
# Last Modified: 2020-08-21
#
############################################################################################

import os, json, sys, time

import paho.mqtt.client as mqtt

from Classes.Helpers import Helpers

class Application():
	""" iotJumpWay Class

	iotJumpWay helper functions.
	"""

	def __init__(self):
		""" Initializes the class. """

		self.Helpers = Helpers("iotJumpWay")

		self.Helpers.logger.info("Initiating Local iotJumpWay Application.")

		self.mqttClient = None
		self.mqttTLS = "/etc/ssl/certs/DST_Root_CA_X3.pem"
		self.mqttHost = self.Helpers.confs["iotJumpWay"]['host']
		self.mqttPort = self.Helpers.confs["iotJumpWay"]['port']

		self.appCommandsCallback = None
		self.appSensorCallback = None
		self.appStatusCallback = None
		self.appTriggerCallback = None
		self.commandsCallback = None
		self.deviceSensorCallback = None
		self.deviceStatusCallback = None
		self.deviceTriggerCallback = None

		self.Helpers.logger.info("iotJumpWay Application Initiated.")

	def appConnect(self):

		self.Helpers.logger.info("Initiating Local iotJumpWay Application Connection.")

		self.mqttClient = mqtt.Client(client_id = self.Helpers.confs["iotJumpWay"]['an'], clean_session = True)
		applicationStatusTopic = '%s/Applications/%s/Status' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['aid'])
		self.mqttClient.will_set(applicationStatusTopic, "OFFLINE", 0, False)
		self.mqttClient.tls_set(self.mqttTLS, certfile=None, keyfile=None)
		self.mqttClient.on_connect = self.on_connect
		self.mqttClient.on_message = self.on_message
		self.mqttClient.on_publish = self.on_publish
		self.mqttClient.on_subscribe = self.on_subscribe
		self.mqttClient.username_pw_set(str(self.Helpers.confs["iotJumpWay"]['un']), str(self.Helpers.confs["iotJumpWay"]['pw']))
		self.mqttClient.connect(self.mqttHost, self.mqttPort, 10)
		self.mqttClient.loop_start()

		self.Helpers.logger.info("Local iotJumpWay Application Connection Initiated.")

	def on_connect(self, client, obj, flags, rc):

		self.Helpers.logger.info("Local iotJumpWay Application Connection Successful.")
		self.Helpers.logger.info("rc: " + str(rc))

		self.appStatusPub("ONLINE")

	def appStatusPub(self, data):

		deviceStatusTopic = '%s/Applications/%s/Status' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['aid'])
		self.mqttClient.publish(deviceStatusTopic, data)
		self.Helpers.logger.info("Published to Application Status " + deviceStatusTopic)

	def on_subscribe(self, client, obj, mid, granted_qos):

		self.Helpers.logger.info("iotJumpWay Subscription: "+str(self.Helpers.confs["iotJumpWay"]['an']))

	def on_message(self, client, obj, msg):

		print("JumpWayMQTT Message Received")
		splitTopic=msg.topic.split("/")

		if splitTopic[1]=='Applications':
			if splitTopic[3]=='Status':
				if self.appStatusCallback == None:
					print("** Application Status Callback Required (appStatusCallback)")
				else:
					self.appStatusCallback(msg.topic,msg.payload)
			elif splitTopic[3]=='Command':
				if self.cameraCallback == None:
					print("** Application Camera Callback Required (cameraCallback)")
				else:
					self.cameraCallback(msg.topic,msg.payload)
		elif splitTopic[1]=='Devices':
			if splitTopic[4]=='Status':
				if self.deviceStatusCallback == None:
					print("** Device Status Callback Required (deviceStatusCallback)")
				else:
					self.deviceStatusCallback(msg.topic,msg.payload)
			elif splitTopic[4]=='Sensors':
				if self.deviceSensorCallback == None:
					print("** Device Sensors Callback Required (deviceSensorCallback)")
				else:
					self.deviceSensorCallback(msg.topic,msg.payload)
			elif splitTopic[4]=='Actuators':
				if self.deviceActuatorCallback == None:
					print("** Device Actuator Callback Required (deviceActuatorCallback)")
				else:
					self.deviceActuatorCallback(msg.topic,msg.payload)
			elif splitTopic[4]=='Commands':
				if self.commandsCallback == None:
					print("** Device Commands Callback Required (commandsCallback)")
				else:
					self.commandsCallback(msg.topic,msg.payload)
			elif splitTopic[4]=='Notifications':
				if self.deviceNotificationsCallback == None:
					print("** Device Notifications Callback Required (deviceNotificationsCallback)")
				else:
					self.deviceNotificationsCallback(msg.topic,msg.payload)
			elif splitTopic[4]=='Camera':
				if self.cameraCallback == None:
					print("** Device Camera Callback Required (cameraCallback)")
				else:
					self.cameraCallback(msg.topic,msg.payload)

	def appChannelPub(self, channel, application, data):

		applicationChannel = '%s/Applications/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], application, channel)
		self.mqttClient.publish(applicationChannel,json.dumps(data))
		print("Published to Application "+channel+" Channel")

	def appChannelSub(self, application, channelID, qos=0):

		if application == "#":
			applicationChannel = '%s/Applications/#' % (self.Helpers.confs["iotJumpWay"]['lid'])
			self.mqttClient.subscribe(applicationChannel, qos=qos)
			self.Helpers.logger.info("-- Subscribed to all Application Channels")
			return True
		else:
			applicationChannel = '%s/Applications/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], application, channelID)
			self.mqttClient.subscribe(applicationChannel, qos=qos)
			self.Helpers.logger.info("-- Subscribed to Application " + channelID + " Channel")
			return True

	def appDeviceChannelPub(self, channel, zone, device, data):

		deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], zone, device, channel)
		self.mqttClient.publish(deviceChannel, json.dumps(data))
		self.Helpers.logger.info("-- Published to Device "+channel+" Channel")

	def appDeviceChannelSub(self, zone, device, channel, qos=0):

		if zone == None:
			print("** Zone ID (zoneID) is required!")
			return False
		elif device == None:
			print("** Device ID (device) is required!")
			return False
		elif channel == None:
			print("** Channel ID (channel) is required!")
			return False
		else:
			if device == "#":
				deviceChannel = '%s/Devices/#' % (self.Helpers.confs["iotJumpWay"]['lid'])
				self.mqttClient.subscribe(deviceChannel, qos=qos)
				self.Helpers.logger.info("-- Subscribed to all devices")
			else:
				deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], zone, device, channel)
				self.mqttClient.subscribe(deviceChannel, qos=qos)
				self.Helpers.logger.info("-- Subscribed to Device "+channel+" Channel")

			return True

	def on_publish(self, client, obj, mid):

			print("-- Published: "+str(obj))

	def on_log(self, client, obj, level, string):

			print(string)

	def appDisconnect(self):
		self.appStatusPub("OFFLINE")
		self.mqttClient.disconnect()
		self.mqttClient.loop_stop()

class Device():
	""" iotJumpWay Class

	The iotJumpWay Class provides the EMAR device with  it's IoT functionality.
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

		self.Helpers.logger.info("Local iotJumpWay Device Connection Successful.")
		self.Helpers.logger.info("rc: " + str(rc))

		self.statusPub("ONLINE")

	def on_subscribe(self, client, obj, mid, granted_qos):

		self.Helpers.logger.info("JumpWayMQTT Subscription: "+str(mid))

	def on_message(self, client, obj, msg):

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

		deviceStatusTopic = '%s/Devices/%s/%s/Status' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'])
		self.mqttClient.publish(deviceStatusTopic, data)
		self.Helpers.logger.info("Published to Device Status " + deviceStatusTopic)

	def channelPub(self, channel, data):

		deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'], channel)
		self.mqttClient.publish(deviceChannel, json.dumps(data))

	def channelSub(self, channel, qos=0):

		if channel == None:
			self.Helpers.logger.info("** Channel (channel) is required!")
			return False
		else:
			deviceChannel = '%s/Devices/%s/%s/%s' % (self.Helpers.confs["iotJumpWay"]['lid'], self.Helpers.confs["iotJumpWay"]['zid'], self.Helpers.confs["iotJumpWay"]['did'], channel)
			self.mqttClient.subscribe(deviceChannel, qos=qos)
			self.Helpers.logger.info("-- Subscribed to Device "+channel+" Channel")

	def on_publish(self, client, obj, mid):

		self.Helpers.logger.info("-- Published to Device channel")

	def on_log(self, client, obj, level, string):

			print(string)

	def disconnect(self):
		self.statusPub("OFFLINE")
		self.mqttClient.disconnect()
		self.mqttClient.loop_stop()
